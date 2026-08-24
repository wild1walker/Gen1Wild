The Pokédex, brought up to the rest of the set — with a POKéMON beside every
entry.

## A party icon beside every entry

The dex list draws each species' party icon in the margin to the left of its
row, resolved down the same path the party menu uses, so a menu-icon mod
(`unique_menu_icons`, `new_icons`) shows up here for free.

A species you have not discovered is a **black silhouette**: its shape is
there, its colours are not, and it fills back in the moment you see one. Every
discovered POKéMON on screen wears its own species colours — seven palettes at
once, where the Game Boy could show four.

The silhouette is a draw-time tint rather than a palette zone, which is the
only version of it that also holds for an icon mod's authored full-colour art:
a zone of four blacks would blacken a DMG icon, but full-colour art is re-blit
unshaded over the colourised pass and would come back in colour underneath.

## Three ways to read the list

**SELECT** cycles the view: `POKéDEX` is every slot in order, blanks included;
`POKéDEX A-Z` is only what you have seen, sorted by name with the dex numbers
kept; `POKéDEX CAUGHT` is only what you own, in dex order. The cursor stays on
the same POKéMON wherever it survives the switch, and the `SEEN` / `OWN` counts
in the footer are the whole dex's in every view — they count your Pokédex, not
the filter you are looking through it with.

UP on the first row and DOWN on the last wrap to the other end.

## An entry is three pages

**A** moves between them, **B** closes.

1. **DEX** — the sprite, the kind, height and weight, and the description.
   This is the vanilla page, kept: A turns the description's own pages first,
   the way it did in the ROM, and only moves on once the text is spent.
2. **STATS** — the five base stats and their **BST**, the types, and what the
   species evolves into.
3. **MOVES** — the level-up learnset, then TM/HM by machine number, eight rows
   to a page. Machine numbers are read off the ITEMS registry rather than a
   hard-coded table, so a mod that adds TM51 needs no help.

Moves the species gets **STAB** on are chipped in their own type's colour, and
each type on the STATS page is underlined in its own. Both are marked true
colour, so the SGB shade remap cannot turn them into arbitrary greys. On the
first two pages UP/DOWN opens the previous or next species you have seen,
wrapping at both ends; on MOVES they page the list.

## How it sits on the vanilla dex

Two registered screen replacements and nothing else. `PokedexMenu` is built by
the vanilla constructor and then re-dressed, so the `DATA` / `CRY` / `AREA` /
`QUIT` side menu, the cursor memory and the `QUIT` path are exactly as they
were: the mod has an opinion about how the list looks and which entries are in
it, and none at all about what pressing A on one does. Every entry point is
guarded rather than trusted — a Pokédex that fails to open is worse than a
vanilla one, so a factory that throws degrades to the builtin.

The icons sit on the vanilla list's own 16-pixel row pitch, which is why the
list still draws seven rows: the icons were sized to fit the list rather than
the list moved to fit the icons.

## Settings

In the mod manager: **SPECIES COLOURS** (off restores the vanilla dex brown and
asks for no palette zones at all), **SELECT VIEWS**, **UP/DOWN SPECIES**,
**LIST WRAPS** and **HOLD TO SCROLL**.

## Compatibility

Red, Blue and Yellow. Requires `engine_internals`. Conflicts with `useful_dex`
and `pokedex_plus` — all three register `DexEntryMenu` and `PokedexMenu`, and
the last one loaded would win silently, so run one or the other. Picks up
optional art from `unique_menu_icons`, `new_icons`, the HGSS/Gold-Silver/Crystal
sprite sets and `crystal_animated_sprites_with_shiny_visuals` when they are
installed. MIT.
