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


ICONS = {
    "gen1autosave": autosave,
    "gen1_auto_continue": auto_continue,
    "gen1arena": arena,
    "Gen1MenuManager": menu_manager,
    "Gen1Follower": gen1_follower,
    "gen1_modern_bag": modern_bag,
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
