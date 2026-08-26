#!/usr/bin/env python3
"""Draw mods/<Author>@<id>/thumbnail.png: one square icon per mod in the index.

Every icon is pixel art on a 32x32 grid, scaled 16x to 512x512 with no
resampling -- one drawn pixel is a clean 16x16 block -- and finished with the
same faint scanlines, vignette and colour glow the cards elsewhere in the
index use.  Nothing is loaded from disk and no font is involved, so a rebuild
on any machine produces byte-identical files.

    python3 tools/make_icons.py            # redraw every icon
    python3 tools/make_icons.py gen1arena  # ... or just the ones named

Add a mod by writing one more draw function and listing it in ICONS against
that mod's id.  A folder with no icon is named on the way out, and makes the
run exit non-zero, so an entry cannot quietly go without one.
"""

import json
import math
import pathlib
import struct
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODS = ROOT / "mods"

GRID = 32          # the drawing grid, in pixels
SCALE = 16         # how many image pixels one drawn pixel becomes
SIZE = GRID * SCALE

# The index's own palette: site/index.html's dark card colours, the Game Boy
# green it uses for links, and the red and bone white of a Poke Ball.
BG      = (0x0b, 0x0d, 0x0c)
INK     = (0x22, 0x2a, 0x21)   # pixel-art outline
PANEL   = (0x16, 0x1c, 0x17)
EDGE    = (0x1e, 0x24, 0x1d)
GREEN   = (0x9b, 0xbc, 0x0f)   # Game Boy green
GREEN_D = (0x63, 0x7a, 0x0c)
RED     = (0xd0, 0x41, 0x3a)
WHITE   = (0xf2, 0xf5, 0xf0)
MUTED   = (0x8b, 0x97, 0x8f)
STEEL   = (0x5a, 0x66, 0x5c)
AMBER   = (0xe8, 0xb7, 0x3a)
PINK    = (0xf2, 0x8c, 0xbc)
PINK_D  = (0xa8, 0x46, 0x78)
PURPLE  = (0x9a, 0x6c, 0xf0)   # Gen1BattleUI's glove
PURPLE_L = (0xc4, 0xa6, 0xff)
PURPLE_D = (0x5c, 0x36, 0xa4)


class Art:
    """A GRID x GRID grid of colours, drawn on with whole-pixel primitives."""

    def __init__(self, bg=BG):
        self.g = [[bg] * GRID for _ in range(GRID)]

    def px(self, x, y, c):
        if 0 <= x < GRID and 0 <= y < GRID:
            self.g[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.px(x, y, c)

    def frame(self, x0, y0, x1, y1, c):
        for x in range(int(x0), int(x1) + 1):
            self.px(x, int(y0), c)
            self.px(x, int(y1), c)
        for y in range(int(y0), int(y1) + 1):
            self.px(int(x0), y, c)
            self.px(int(x1), y, c)

    def ellipse(self, cx, cy, rx, ry, c, rows=None):
        for y in range(GRID):
            if rows and not (rows[0] <= y <= rows[1]):
                continue
            for x in range(GRID):
                if ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1:
                    self.px(x, y, c)

    def disc(self, cx, cy, r, c, rows=None):
        self.ellipse(cx, cy, r, r, c, rows)

    def arc(self, cx, cy, r_in, r_out, a0, a1, c):
        """A ring segment, angles in degrees counter-clockwise from east."""
        for y in range(GRID):
            for x in range(GRID):
                dx, dy = x + .5 - cx, y + .5 - cy
                if not r_in <= math.hypot(dx, dy) <= r_out:
                    continue
                a = math.degrees(math.atan2(-dy, dx)) % 360
                if (a0 <= a <= a1) if a0 <= a1 else (a >= a0 or a <= a1):
                    self.px(x, y, c)

    def poly(self, pts, c):
        for y in range(GRID):
            py = y + .5
            xs = []
            for i in range(len(pts)):
                (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
                if (y1 <= py < y2) or (y2 <= py < y1):
                    xs.append(x1 + (py - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(GRID):
                    if xs[i] <= x + .5 <= xs[i + 1]:
                        self.px(x, y, c)


def polar(cx, cy, a, r):
    return cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a))


def ball(art, cx, cy, r, ink=INK):
    """A Poke Ball: red over bone white, banded, and buttoned if it is big
    enough for a button to be more than a smudge."""
    band = max(1.0, r * .17)
    art.disc(cx, cy, r, ink)
    art.disc(cx, cy, r - max(1.0, r * .16), RED, rows=(0, int(cy - band)))
    art.disc(cx, cy, r - max(1.0, r * .16), WHITE, rows=(int(cy + band), GRID))
    if r >= 4:
        art.disc(cx, cy, r * .36, ink)
        art.disc(cx, cy, r * .22, WHITE)


def arrow(art, x, y, size, facing, c):
    """A stepped pixel arrow with its tip at (x, y): crisper at this size
    than a filled triangle, which frays into a blob below about ten pixels."""
    for i in range(size):
        span = size - 1 - i
        if facing == "right":
            art.rect(x + i, y - span, x + i, y + span, c)
        elif facing == "up":
            art.rect(x - i, y + i, x + i, y + i, c)
        else:
            art.rect(x - i, y - i, x + i, y - i, c)


def stamp(art, x, y, rows, key):
    """Draw a little sprite written out as text, one character per pixel."""
    for j, line in enumerate(rows):
        for i, ch in enumerate(line):
            if ch in key:
                art.px(x + i, y + j, key[ch])


def numerals(art, x, y, text, colour, shadow):
    """Write a row of digits, each sitting on a shadow a pixel down and right.

    Seven by nine is the biggest a three-digit row goes on a 32-pixel grid
    and still leaves two of them room to sit either side of a rule.  The
    shadow is what gives the strokes an edge: a flat colour on the near-black
    ground reads as a stencil rather than as something drawn.
    """
    for ch in text:
        rows = DIGITS[ch]
        stamp(art, x + 1, y + 1, rows, {"#": shadow})
        stamp(art, x, y, rows, {"#": colour})
        x += len(rows[0]) + DIGIT_GAP


# The two digits 151 needs, seven wide and nine tall, with a gap between
# them.  Only 1 and 5 are here because only 1 and 5 are ever drawn -- a full
# set of ten would be nine glyphs of dead weight and one more thing to keep
# in step with nothing.
DIGIT_GAP = 2
DIGITS = {
    "1": [
        "..####.",
        ".#####.",
        "....##.",
        "....##.",
        "....##.",
        "....##.",
        "....##.",
        ".######",
        ".######",
    ],
    "5": [
        "#######",
        "#######",
        "##.....",
        "######.",
        "#######",
        ".....##",
        "##...##",
        "#######",
        ".#####.",
    ],
}


# The five letters QOL and UI need, on the same seven-by-nine body the
# digits use so a word and a number sit at the same weight.  Only these five
# are here, for the same reason only 1 and 5 are: a full alphabet would be
# twenty-one glyphs of dead weight and one more thing to keep in step with
# nothing.
LETTERS = {
    "Q": [
        ".#####.",
        "##...##",
        "##...##",
        "##...##",
        "##...##",
        "##.#.##",
        "##..###",
        ".######",
        ".....##",
    ],
    "O": [
        ".#####.",
        "##...##",
        "##...##",
        "##...##",
        "##...##",
        "##...##",
        "##...##",
        ".#####.",
        ".......",
    ],
    "L": [
        "##.....",
        "##.....",
        "##.....",
        "##.....",
        "##.....",
        "##.....",
        "##.....",
        "#######",
        ".......",
    ],
    "U": [
        "##...##",
        "##...##",
        "##...##",
        "##...##",
        "##...##",
        "##...##",
        "##...##",
        ".#####.",
        ".......",
    ],
    "I": [
        "#######",
        "..###..",
        "..###..",
        "..###..",
        "..###..",
        "..###..",
        "..###..",
        "#######",
        ".......",
    ],
}


# The same five letters again, five by seven, for when they have to fit on a
# screen rather than fill a frame.  QOL at the full seven-by-nine body is
# twenty-five pixels wide, which on a 32-pixel grid leaves nothing for the
# Game Boy around it -- the console would have to be wider than the icon.
LETTERS_SMALL = {
    "Q": [
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        ".###.",
        "....#",
    ],
    "O": [
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
        ".....",
    ],
    "L": [
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#####",
        ".....",
    ],
    "U": [
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
        ".....",
    ],
    "I": [
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "#####",
        ".....",
    ],
}


def word(art, x, y, text, colour, shadow, outline=None,
         glyphs=LETTERS, gap=DIGIT_GAP):
    """Write a word, each glyph sitting on a shadow a pixel down and right.

    The same stencil trick numerals() uses: a flat colour reads as something
    printed rather than something drawn, and the offset shadow is what gives
    the strokes an edge.  Returns the width laid down, so a caller can centre
    the word without counting glyphs itself.

    `outline` traces each glyph a pixel out in all eight directions first.
    On the near-black ground the rest of the index uses it is unnecessary --
    the shadow alone separates the strokes.  Over grass it is not: gold on
    green is two mid tones, and without a dark edge between them the word
    dissolves into the tufts at any size below the full 512.

    Glyphs are outlined one at a time, which is only safe because the gap is
    wider than the trace: at gap 2 a glyph's outline reaches one pixel past
    its body and the next begins two past, so no outline lands on a
    neighbour's fill.
    """
    start = x
    for ch in text:
        rows = glyphs[ch]
        if outline:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx or dy:
                        stamp(art, x + dx, y + dy, rows, {"#": outline})
        stamp(art, x + 1, y + 1, rows, {"#": shadow})
        stamp(art, x, y, rows, {"#": colour})
        x += len(rows[0]) + gap
    return x - gap - start


def word_width(text, glyphs=LETTERS, gap=DIGIT_GAP):
    return sum(len(glyphs[c][0]) for c in text) + gap * (len(text) - 1)

# A Poke Ball small enough that drawing it as circles would only smear: at
# eleven pixels across it is worth spelling out.
SMALL_BALL = [
    "...#####...",
    "..#RRRRR#..",
    ".#RRRRRRR#.",
    "#RRRRRRRRR#",
    "#RRR###RRR#",
    "#####O#####",
    "#WWW###WWW#",
    "#WWWWWWWWW#",
    ".#WWWWWWW#.",
    "..#WWWWW#..",
    "...#####...",
]

# One party member, walking behind you.
FOLLOWER = [
    ".#...#.",
    ".##.##.",
    ".#####.",
    "#o###o#",
    "#######",
    ".#####.",
    ".#...#.",
]

# You, from behind, mid-stride: cap, hair under it, and the boots below.
TRAINER = [
    "...#####...",
    "..#RRRRR#..",
    ".#RRRRRRR#.",
    "#RRRRRRRRR#",
    "#RRRRRRRRR#",
    "#HHHHHHHHH#",
    ".#HHHHHHH#.",
    "..#SSSSS#..",
    ".#DSSSSSD#.",
    ".#DSSSSSD#.",
    "..#SSSSS#..",
    "..#PPPPP#..",
    "..#P#.#P#..",
]

# The one following you: ears up, cheeks lit, a step behind.
PARTY_MON = [
    "..##...##..",
    "..#Y...Y#..",
    ".#YY...YY#.",
    ".#YY###YY#.",
    "#YYYYYYYYY#",
    "#Y#YYYYY#Y#",
    "#oYYYYYYYo#",
    ".#YY###YY#.",
    "..#YYYYY#..",
    "...#...#...",
]


# --------------------------------------------------------------------------
# the icons

def autosave():
    """A Poke Ball inside the loop that keeps writing it out."""
    a = Art()
    cx = cy = 16.0
    for a0, a1 in ((32, 148), (212, 328)):
        a.arc(cx, cy, 12.4, 14.0, a0, a1, GREEN_D)
        a.arc(cx, cy, 12.4, 14.0, a0 + 12, a1, GREEN)
        head = a1 if a0 == 32 else a1          # arrowhead at the arc's end
        a.poly([polar(cx, cy, head + 13, 13.2),
                polar(cx, cy, head - 3, 10.2),
                polar(cx, cy, head - 3, 16.2)], GREEN)
    ball(a, cx, cy, 10.0)
    return a, GREEN


def auto_continue():
    """Skip to the end of the boot: two arrows and the bar they run into."""
    a = Art()
    a.poly([(3, 5.5), (3, 26.5), (13.5, 16)], GREEN_D)
    a.poly([(14, 4), (14, 28), (27, 16)], BG)
    a.poly([(15, 5.5), (15, 26.5), (25.5, 16)], GREEN)
    a.rect(26.5, 6, 28.5, 25, WHITE)
    return a, GREEN


def arena():
    """A backdrop with something behind the battle, and a platform on it."""
    a = Art(BG)
    a.rect(3, 3, 28, 28, PANEL)
    sky = [(0x2a, 0x22, 0x3e), (0x3a, 0x2c, 0x4c), (0x4e, 0x35, 0x50),
           (0x6b, 0x3d, 0x4c), (0x8e, 0x4a, 0x42)]
    for i, c in enumerate(sky):
        a.rect(4, 4 + i * 3, 27, 6 + i * 3, c)
    a.disc(21.5, 12.5, 3.2, AMBER)                       # low sun
    a.poly([(4, 19), (11, 9.5), (19, 19)], (0x1c, 0x24, 0x1e))
    a.poly([(14, 19), (23, 12), (28, 19)], (0x15, 0x1c, 0x18))
    a.rect(4, 19, 27, 27, (0x25, 0x2e, 0x20))
    a.rect(4, 24, 27, 27, (0x1a, 0x21, 0x18))
    a.ellipse(16, 23.4, 8.5, 2.8, (0x33, 0x40, 0x1f))    # battle platform,
    a.ellipse(16, 22.9, 7.4, 2.0, (0x50, 0x62, 0x2c))    # lit from the front
    a.frame(3, 3, 28, 28, EDGE)
    return a, (0xa0, 0x5a, 0x50)


def menu_manager():
    """A menu with one row picked up and moving."""
    a = Art()
    a.rect(4, 3, 27, 28, PANEL)
    a.frame(4, 3, 27, 28, MUTED)
    for i, top in enumerate((6, 11, 16, 21)):
        a.rect(10, top, 18, top + 2, GREEN if i == 1 else STEEL)
    arrow(a, 6, 12, 3, "right", WHITE)                     # the menu cursor
    arrow(a, 22, 9, 3, "up", MUTED)                        # ... and the row
    arrow(a, 22, 16, 3, "down", MUTED)                     # it is moving
    return a, GREEN


def gen1_follower():
    """The thing the mod is: a party member walking the route behind you."""
    a = Art()
    grass = (0x24, 0x33, 0x18)
    grass_l = (0x33, 0x46, 0x1e)
    grass_d = (0x18, 0x24, 0x14)
    dirt = (0x6a, 0x52, 0x30)
    dirt_d = (0x46, 0x36, 0x1f)

    a.rect(0, 0, 31, 31, grass)                     # the route, seen from
    a.rect(4, 0, 27, 31, dirt_d)                    # above: a path, with
    a.rect(5, 0, 26, 31, dirt)                      # grass either side of it
    for cx, cy in ((1.5, 4), (30, 11), (2, 20), (29.5, 27), (1, 30)):
        a.disc(cx, cy, 2.4, grass_d)                # hedges off the path
    for x, y in ((2, 12), (29, 3), (1, 26), (30, 19)):
        a.px(x, y, grass_l)
    for x, y in ((6, 7), (25, 14), (7, 23), (24, 29), (6, 30), (25, 2)):
        a.px(x, y, dirt_d)                          # trodden dirt

    a.ellipse(15.5, 16, 4.6, 1.3, dirt_d)           # both cast a shadow onto
    a.ellipse(15.5, 29.5, 4.4, 1.3, dirt_d)         # the path they stand on
    stamp(a, 10, 2, TRAINER, {"#": INK, "R": RED, "H": (0x6b, 0x47, 0x2a),
                              "S": (0xe6, 0xe9, 0xe4), "D": (0xa8, 0xb0, 0xa5),
                              "P": (0x2f, 0x3a, 0x4d)})
    a.rect(8, 26, 10, 27, AMBER)                    # the follower's tail,
    a.rect(6, 24, 9, 25, AMBER)                     # trailing behind it
    a.px(7, 27, INK)
    a.px(8, 28, INK)
    a.px(5, 24, INK)
    a.px(5, 25, INK)
    a.px(6, 23, INK)
    stamp(a, 10, 19, PARTY_MON, {"#": INK, "Y": AMBER, "o": RED})
    return a, GREEN


# Keyed by the mod's id rather than its folder, because an entry's folder
# carries its author and an author can change -- this one's has twice -- while
# the id is the thing the installer, mod-sync and the feed all key on and so
# cannot move without the mod itself moving.
def modern_bag():
    """The bag itself: flap, clasp, and a pocket down the side."""
    a = Art()
    hide = (0x8a, 0x5c, 0x33)
    hide_d = (0x55, 0x36, 0x1c)
    hide_l = (0xa8, 0x74, 0x44)
    a.arc(16, 13, 4.6, 6.2, 25, 155, hide_d)               # the handle
    a.rect(5, 13, 26, 28, hide)                            # body
    a.rect(5, 26, 26, 28, hide_d)
    for x, y in ((5, 13), (26, 13), (5, 28), (26, 28)):    # softened corners
        a.px(x, y, BG)
    a.rect(4, 12, 27, 19, hide_d)                          # flap over it
    a.rect(4, 12, 27, 13, hide_l)
    for x in (4, 27):
        a.px(x, 12, BG)
        a.px(x, 19, BG)
    a.rect(5, 18, 26, 18, GREEN)                           # piping
    a.rect(14, 17, 17, 22, AMBER)                          # the clasp
    a.rect(15, 19, 16, 20, hide_d)
    for x in (9, 20):                                      # straps, each
        a.rect(x, 21, x + 2, 27, hide_d)                   # through a keeper
        a.rect(x, 23, x + 2, 24, AMBER)
    return a, AMBER

def bills_box():
    """Pikachu coming up out of the box.

    The mod replaces a PC that only ever showed you a list of twenty names,
    so the icon shows the one thing that list never did: what is actually in
    the box.  He is drawn over the far flaps and under the near wall, which
    is what puts him inside the box rather than behind it.
    """
    a = Art()
    card = (0xb5, 0x86, 0x4e)                      # cardboard, lit from above
    card_d = (0x8a, 0x63, 0x36)
    card_l = (0xcf, 0xa2, 0x66)
    pika = AMBER
    pika_d = (0xc2, 0x8e, 0x22)

    # The two far flaps, folded back and away.  These are behind him.
    a.poly([(5, 18), (1, 12), (5, 9), (12, 16)], card_d)
    a.poly([(26, 18), (30, 12), (26, 9), (19, 16)], card_d)

    # An ear is three shapes over each other: the whole ear a shade darker,
    # the ear inside that, and the black tip inside that again.  The darker
    # one is doing the work -- a black tip against the dark behind it loses
    # its outline entirely without a rim to sit in.
    for outer, inner, tip in (
        ([(12.8, 11.6), (15.6, 9.6), (11.2, 0.0), (8.0, 1.5)],
         [(12.5, 10.7), (14.8, 9.2), (10.9, 1.0), (8.6, 2.1)],
         [(11.2, 0.0), (8.0, 1.5), (10.1, 6.0), (13.3, 4.5)]),
        ([(19.2, 11.6), (16.4, 9.6), (20.8, 0.0), (24.0, 1.5)],
         [(19.5, 10.7), (17.2, 9.2), (21.1, 1.0), (23.4, 2.1)],
         [(20.8, 0.0), (24.0, 1.5), (21.9, 6.0), (18.7, 4.5)]),
    ):
        a.poly(outer, pika_d)
        a.poly(inner, pika)
        a.poly(tip, INK)

    a.ellipse(16, 14.2, 6.8, 5.6, pika_d)          # the head, on its own rim
    a.ellipse(16, 13.6, 6.6, 5.4, pika)
    a.disc(10.8, 16.0, 2.0, RED)                   # cheeks
    a.disc(21.2, 16.0, 2.0, RED)
    for ex, gx in ((12.8, 12), (19.2, 19)):        # eyes, with a glint each
        a.disc(ex, 12.2, 1.7, INK)
        a.px(gx, 11, WHITE)
    a.px(16, 14, INK)                              # nose, over the two lips
    a.rect(14, 16, 15, 16, INK)                    # and the mouth they open
    a.rect(17, 16, 18, 16, INK)
    a.rect(15, 17, 17, 17, INK)

    # The near wall, drawn over him: below this line he is in the box.
    a.rect(3, 18, 28, 29, card)
    a.rect(3, 18, 28, 19, card_l)                  # the rim, catching light
    a.rect(3, 27, 28, 29, card_d)                  # and the shadowed foot
    a.rect(15, 20, 16, 26, card_d)                 # the seam down the front
    a.frame(3, 18, 28, 29, card_d)

    # Both paws over the rim, holding himself up on it.
    for x in (6, 22):
        a.rect(x, 16, x + 3, 19, pika)
        a.rect(x, 19, x + 3, 19, pika_d)
        a.px(x + 1, 16, pika_d)
        a.px(x + 2, 16, pika_d)

    # The two near flaps, folded down over the front corners.
    a.poly([(3, 18), (3, 25), (7, 22), (7, 18)], card_l)
    a.poly([(28, 18), (28, 25), (24, 22), (24, 18)], card_l)
    return a, AMBER


def sound_qol():
    """Two notes under one beam.

    One beam and not two: a sixteenth's second beam closes the gap between
    the stems and the pair stops reading as notes at all, which at 32 pixels
    is the whole difference between a tune and a green rectangle.
    """
    a = Art()
    # Each head sits on a darker rim: a green ellipse straight onto the
    # near-black ground has no edge, and the rim is what gives it one.
    for cx, cy in ((8.0, 25.0), (20.0, 22.0)):
        a.ellipse(cx, cy, 4.7, 3.8, GREEN_D)
        a.ellipse(cx, cy, 3.8, 2.9, GREEN)

    a.rect(11, 8, 12, 25, GREEN)                                 # the stems,
    a.rect(23, 5, 24, 22, GREEN)                                 # and the
    a.poly([(11, 7), (25, 4), (25, 7), (11, 10)], GREEN)         # beam over
    a.poly([(11, 10), (25, 7), (25, 8), (11, 11)], GREEN_D)      # them, edged
    return a, GREEN


def dex():
    """The Pokedex itself, open on the list this mod puts the icons in.

    The screen is the mod in one picture: three rows, each with a POKeMON
    beside it, the one you have seen in its own colours and the two you have
    not blacked back to silhouettes.  Every recess -- the lens, the lamps,
    the screen -- is rimmed in the shell's own shadow rather than in ink,
    because a black ring on red does not read as a seated part, it reads as
    a hole cut through the case.
    """
    a = Art()
    shell = RED
    shell_d = (0x8e, 0x2b, 0x27)
    shell_l = (0xe8, 0x5f, 0x53)
    screen = (0x0d, 0x14, 0x0e)
    seen_not = (0x2b, 0x38, 0x2c)      # a silhouette, still a shape
    lens = (0x34, 0x66, 0xa6)
    lens_l = (0x6f, 0x9d, 0xd6)
    plastic = (0x3b, 0x41, 0x3c)

    a.rect(3, 1, 28, 30, shell)                    # the case, lit from above
    a.rect(3, 1, 28, 2, shell_l)
    a.rect(3, 30, 28, 30, shell_d)
    for x in (3, 28):                              # softened corners
        a.px(x, 1, BG)
        a.px(x, 30, BG)
    a.frame(3, 1, 28, 30, INK)

    a.disc(8.5, 5.5, 4.0, shell_d)                 # the big lens, and the
    a.disc(8.5, 5.5, 3.2, lens)                    # light in the top of it
    a.disc(7.4, 4.4, 1.1, lens_l)
    for cx, c in ((15.0, AMBER), (19.0, GREEN), (23.0, WHITE)):
        a.disc(cx, 5, 1.9, shell_d)                # the three little lamps
        a.disc(cx, 5, 1.3, c)

    a.rect(4, 10, 27, 24, shell_d)                 # the screen, in its recess
    a.rect(5, 11, 26, 23, screen)
    for i, top in enumerate((12, 16, 20)):
        seen = i == 0
        a.rect(9, top, 12, top + 2, AMBER if seen else seen_not)
        a.rect(14, top, 24, top + 1, GREEN if seen else GREEN_D)
    arrow(a, 6, 13, 2, "right", WHITE)             # the list cursor

    a.rect(8, 25, 10, 29, plastic)                 # the pad,
    a.rect(6, 26, 12, 28, plastic)
    for cx, c in ((19.0, WHITE), (24.0, AMBER)):   # and the two buttons
        a.disc(cx, 27, 2.1, shell_d)
        a.disc(cx, 27, 1.4, c)
    return a, RED


def mod_menu():
    """A cog: the settings screen this mod redraws."""
    a = Art()
    cx = cy = 16.0

    # Eight trapezoid teeth rather than eight discs -- a rounded tooth reads
    # as a flower at 54px, which is the size the index card actually shows.
    # Drawn twice, INK a shade proud of GREEN, so the cog keeps the same
    # outline every other icon here has.
    def teeth(root, tip, half_root, half_tip, colour):
        for i in range(8):
            a0 = i * 45
            a.poly([polar(cx, cy, a0 - half_root, root),
                    polar(cx, cy, a0 - half_tip, tip),
                    polar(cx, cy, a0 + half_tip, tip),
                    polar(cx, cy, a0 + half_root, root)], colour)

    teeth(10.0, 14.8, 14, 9.5, INK)
    a.disc(cx, cy, 12.7, INK)
    teeth(9.5, 13.4, 11.5, 7.0, GREEN)
    a.disc(cx, cy, 11.4, GREEN)

    # the bore, dark rather than empty, so the cog stays legible on the dark
    # card as well as on the lighter strip
    a.disc(cx, cy, 5.6, INK)
    a.disc(cx, cy, 4.2, PANEL)
    return a, GREEN


def party():
    """The party screen, with every POKeMON in a colour of its own.

    The mod's whole argument in one picture.  Vanilla lays a single palette
    zone over the icon column -- all six members at once -- so a party comes
    out in one colour; here each row wears its own, and the HP bars are the
    three the game actually draws, green through yellow to red.

    Three rows rather than six because six at this size are six stripes: the
    point being made is that the rows DIFFER from each other, and three big
    enough to read carries that where six too small to read does not.

    The rows are seven pixels apart and each POKeMON is drawn no more than
    five tall, which is what keeps them three creatures rather than one
    column -- at six they touch, and touching reads as a single blob with
    colour bands across it.  The cursor sits in a lane of its own at the far
    left for the same reason: over the first POKeMON it looked like part of
    it rather than like something pointing at it.
    """
    a = Art()
    shell = (0x3b, 0x41, 0x3c)                     # the console around it
    shell_l = (0x50, 0x58, 0x51)
    shell_d = (0x2a, 0x2f, 0x2b)
    screen = (0x0d, 0x14, 0x0e)
    bar_bg = (0x2b, 0x38, 0x2c)

    a.rect(2, 2, 29, 29, shell)                    # the case, lit from above
    a.rect(2, 2, 29, 3, shell_l)
    a.rect(2, 28, 29, 29, shell_d)
    for x in (2, 29):                              # softened corners
        a.px(x, 2, BG)
        a.px(x, 29, BG)
    a.frame(2, 2, 29, 29, INK)

    a.rect(3, 5, 28, 27, shell_d)                  # the screen, in its recess
    a.rect(4, 6, 27, 26, screen)

    # Each row: the POKeMON in its own colour, its name, and its HP.  The
    # three bar colours are the game's own thresholds rather than a gradient
    # chosen here -- green, yellow, red is what the party menu shows.
    rows = (
        (7,  (0x8c, 0xc0, 0x4a), (0x5e, 0x86, 0x2c), GREEN, 11),  # full
        (14, (0xe0, 0xa8, 0x3c), (0x9c, 0x71, 0x22), AMBER, 7),   # about half
        (21, (0x5a, 0x8f, 0xd0), (0x38, 0x5f, 0x93), RED, 3),     # nearly out
    )
    for top, body, body_d, bar, fill in rows:
        a.ellipse(10, top + 2.5, 2.9, 2.6, body_d)     # the POKeMON, on a rim
        a.ellipse(10, top + 2.2, 2.6, 2.3, body)
        a.px(9, top + 2, INK)                          # two eyes, so it reads
        a.px(11, top + 2, INK)                         # as a creature, not a dot
        a.rect(15, top, 25, top + 1, MUTED)            # the name
        a.rect(15, top + 3, 25, top + 4, bar_bg)       # the HP bar, and its fill
        a.rect(15, top + 3, 14 + fill, top + 4, bar)

    arrow(a, 5, 9, 2, "right", WHITE)              # the cursor, in its own lane
    return a, GREEN


def gen151():
    """151 over 151: the dex finished, which is the whole mod in one number.

    Stacked as a fraction rather than written across in one line, because
    seven characters side by side on a 32-pixel grid leaves each of them
    three pixels wide -- at which point a 5 is a smudge and the number stops
    being a number.  Two rows of three over a rule reads at the 54 pixels the
    README table shows it at, which is the size that has to work.

    Pink is Mew's, and Mew is the last of the 151 in every sense: the one the
    cartridge never gave you, and the one this mod puts behind four journals
    in a basement.
    """
    a = Art()
    numerals(a, 3, 3, "151", PINK, PINK_D)
    a.rect(3, 16, 29, 17, PINK_D)                  # the rule, on its own
    a.rect(2, 15, 28, 16, PINK)                    # shadow like the digits
    numerals(a, 3, 20, "151", PINK, PINK_D)
    return a, PINK


def sprint():
    """A winged shoe: Hermes' talaria, in the running shoes' own red.

    Blocked out of a body, a collar and a round toe rather than traced as
    one outline.  A shoe in profile is mostly a silhouette problem, and an
    outline drawn at 32 pixels loses its toe to the scanline fill -- the
    front tapers to a sliver a pixel or two tall and stops reading as a
    shoe at all.  Blocking keeps the toe box the height it needs, and the
    sole is left to say which way is down.

    The feathers are quads with blunt, rounded tips, not triangles.  A
    triangle ends in a single pixel, and three of them fanned out read as
    scratches on the picture rather than as a wing.  They are laid down
    before the shoe and rooted behind the heel, so the wing emerges from
    something instead of being parked next to it, and they sweep back
    rather than over the toe -- which is how a wing is drawn on something
    already moving.
    """
    a = Art()

    BONE  = (0xe9, 0xec, 0xe4)
    QUILL = (0x8d, 0x97, 0x8f)
    SOLE  = (0xf2, 0xf5, 0xf0)
    DARK  = (0x8f, 0x2a, 0x26)
    LIT   = (0xe8, 0x6d, 0x62)

    # ------- the wing, laid down first so the shoe owns the overlap

    def feather(bx, by, tx, ty, wb, wt, c):
        dx, dy = tx - bx, ty - by
        n = math.hypot(dx, dy)
        nx, ny = -dy / n, dx / n
        a.poly([(bx + nx * wb, by + ny * wb), (tx + nx * wt, ty + ny * wt),
                (tx - nx * wt, ty - ny * wt), (bx - nx * wb, by - ny * wb)], c)
        a.disc(tx, ty, wt, c)                      # the blunt tip

    # Each feather gets its own root rather than all three sharing one: a
    # common root makes them one white mass for the first third of their
    # length, and a wing that has lost its feathers is a splash.  Drawn
    # back to front, each laying its own darker edge over the one behind,
    # which is what keeps them apart where they do overlap.
    for (bx, by), (tx, ty) in (((14.5, 17.0), (5.0, 3.5)),
                               ((13.5, 19.5), (1.5, 10.0)),
                               ((12.5, 21.5), (3.0, 17.0))):
        feather(bx, by, tx - .8, ty + .8, 3.2, 2.0, QUILL)
        feather(bx, by, tx, ty, 2.3, 1.2, BONE)

    # ------- the shoe, blocked out

    a.rect(9, 17, 24, 22, RED)                    # the body
    a.disc(23.5, 19.5, 3.2, RED)                  # a round toe box
    a.disc(11.0, 19.5, 3.0, RED)                  # and a round heel
    a.rect(9, 13, 16, 18, RED)                    # the ankle collar over both

    a.rect(9, 21, 23, 22, DARK)                   # the upper darkens into
    a.disc(23.5, 19.5, 3.2, DARK, rows=(21, 22))  # the sole, toe kept round

    a.rect(10, 14, 15, 16, LIT)                   # light off the collar
    a.ellipse(12.5, 13.6, 3.0, 1.7, BG)           # the opening, cut into it
    a.ellipse(12.5, 14.2, 2.2, 1.1, INK)

    # Three laces across the instep.  Two read as a mistake and four turn the
    # vamp into a grille, so three it is.
    for x in (17.4, 19.6, 21.8):
        a.poly([(x, 17.5), (x + 1.0, 17.5), (x + .3, 20.3), (x - .7, 20.3)],
               BONE)

    # ------- the sole, the one horizontal that says which way is down

    a.rect(7, 23, 27, 25, SOLE)
    a.disc(7.4, 24.0, 1.5, SOLE)
    a.disc(26.6, 24.0, 1.5, SOLE)
    a.rect(7, 26, 27, 26, QUILL)
    a.px(6, 25, QUILL); a.px(28, 25, QUILL)

    return a, RED


# --------------------------------------------------------------------------
# the two bundles
#
# These two are the suite rather than a mod in it, so they are drawn as the
# thing the suite is about: a word standing in tall grass, the way a wild
# Pokemon stands in it.  Everything else in the index is an object -- a shoe,
# a bag, a ball -- and that is the point of the difference.

# Two cases, one drawing. Each is four tones of the same hue -- lit, mid,
# shadow, and a near-black for the cut lines -- so the same code draws either
# by being handed a different four.
#
# The halves are told apart by colour and by nothing else, which is the point:
# they are the same console, and a reader scanning the index should be able to
# tell which is which without reading the screen.
GOLD    = (0xf5, 0xc9, 0x42)
GOLD_M  = (0xc9, 0x9c, 0x28)
GOLD_D  = (0x8a, 0x66, 0x12)
GOLD_K  = (0x4a, 0x35, 0x08)
CASE_GOLD = (GOLD, GOLD_M, GOLD_D, GOLD_K)

# Built out from the index's own RED rather than picked fresh, so the UI card
# sits in the same family as the Poke Ball on the icons that use one.
RED_L   = (0xef, 0x5a, 0x4c)
RED_M   = (0xd0, 0x41, 0x3a)
RED_D   = (0x8e, 0x24, 0x20)
RED_K   = (0x46, 0x10, 0x0d)
CASE_RED = (RED_L, RED_M, RED_D, RED_K)

LCD     = (0x14, 0x1a, 0x11)   # the screen, off


# A round button, four across.  a.disc at this radius rasterises to a
# diamond, and two diamonds beside a cross read as three d-pads.
BUTTON_ROWS = [
    ".##.",
    "####",
    "####",
    ".##.",
]


def bundle_icon(text, case=CASE_GOLD, gap=2):
    """A Game Boy with the word on its screen, in the case colour given.

    The console is the suite and the screen says which half of it, which is
    why the word is on the screen rather than under the console: an icon with
    a caption is two things to read, and one of them is always the one that
    got small.

    Proportion is the compromise here. A DMG is about three units wide to
    five tall; at that ratio on a 32-pixel grid the screen is fourteen pixels
    across, and QOL does not fit on it in any letterform that is still
    letters. The case is drawn wider than life so the screen can hold three
    glyphs. What makes it read as a Game Boy at this size is not the outline
    ratio anyway -- it is the furniture: a bezel deeper below the screen than
    above, a cross, two round buttons set on a diagonal, and two little
    slanted pills for START and SELECT.
    """
    a = Art()
    lit, mid, dark, cut = case

    X0, X1 = 3, 28
    Y0, Y1 = 1, 30

    # ------- the case
    a.rect(X0, Y0, X1, Y1, lit)
    # A bevel rather than a flat fill: light off the top-left, shadow into
    # the bottom-right, which is what stops a rounded rectangle of one colour
    # reading as a sticker.
    a.rect(X0, Y1 - 1, X1, Y1, dark)
    a.rect(X1 - 1, Y0, X1, Y1, dark)
    a.rect(X0, Y0, X1, Y0, mid)
    a.frame(X0, Y0, X1, Y1, INK)

    # The DMG's one asymmetric corner, bottom right, is the detail that says
    # Game Boy before any of the buttons do.
    for i, run in enumerate((4, 2, 1)):
        a.rect(X1 - run + 1, Y1 - i, X1, Y1 - i, BG)
    a.px(X1 - 4, Y1, INK)
    a.px(X1 - 2, Y1 - 1, INK)
    a.px(X1 - 1, Y1 - 2, INK)
    a.px(X1, Y1 - 3, INK)

    # ------- the screen
    #
    # Set down from the top edge rather than against it. Butted up, the strip
    # of case left above it reads as a seam and the whole thing looks like a
    # lid.
    a.rect(5, 4, 26, 17, dark)
    a.frame(5, 4, 26, 17, INK)
    a.rect(6, 6, 25, 15, LCD)
    a.frame(6, 5, 25, 16, cut)

    width = word_width(text, glyphs=LETTERS_SMALL, gap=gap)
    word(a, 6 + (20 - width) // 2, 7, text, lit, dark,
         glyphs=LETTERS_SMALL, gap=gap)

    # ------- the controls
    #
    # The cross left, the buttons right and diagonal, START and SELECT
    # slanted between them: the arrangement is doing more work here than any
    # single piece of it, so each is placed where the eye expects it rather
    # than where it fits best.
    a.rect(6, 22, 11, 23, cut)      # cross, horizontal arm
    a.rect(8, 20, 9, 25, cut)       # cross, vertical arm

    # A above and right of B, with air between them and between both and the
    # stubs below: at four pixels across, anything closer than two pixels
    # merges into one shape once the icon is looked at small.
    stamp(a, 22, 19, BUTTON_ROWS, {"#": cut})   # A
    stamp(a, 16, 22, BUTTON_ROWS, {"#": cut})   # B

    # START and SELECT: two stubs on the slant the real pair sits at.
    a.rect(9, 28, 11, 28, cut)
    a.rect(10, 27, 12, 27, cut)
    a.rect(15, 28, 17, 28, cut)
    a.rect(16, 27, 18, 27, cut)

    return a, lit


# The glove, one character per pixel.  Written out rather than built from
# discs and ellipses like the rest of the icons here, because this shape is
# three round masses that have to meet along shared outlines: composed from
# primitives it kept coming out with a stray pixel where two curves grazed
# each other and a gap where the thumb met the cuff, and every fix for one
# moved the other.  A map has no such argument with itself.
#
#   o  the outline      L  lit              M  the body
#   D  shade            W  the laces        .  through to the ground
GLOVE = [
    "................................",
    ".............oooooo.............",
    "..........oooLLLLLLooo..........",
    "........ooLLLLLLLLLLLLoo........",
    ".......oLLLLLLLLLLLLLLLLo.......",
    "......ooLLLLLLLLLLLLLLLLMo......",
    "......oLLLLLLLLLLLLLLLLLMo......",
    ".....ooLLDLLLDLLLDLLLLLLMMo.....",
    ".....oLLLDLLLDLLLDLLLLLLMMo.....",
    ".....oLLLDLLLDLLLDLLLLLLMMo.....",
    ".....oLLLDLLLDLLLDLLLLLLMMo.....",
    ".....oLLLLLLLLLLLLLLLLLLMMo.....",
    "....ooLLLLLLLLLLLLLLLLLMMMo.....",
    "..oooMMMMMMMMMMMMMMMMMMMMMo.....",
    ".ooLLoMMMMMMMMMMMMMMMMMMMMo.....",
    ".oLLLLoMMMMMMMMMMMMMMMMMMMo.....",
    ".oLLLLoMMMMMMMMMMMMMMMMMMMo.....",
    ".oMMMMooMMMMMMMMMMMMMMMMMMo.....",
    ".oMMMMMoMMMMMMMMMMMMMMMMMMo.....",
    ".oMMMMMoDDDDDDDDDDDDDDDDDDo.....",
    "..oMMMMoDDDDDDDDDDDDDDDDDo......",
    "..oMMMMoDDDDDDDDDDDDDDDDo.......",
    "...ooooooDDDDDDDDDDDDDDo........",
    ".........oooooooooooooo.........",
    "..........oMMMMMMMMMMo..........",
    "..........oDDDDWWDDDDo..........",
    "..........oWWWWWWWWWWo..........",
    "..........oDDDDWWDDDDo..........",
    "..........oWWWWWWWWWWo..........",
    "..........oDDDDWWDDDDo..........",
    "..........oooooooooooo..........",
    "................................",
]


def battle_ui():
    """A purple boxing glove: the battle menu, hitting differently."""
    a = Art()
    stamp(a, 0, 0, GLOVE, {
        "o": INK, "L": PURPLE_L, "M": PURPLE, "D": PURPLE_D, "W": WHITE,
    })
    return a, PURPLE


def wild_qol():
    """A gold Game Boy reading QOL."""
    return bundle_icon("QOL", CASE_GOLD)


def wild_ui():
    """A red Game Boy reading UI."""
    return bundle_icon("UI", CASE_RED, gap=4)


def return_ink(art):
    """Grow a pixel of INK around everything drawn, and hand the art back.

    For the icons whose subject has no straight edges to hang a frame on: the
    outline follows whatever the shapes happened to add up to, so a softened
    corner or a notched ribbon tail is outlined correctly without being
    restated here.  Read off a snapshot taken before any ink is written, or the
    outline would grow a second ring into itself as the loop advanced.
    """
    edge = [[art.g[y][x] != BG for x in range(GRID)] for y in range(GRID)]
    for y in range(GRID):
        for x in range(GRID):
            if edge[y][x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID and 0 <= ny < GRID and edge[ny][nx]:
                    art.px(x, y, INK)
                    break
    return art


def remember():
    """A book with a bookmark in it: the move this POKeMON is being handed back
    was never gone, only closed on -- which is what a bookmark is for.

    Drawn straight on rather than at the three-quarter angle a book usually
    gets in an icon set.  An angled book needs a visible spine, a cover face
    and a page block in perspective, and at 54 pixels -- the size the card
    actually shows -- those three shapes are four pixels each and read as
    stripes.  Face on, the shape is unambiguous at any size: a tall block, a
    darker spine down one side, page edges down the other.

    Two things the ribbon has to do, and both of them are why it is placed
    where it is rather than down the middle:

      * it sits near the FORE EDGE, away from the spine, because that is where
        a bookmark falls and because a stripe down the centre of a cover reads
        as part of the binding rather than as something laid on top of it.
      * it BREAKS the silhouette top and bottom.  A bookmark drawn inside the
        covers is a stripe on a book; one that leaves them is a book somebody
        stopped reading and meant to come back to, which is the mod.

    The cover carries two short gold bars rather than the inset rule a tome
    usually gets: a full frame and a ribbon crossing it is two competing
    rectangles at card size, and the frame is the one that loses nothing by
    going.
    """
    a = Art()
    cover   = GREEN_D
    cover_l = GREEN
    cover_d = (0x3f, 0x4e, 0x08)
    spine   = (0x33, 0x40, 0x07)
    gold    = AMBER
    gold_d  = (0x9a, 0x77, 0x1e)
    page    = (0xef, 0xea, 0xd2)       # bone, not white: paper next to gold
    page_d  = (0xbc, 0xb5, 0x9b)
    ribbon  = RED
    ribbon_l = (0xe8, 0x6b, 0x60)
    ribbon_d = (0x8e, 0x28, 0x24)

    # ---- the page block, offset right and down so it shows past the cover
    a.rect(9, 4, 27, 26, page)
    a.rect(25, 4, 25, 26, page_d)                  # where the leaves start
    for y in range(6, 26, 3):                      # and the leaf edges
        a.rect(26, y, 27, y, page_d)

    # ---- the cover over it, and the spine down the left
    #
    # Stopped at row 24 rather than run to the bottom of the grid, which is
    # what buys the ribbon its six rows of daylight below: a tail that ends
    # level with the covers is a stripe that stops, and the notch in it lands
    # on the outline where nothing can be read.
    a.rect(4, 2, 24, 24, cover)
    a.rect(4, 2, 24, 3, cover_l)                   # lit from above
    a.rect(4, 23, 24, 24, cover_d)
    a.rect(4, 2, 7, 24, spine)                     # the spine
    a.rect(8, 2, 8, 24, cover_d)                   # its hinge shadow
    for x in (4, 24):                              # softened corners
        a.px(x, 2, BG)
        a.px(x, 24, BG)

    # ---- gold: two bands across the spine, two short bars on the cover
    for y in (7, 18):
        a.rect(4, y, 7, y, gold)
        a.rect(4, y + 1, 7, y + 1, gold_d)
    for x0, y0, x1 in ((11, 9, 15), (11, 13, 14)):
        a.rect(x0, y0, x1, y0, gold)
        a.rect(x0, y0 + 1, x1, y0 + 1, gold_d)

    # ---- the ribbon, over everything, out of the top and past the bottom
    a.rect(18, 0, 22, 30, ribbon)
    a.rect(18, 0, 18, 30, ribbon_l)                # a lit edge down one side
    a.rect(22, 0, 22, 30, ribbon_d)
    a.rect(19, 25, 21, 30, ribbon_d)               # the hanging tail, in shade
    a.px(20, 29, BG)                               # notched two rows deep, so
    a.rect(19, 30, 21, 30, BG)                     # the fork reads at 54px
    return_ink(a)
    return a, GREEN


ICONS = {
    "gen1autosave": autosave,
    "Gen1BattleUI": battle_ui,
    "gen1_auto_continue": auto_continue,
    "gen1arena": arena,
    "Gen1MenuManager": menu_manager,
    "Gen1Follower": gen1_follower,
    "gen1_modern_bag": modern_bag,
    "Gen1BillsBox": bills_box,
    "gen1_sound_qol": sound_qol,
    "Gen1Dex": dex,
    "gen1_mod_menu": mod_menu,
    "Gen1Party": party,
    "Gen1Remember": remember,
    "gen151": gen151,
    "gen1_sprint": sprint,
    "gen1_wild_qol": wild_qol,
    "gen1_wild_ui": wild_ui,
}


# --------------------------------------------------------------------------
# out to a file

def png(path, rows):
    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b""))


def render(art, accent, path):
    """Scale up, then the CRT finish: accent glow, vignette, scanlines."""
    mid = SIZE / 2
    far = math.hypot(mid, mid)
    rows = []
    for y in range(SIZE):
        line = bytearray()
        grid_row = art.g[y // SCALE]
        scan = .94 if (y // 2) % 2 else 1.0
        for x in range(SIZE):
            d = math.hypot(x + .5 - mid, y + .5 - mid)
            glow = max(0.0, 1.0 - d / (SIZE * .58)) ** 2 * .13
            dim = (1.0 - .30 * (d / far) ** 2) * scan
            for i, v in enumerate(grid_row[x // SCALE]):
                line.append(min(255, max(0, int((v + accent[i] * glow) * dim))))
        rows.append(line)
    png(path, rows)


def entries():
    """Every mod folder, with the id its meta.json claims."""
    for folder in sorted(p for p in MODS.iterdir() if p.is_dir()):
        meta = folder / "meta.json"
        if not meta.exists():
            continue
        try:
            yield folder, json.loads(meta.read_text(encoding="utf-8")).get("id")
        except json.JSONDecodeError as e:
            print(f"::error::{folder.name}/meta.json: {e}", file=sys.stderr)
            yield folder, None


def main(argv):
    wanted = [a.lower() for a in argv]
    drawn, missing = 0, []
    for folder, mod_id in entries():
        draw = ICONS.get(mod_id)
        if draw is None:
            missing.append(f"{folder.name} ({mod_id or 'no id'})")
            continue
        if wanted and not any(w in folder.name.lower() or w in mod_id.lower()
                              for w in wanted):
            continue
        art, accent = draw()
        render(art, accent, folder / "thumbnail.png")
        print(f"  {folder.name:<38} {SIZE}x{SIZE}")
        drawn += 1
    for m in missing:
        print(f"  {m:<38} no icon: add a draw function", file=sys.stderr)
    print(f"drew {drawn} icon(s)")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
