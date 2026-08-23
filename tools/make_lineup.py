#!/usr/bin/env python3
"""Draw site/banners/lineup.png: the index's mods, side by side.

Every tile is that mod's own thumbnail.png -- the same 512x512 icon its card
carries in FIND MODS, drawn by tools/make_icons.py -- laid on the index's dark
card colours.  Nothing here is a mock-up or an illustration of a mod: it is
the art the feed actually serves, at the size a reader can take in at once.

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
OUT = ROOT / "site" / "banners" / "lineup.png"

# site/index.html's card colours.
BG = (0x0b, 0x0d, 0x0c)
PANEL = (0x16, 0x1c, 0x17)
EDGE = (0x1e, 0x24, 0x1d)
TEXT = (0xe7, 0xec, 0xe8)
MUTED = (0x8b, 0x97, 0x8f)

TILE = 150          # a thumbnail's drawn size
GAP = 22            # between tiles
PAD = 26            # around the strip
LABEL = 15          # label type size
LABEL_GAP = 14      # between a tile and its label


def gfont(family, weight, size):
    """A Google font, fetched once and kept in tools/.cache/."""
    path = CACHE / f"{family.replace(' ', '')}-{weight}.ttf"
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        css = f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}:wght@{weight}"
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
        meta = folder / "meta.json"
        thumb = folder / "thumbnail.png"
        if not (meta.is_file() and thumb.is_file()):
            continue
        found.append((json.loads(meta.read_text())["title"], thumb))
    return sorted(found)


def rounded(img, radius):
    """Round an image's corners, so a tile sits on the panel like a card."""
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, img.width - 1, img.height - 1), radius, fill=255)
    img.putalpha(mask)
    return img


def main():
    mods = entries()
    if not mods:
        print("no mods with a thumbnail", file=sys.stderr)
        return 1

    font = gfont("Inter", 700, LABEL)
    width = PAD * 2 + TILE * len(mods) + GAP * (len(mods) - 1)
    height = PAD * 2 + TILE + LABEL_GAP + LABEL + 4

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    x = PAD
    for title, thumb in mods:
        tile = Image.open(thumb).convert("RGB").resize((TILE, TILE), Image.LANCZOS)
        draw.rounded_rectangle((x - 1, PAD - 1, x + TILE, PAD + TILE), 11,
                               fill=PANEL, outline=EDGE)
        img.paste(rounded(tile, 10), (x, PAD), rounded(tile.copy(), 10))
        draw.text((x + TILE / 2, PAD + TILE + LABEL_GAP), title,
                  font=font, fill=TEXT, anchor="ma")
        x += TILE + GAP

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"  {OUT.relative_to(ROOT)}  {width}x{height}  ({len(mods)} mods)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
