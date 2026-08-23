#!/usr/bin/env python3
"""Cut the site's favicon out of the wordmark.

The mark is committed artwork, not something a tool redraws -- see the README.
So the favicon is not drawn either: it is the wordmark's own leading G, lifted
straight out of docs/banner.png and set on the mark's blue, which keeps the tab
icon and the banner the same object rather than two things that have to be kept
looking alike by hand.

    python3 tools/make_favicon.py

Writes site/favicon.png (180, also the apple-touch icon) and site/favicon-32.png.
Re-run it after replacing the wordmark.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BANNER = ROOT / "docs" / "banner.png"
OUT = ROOT / "site"

# The G, in wordmark pixels.  The glyphs carry overlapping drop shadows, so
# there is no gap between letters to find programmatically -- this is measured.
GLYPH = (10, 15, 375, 505)

BLUE = (38, 71, 129, 255)   # the wordmark's own shadow blue, #264781
FILL = 0.82                 # how much of the tile the glyph occupies

SIZES = [(180, "favicon.png"), (32, "favicon-32.png")]


def main() -> None:
    if not BANNER.exists():
        raise SystemExit(f"no wordmark at {BANNER}")

    glyph = Image.open(BANNER).convert("RGBA").crop(GLYPH)

    for size, name in SIZES:
        inner = round(size * FILL)
        g = glyph.copy()
        g.thumbnail((inner, inner), Image.LANCZOS)
        tile = Image.new("RGBA", (size, size), BLUE)
        tile.alpha_composite(g, ((size - g.width) // 2, (size - g.height) // 2))
        tile.save(OUT / name)
        print(f"wrote site/{name}  {size}x{size}")


if __name__ == "__main__":
    main()
