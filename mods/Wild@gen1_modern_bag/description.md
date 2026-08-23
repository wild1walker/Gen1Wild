# Gen1ModernBag

Seven pockets instead of one list. Items sort themselves into Items, Balls,
TM/HM, Berries, Key Items, Medicine and Battle Items, and the Bag opens on the
pocket you tell it to. Nothing about what an item *does* changes — using one
still runs the vanilla Bag menu underneath.

- **Favorites and pins.** Mark what you reach for; pinned items stay at the top
  of their pocket across sessions.
- **Search.** Type to filter, which is the fastest way through a full TM pocket.
- **Hold to scroll.** Holding the d-pad accelerates instead of stepping.
- **TM/HM tools** for a pocket that fills up and never empties.
- **No capacity limit.** The 20-slot ceiling is gone.

## Attribution — required

Gen1ModernBag is a derivative of the **Modern Bag** mod by **FAFF0x**, taken
from <https://github.com/FAFF0x/gen1recomp> at upstream version **1.6.0**.
Modern Bag is MIT licensed, and the original copyright and permission notice
travels verbatim in the mod's `LICENSE` with the derivative grant appended
below it.

Essentially all of the functionality above is upstream's work. It is an
independent, parallel project: not endorsed by or affiliated with FAFF0x or
the gen1recomp project, and not a replacement, successor or official
continuation of Modern Bag.

## What is different

One constant. In upstream 1.6.0 a long TM/HM label draws past the right edge
of the item window: the truncation helper budgets 15 characters where the
drawable run inside the window is 13 glyphs, so a 15-character label passes
through untouched and clips mid-word, and a 17-character one is cut to 15,
putting the ellipsis itself off-screen. At 13 the labels stay inside the
window. The mod's own README works the number out from the tile geometry.

## Running it

It declares `conflicts: ["modern_bag"]`, so it and upstream's Modern Bag are
not meant to be enabled together — they cover the same ground and both patch
the Bag. Pick one.

`gen1_modern_ui` is an optional dependency: installed, the Bag is presented in
its style; absent, the mod runs on its own.

It requests `engine_internals`, and needs it — the Bag menu is engine code.
