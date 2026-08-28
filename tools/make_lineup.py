#!/usr/bin/env python3
"""Draw the family strip: the mods in the index, side by side.

Every tile is that mod's own thumbnail.png -- the same 512x512 icon its card
carries in FIND MODS, drawn by tools/make_icons.py -- laid on the index's dark
card colours.  Nothing here is a mock-up or an illustration of a mod: it is
the art the feed actually serves, at a size a reader can take in at once.

Two shapes come out of this:

    site/banners/lineup.png           every mod, for this repo's own README
    site/banners/lineup-<Mod>.png     one per mod: seven tiles, under a
                                      "Check out my other mods!" line

The per-mod ones are what each mod repo carries at docs/lineup.png, so a
reader landing on any one of them can see where the page they are on sits in
the family.  Seven tiles, in fixed places: the mod you are reading about
first, ringed in yellow; the Wild Green cart in the middle, ringed in green;
five other mods around them.  See sample() below.

    python3 tools/make_lineup.py

Labels are set in Inter (SIL Open Font Licence 1.1, Rasmus Andersson), fetched
once into tools/.cache/.

Needs Pillow:  pip install Pillow
"""

import hashlib
import json
import pathlib
import re
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODS = ROOT / "mods"
CART = ROOT / "carts" / "Wild@wild_green"
CACHE = ROOT / "tools" / ".cache"
OUT = ROOT / "site" / "banners"

# site/index.html's card colours, the Game Boy green it uses for links, and
# the brand yellow it marks a featured entry with.
BG = (0x0b, 0x0d, 0x0c)
PANEL = (0x16, 0x1c, 0x17)
EDGE = (0x1e, 0x24, 0x1d)
TEXT = (0xe7, 0xec, 0xe8)
ACCENT = (0x9b, 0xbc, 0x0f)
BRAND = (0xfa, 0xc6, 0x13)

TILE = 150          # a thumbnail's drawn size
GAP = 24            # between tiles
PAD = 26            # around the strip
RING = 3            # the ring around a marked tile
LABEL = 15          # label type size
LABEL_GAP = 14      # between a tile and its label
HEAD = 19           # the "check out" line
HEAD_GAP = 20       # between it and the tiles

COMPANIONS = 5      # other mods, either side of the cart
CART_SLOT = 3       # the middle of seven

CALL_TO_ACTION = "Check out my other mods!"


def gfont(family, weight, size):
    """A Google font, fetched once and kept in tools/.cache/."""
    path = CACHE / f"{family.replace(' ', '')}-{weight}.ttf"
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        css = (f"https://fonts.googleapis.com/css2?family="
               f"{family.replace(' ', '+')}:wght@{weight}")
        with urllib.request.urlopen(css, timeout=30) as r:
            sheet = r.read().decode()
        m = re.search(r"url\((https://[^)]+\.ttf)\)", sheet)
        if not m:
            raise SystemExit(f"no TrueType URL for {family} {weight}")
        with urllib.request.urlopen(m.group(1), timeout=30) as r:
            path.write_bytes(r.read())
    return ImageFont.truetype(str(path), size)


def tiles(folder):
    """(title, thumbnail) for every entry in a folder that has an icon."""
    found = []
    for entry in sorted(folder.iterdir()):
        meta, thumb = entry / "meta.json", entry / "thumbnail.png"
        if meta.is_file() and thumb.is_file():
            found.append((json.loads(meta.read_text())["title"], thumb))
    return sorted(found)


def entries():
    """Every mod in the feed that has an icon, in title order."""
    return tiles(MODS)


def cart():
    """The Wild Green cart's tile, or None if it has no icon."""
    meta, thumb = CART / "meta.json", CART / "thumbnail.png"
    if meta.is_file() and thumb.is_file():
        return (json.loads(meta.read_text())["title"], thumb)
    return None


def sample(mods, title, green):
    """Seven tiles, in fixed places, for one mod's own strip.

    Every mod on every mod's page grew with the index and was read by nobody.
    A dozen icons over a dozen names is a wall, and the one you are already
    looking at is lost in the middle of it.  Seven is a glance, and three of
    the seven are saying something:

        1st       the mod whose page this is, ringed in yellow
        middle    the Wild Green cart, ringed in green -- the whole suite,
                  playable as its own version, on every page in the family
        the rest  five other mods, so there is somewhere else to go

    The five are arbitrary but not fresh: each candidate is ordered by a hash
    of its name paired with the name of the mod whose strip this is, so every
    mod gets its own five, the same five on every machine, and a rebuild that
    changed nothing redraws the same file and commits nothing.  Adding a mod
    reshuffles all of them, which is the point -- a new one turns up on other
    mods' pages without anything being chosen by hand.
    """
    here = [m for m in mods if m[0] == title]
    others = [m for m in mods if m[0] != title]

    def draw(other):
        pair = f"{title}\x00{other[0]}".encode("utf-8")
        return hashlib.sha256(pair).hexdigest()

    picked = sorted(sorted(others, key=draw)[:COMPANIONS])

    row = here + picked
    if green:
        row.insert(min(CART_SLOT, len(row)), green)
    return row


def rounded(img, radius):
    """Round an image's corners, so a tile sits on the panel like a card."""
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, img.width - 1, img.height - 1), radius, fill=255)
    img.putalpha(mask)
    return img


def strip(mods, out, rings=None, heading=None):
    """Draw the strip, ringing the marked tiles and topping it with a line."""
    rings = rings or {}
    label_font = gfont("Inter", 700, LABEL)
    head_font = gfont("Inter", 700, HEAD)

    top = PAD + ((HEAD + HEAD_GAP) if heading else 0)
    width = PAD * 2 + TILE * len(mods) + GAP * (len(mods) - 1)
    height = top + TILE + LABEL_GAP + LABEL + PAD

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    if heading:
        draw.text((width / 2, PAD), heading, font=head_font,
                  fill=ACCENT, anchor="ma")

    x = PAD
    for title, thumb in mods:
        ring = rings.get(title)
        tile = Image.open(thumb).convert("RGB").resize((TILE, TILE),
                                                       Image.LANCZOS)
        draw.rounded_rectangle((x - 1, top - 1, x + TILE, top + TILE), 11,
                               fill=PANEL, outline=EDGE)
        img.paste(rounded(tile, 10), (x, top), rounded(tile.copy(), 10))
        if ring:
            # The ring sits outside the tile, in the gap between two of them.
            draw.rounded_rectangle(
                (x - RING - 1, top - RING - 1, x + TILE + RING, top + TILE + RING),
                11 + RING, outline=ring, width=RING)
        draw.text((x + TILE / 2, top + TILE + LABEL_GAP), title,
                  font=label_font, fill=ring or TEXT, anchor="ma")
        x += TILE + GAP

    OUT.mkdir(parents=True, exist_ok=True)
    img.save(out)
    marked = ", ".join(sorted(rings)) if rings else ""
    print(f"  {out.relative_to(ROOT)}  {width}x{height}"
          + (f"  ({marked} ringed)" if marked else ""))


def main():
    mods = entries()
    if not mods:
        print("no mods with a thumbnail", file=sys.stderr)
        return 1

    green = cart()
    if green is None:
        print("no cart thumbnail; strips will run six wide", file=sys.stderr)

    strip(mods, OUT / "lineup.png")
    for title, _ in mods:
        rings = {title: BRAND}
        if green:
            rings[green[0]] = ACCENT
        strip(sample(mods, title, green), OUT / f"lineup-{title}.png",
              rings=rings, heading=CALL_TO_ACTION)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
