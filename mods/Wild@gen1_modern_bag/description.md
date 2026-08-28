# Gen1ModernBag

Seven pockets instead of one list. Items, Balls, TM/HM, Berries, Key Items,
Medicine and Battle Items sort themselves out, and the bag opens on whichever
one you tell it to.

Nothing about what an item *does* changes. Using one still runs the game's
own bag underneath.

- **A picture on every row.** Every item is drawn with its own icon, and a TM
  or HM is a disc in the colour of the type it teaches, which is the whole of
  what tells TM24 from TM25 in a pocket of fifty-five four-letter names.
- **Favourites and pins.** Mark what you actually reach for; pinned items stay
  at the top of their pocket.
- **Search.** Type to filter, which is the fastest way through a full TM pocket.
- **Hold to scroll**, so a long list is one press rather than forty.
- **No capacity limit.** The 20-slot ceiling is gone.

## Attribution (required)

Gen1ModernBag is a derivative of the **Modern Bag** mod by **FAFF0x**, taken
from <https://github.com/FAFF0x/gen1recomp> at upstream version **1.6.0**.
Modern Bag is MIT licensed, and the original copyright and permission notice
travels verbatim in the mod's `LICENSE`.

Essentially all of the functionality above is upstream's work. This is an
independent, parallel project: not endorsed by or affiliated with FAFF0x or
the gen1recomp project, and not a replacement, successor or official
continuation of Modern Bag.

The item art is **Pokémon Polished Crystal's**, by **Rangi** and that
project's graphics contributors, not this project's. The mod's `CREDITS.md`
carries the attribution and the terms, and travels with the assets.

## Worth knowing

It declares a conflict with upstream's Modern Bag. They cover the same ground
and both patch the bag, so pick one. `gen1_modern_ui` is optional: installed,
the bag is presented in its style; absent, this runs on its own.
