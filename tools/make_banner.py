#!/usr/bin/env python3
"""Draw the family wordmarks: fat letters, yellow, on a blue extrusion.

One banner per mod, matching the Gen1Wild logo -- a yellow letter, a thin
darker-blue edge, and a blue 3D extrusion swept down and to the left.  The
edge comes from a distance field around the rasterised glyph, so it keeps an
even width around a letter however round its corners are, and the extrusion
is the solid that silhouette traces as it slides.

    python3 tools/make_banner.py                 # redraw every banner
    python3 tools/make_banner.py Gen1Arena       # ... or just the ones named
    python3 tools/make_banner.py --out /tmp/x.png "Some Name"

Letterforms are Titan One (SIL Open Font Licence 1.1, Rodrigo Fuenzalida),
fetched once into tools/.cache/ -- the font is not vendored, and nothing but
the rendered PNG is committed.  Text set in a font is not a derivative of it,
so the banners carry no licence of their own; the credit is here because the
shapes are someone else's work.

Needs Pillow, numpy and scipy:  pip install Pillow numpy scipy
"""

import argparse
import hashlib
import pathlib
import re
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / ".cache"
FONT_CSS = "https://fonts.googleapis.com/css2?family=Titan+One"
FONT_FILE = CACHE / "TitanOne.ttf"

# The logo's palette: a golden yellow letter over a cornflower blue extrusion,
# with a darker blue drawing the edge between the two and around the solid.
YELLOW = (250, 198, 19)
BLUE = (52, 102, 166)
BLUE_DARK = (38, 71, 129)

SS = 4                     # supersample factor; the render is scaled back down
PT = 220 * SS              # nominal glyph size
BAND = 8 * SS              # the blue drawn around a letter
TRACK = 10 * SS            # extra space between letters
EXT_DX, EXT_DY = -0.42, 1.0    # the extrusion's direction
EXT_LEN = 20 * SS              # ... and its depth
LINE_GAP = 16 * SS         # air between the lines of a stacked wordmark

# Every mod in the family, and how its wordmark breaks across lines.
# Gen1Wild's own wordmark is hand-made artwork kept at docs/banner.png; these
# are the rest of the family, drawn to sit beside it.
BANNERS = {
    "Gen1Arena": ["Gen1Arena"],
    "Gen1AutoSave": ["Gen1AutoSave"],
    "Gen1Follower": ["Gen1Follower"],
    "Gen1ModernBag": ["Gen1ModernBag"],
    "Gen1AutoContinue": ["Gen1", "AutoContinue"],
    "Gen1MenuManager": ["Gen1", "MenuManager"],
}


def font_path():
    """Titan One, fetched once and kept in tools/.cache/.

    The stylesheet is asked for rather than a file URL directly: Google serves
    the font from a versioned path that moves, and hands a client with no
    woff2 in its user agent the plain TrueType we want.
    """
    if not FONT_FILE.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(FONT_CSS, timeout=30) as r:
            css = r.read().decode()
        m = re.search(r"url\((https://[^)]+\.ttf)\)", css)
        if not m:
            raise SystemExit("could not find a TrueType URL in " + FONT_CSS)
        with urllib.request.urlopen(m.group(1), timeout=30) as r:
            FONT_FILE.write_bytes(r.read())
    return str(FONT_FILE)


def jitter(word, i):
    """A letter's tilt and its ride above the baseline.

    Hand lettering does not sit flat, and a font does.  The wobble is derived
    from the word and the position so a given name always draws the same.
    """
    h = hashlib.sha256(f"{word}:{i}".encode()).digest()
    return (h[0] / 255 * 5.0 - 2.5,          # degrees
            int(h[1] / 255 * 11) - 5)        # pixels, at 1x


def line_mask(text, font):
    """Rasterise one line, letter by letter, into a single alpha mask."""
    tiles, advances = [], []
    for i, ch in enumerate(text):
        rot, dy = jitter(text, i)
        box = font.getbbox(ch)
        w, h = box[2] - box[0], box[3] - box[1]
        pad = int(PT * 0.6)
        # Draw the letter alone on a canvas wide enough that a tilt cannot
        # clip it, then rotate in place.
        tile = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
        ImageDraw.Draw(tile).text((pad - box[0], pad - box[1]), ch,
                                  font=font, fill=255)
        if rot:
            tile = tile.rotate(rot, resample=Image.BICUBIC, expand=False)
        tiles.append((tile, pad, dy * SS))
        advances.append(font.getlength(ch) + (TRACK if i < len(text) - 1 else 0))

    width = int(sum(advances)) + 2 * int(PT * 0.6)
    canvas = Image.new("L", (width, int(PT * 3.2)), 0)
    base, x = int(PT * 1.4), 0.0
    for (tile, pad, dy), adv in zip(tiles, advances):
        canvas.paste(tile, (int(x), base - pad + dy), tile)
        x += adv
    return canvas


def stack(lines, font):
    """Lay the lines out centred, one under the next, at one letter size."""
    masks = [trim(line_mask(t, font)) for t in lines]
    width = max(m.width for m in masks)
    height = sum(m.height for m in masks) + LINE_GAP * (len(masks) - 1)
    canvas = Image.new("L", (width, max(1, height)), 0)
    y = 0
    for m in masks:
        canvas.paste(m, ((width - m.width) // 2, y), m)
        y += m.height + LINE_GAP
    return canvas


def trim(mask, margin=0):
    """Crop to the ink, then lay it on a canvas with `margin` px of air.

    The air has to be added rather than kept: a line is trimmed tight before
    it is stacked, so by the time the bands and the extrusion need room to
    grow into there is none left at the edges.
    """
    a = np.array(mask)
    ys, xs = np.nonzero(a > 8)
    if not len(ys):
        return mask
    ink = Image.fromarray(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    out = Image.new("L", (ink.width + 2 * margin, ink.height + 2 * margin), 0)
    out.paste(ink, (margin, margin))
    return out


def sweep(silhouette):
    """The solid a silhouette traces as it slides along the extrusion."""
    h, w = silhouette.shape
    out = silhouette.copy()
    for k in range(1, int(EXT_LEN) + 1):
        ox, oy = int(round(EXT_DX * k)), int(round(EXT_DY * k))
        shifted = np.zeros_like(silhouette)
        y0, y1 = max(0, oy), min(h, h + oy)
        x0, x1 = max(0, ox), min(w, w + ox)
        shifted[y0:y1, x0:x1] = silhouette[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
        out |= shifted
    return out


def draw(lines, out_path):
    font = ImageFont.truetype(font_path(), PT)
    mask = trim(stack(lines, font), margin=int(EXT_LEN + BAND + 10 * SS))
    letters = np.array(mask) > 127
    height, width = letters.shape

    # How far each pixel lies outside the letter, which is what the band is
    # cut from.
    dist = ndimage.distance_transform_edt(~letters)
    banded = dist <= BAND

    img = np.zeros((height, width, 4), dtype=np.uint8)

    def paint(where, rgb):
        img[where] = (*rgb, 255)

    paint(sweep(banded), BLUE_DARK)    # the solid the front face extrudes into
    paint(banded, BLUE)                # the band around the letter
    paint(letters, YELLOW)             # the letter itself

    banner = Image.fromarray(img, "RGBA").resize(
        (width // SS, height // SS), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    banner.save(out_path)
    return banner.size


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("names", nargs="*", help="mod names; default is all of them")
    ap.add_argument("--out", type=pathlib.Path,
                    help="write one banner here instead of site/banners/")
    args = ap.parse_args(argv)

    if args.out:
        if len(args.names) != 1:
            ap.error("--out takes exactly one name")
        name = args.names[0]
        size = draw(BANNERS.get(name, [name]), args.out)
        print(f"  {args.out}  {size[0]}x{size[1]}")
        return 0

    wanted = [n.lower() for n in args.names]
    unknown = [n for n in wanted
               if not any(n == k.lower() for k in BANNERS)]
    if unknown:
        print(f"no such mod: {', '.join(unknown)}", file=sys.stderr)
        return 1

    for name, lines in BANNERS.items():
        if wanted and name.lower() not in wanted:
            continue
        path = ROOT / "site" / "banners" / f"{name}.png"
        size = draw(lines, path)
        print(f"  {name:<20} {size[0]}x{size[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
