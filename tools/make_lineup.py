#!/usr/bin/env python3
"""Draw the family strip: every mod in the index, side by side.

Every tile is that mod's own thumbnail.png -- the same 512x512 icon its card
carries in FIND MODS, drawn by tools/make_icons.py -- laid on the index's dark
card colours.  Nothing here is a mock-up or an illustration of a mod: it is
the art the feed actually serves, at a size a reader can take in at once.

Two shapes come out of this:

    site/banners/lineup.png           plain, for this repo's own README
    site/banners/lineup-<Mod>.png     one per mod, that mod ringed, under a
                                      "Check out my other mods!" line

The per-mod ones are what each mod repo carries at docs/lineup.png, so a
reader landing on any one of them can see the rest of the family and where
the page they are on sits in it.

    python3 tools/make_lineup.py

Labels are set in Inter (SIL Open Font Licence 1.1, Rasmus Andersson), fetched
once into tools/.cache/.

Needs Pillow:  pip install Pillow
"""

import json
import pathlib
import re
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODS = ROOT / "mods"
CACHE = ROOT / "tools" / ".cache"
OUT = ROOT / "site" / "banners"

# site/index.html's card colours, and the Game Boy green it uses for links.
BG = (0x0b, 0x0d, 0x0c)
PANEL = (0x16, 0x1c, 0x17)
EDGE = (0x1e, 0x24, 0x1d)
TEXT = (0xe7, 0xec, 0xe8)
ACCENT = (0x9b, 0xbc, 0x0f)

TILE = 150          # a thumbnail's drawn size
GAP = 24            # between tiles
PAD = 26            # around the strip
RING = 3            # the ring around the mod being viewed
LABEL = 15          # label type size
LABEL_GAP = 14      # between a tile and its label
HEAD = 19           # the "check out" line
HEAD_GAP = 20       # between it and the tiles

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


def entries():
    """Every mod in the feed that has an icon, in title order."""
    found = []
    for folder in sorted(MODS.iterdir()):
        meta, thumb = folder / "meta.json", folder / "thumbnail.png"
        if meta.is_file() and thumb.is_file():
            found.append((json.loads(meta.read_text())["title"], thumb))
    return sorted(found)


def rounded(img, radius):
    """Round an image's corners, so a tile sits on the panel like a card."""
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, img.width - 1, img.height - 1), radius, fill=255)
    img.putalpha(mask)
    return img


def strip(mods, out, highlight=None, heading=None):
    """Draw the strip, optionally ringing one mod and topped with a line."""
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
        here = title == highlight
        tile = Image.open(thumb).convert("RGB").resize((TILE, TILE),
                                                       Image.LANCZOS)
        draw.rounded_rectangle((x - 1, top - 1, x + TILE, top + TILE), 11,
                               fill=PANEL, outline=EDGE)
        img.paste(rounded(tile, 10), (x, top), rounded(tile.copy(), 10))
        if here:
            # The ring sits outside the tile, in the gap between two of them.
            draw.rounded_rectangle(
                (x - RING - 1, top - RING - 1, x + TILE + RING, top + TILE + RING),
                11 + RING, outline=ACCENT, width=RING)
        draw.text((x + TILE / 2, top + TILE + LABEL_GAP), title,
                  font=label_font, fill=ACCENT if here else TEXT, anchor="ma")
        x += TILE + GAP

    OUT.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"  {out.relative_to(ROOT)}  {width}x{height}"
          + (f"  ({highlight} ringed)" if highlight else ""))


def main():
    mods = entries()
    if not mods:
        print("no mods with a thumbnail", file=sys.stderr)
        return 1

    strip(mods, OUT / "lineup.png")
    for title, _ in mods:
        strip(mods, OUT / f"lineup-{title}.png",
              highlight=title, heading=CALL_TO_ACTION)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
