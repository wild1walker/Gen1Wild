# Gen1Dex

The Pokédex, with a Pokémon beside every entry, and a screen that finally
tells you where to go looking.

## A list you can read

Every row gets that species' party icon in the margin, in its own colours.
One you have not met yet is a **black silhouette**: the shape is there, the
colours are not, and it fills in the moment you see one.

**SELECT** switches how the list reads: every slot in dex order, or only what
you have seen sorted A to Z, or only what you own. The cursor stays on the
same Pokémon through the switch, and the SEEN / OWN counts always count your
whole dex rather than whatever you are filtering by.

## An entry is three pages

**LEFT** and **RIGHT** walk between them.

1. **DEX**: the sprite, the kind, the height and weight and the description.
   The vanilla page, kept exactly as it was.
2. **STATS**: base stats and their total, the types, and what it evolves into.
3. **MOVES**: the level-up learnset and every TM and HM it can take. Moves it
   gets STAB on are marked in their own type's colour.

## And a map that answers the question

Vanilla's AREA screen refuses to open on a Pokémon you have never seen, which
is backwards, on the one screen you open *to find out where something lives*.
Here it opens on anything, without handing over the dex entry you have not
earned.

**The map also gets a line under it saying how to get there, for all 151.**
The blinking nests tell you *where*; they cannot tell you *in the grass,
around level ten, and rare*, which is the half you actually need. It is read
straight out of the game's live encounter tables, so it is right by
construction. A species that lives nowhere wild gets the answer from the
evolution table instead: `EVOLVE ODDISH / AT LV21`, `MOON STONE / ON
NIDORINO`.

A press takes the hint away and leaves you the plain town map; START brings it
back. And for the handful nobody can answer for (the legendary statics, or
something a mod is deliberately keeping from you) it says `NO RECORD REMAINS`
/ `GO ADVENTURING!` rather than drawing an empty map you cannot tell from a
bug.

Other mods can write that line for their own species.
[Gen151](https://github.com/wild1walker/Gen151) does, for everything it adds.

## Switches

Species colours, the SELECT views, list wrapping, hold-to-scroll, the AREA
hints and whether the START menu's first row says DEX are all separate
options.
Turn the colours off and you get the vanilla dex brown, unchanged.

## Worth knowing

Red, Blue and Yellow. It conflicts with `useful_dex` and `pokedex_plus`. All
three redraw the same screens, so run one. It picks up icon and sprite art
from `unique_menu_icons`, `new_icons` and the HGSS / Gold-Silver / Crystal
sprite sets when you have them installed. MIT.
