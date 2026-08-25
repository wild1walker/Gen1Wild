The Pokédex, brought up to the rest of the set — with a POKéMON beside every
entry.

## A party icon beside every entry

The dex list draws each species' party icon in the margin to the left of its
row, resolved down the same path the party menu uses, so a menu-icon mod
(`unique_menu_icons`, `new_icons`) shows up here for free.

A species you have not discovered is a **black silhouette**: its shape is
there, its colours are not, and it fills back in the moment you see one. Every
discovered POKéMON on screen wears its own species colours — six palettes at
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

**LEFT** and **RIGHT** walk between them, wrapping both ways, with an arrow at
each end of the header saying so. **B** closes. **A** still advances too,
because that is the key the vanilla page used.

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

## The AREA screen, and a line under the map

Vanilla's dex side menu returns early unless an entry is seen or owned — which
is exactly backwards on the screen a player opens to find out where something
lives. **A on a blank row opens `AREA` / `QUIT`**, and nothing that would hand
over the dex paragraph you have not earned. It opens on the species the *row*
names, which is what makes it survive this mod's own filtered and re-sorted
views.

**The map gets a line under it saying how to get there, for all 151.** The
blinking nests say *where*; they cannot say *in the grass, around level ten,
and rare*, which is the half you actually need. It is read straight out of the
live encounter tables — the map where the species has the biggest share of the
encounters, that map's own level band, and a rarity worked out from Gen 1's ten
slot buckets — so it is right by construction and costs no data of its own. A
species that is wild nowhere is answered from the evolution table instead:
`EVOLVE ODDISH / AT LV21`, `LINK CABLE / ON KADABRA`, `MOON STONE / ON
NIDORINO`.

**A press takes it away, START brings it back.** The box covers two tile rows of
Kanto and one of them has nests in it, so the first A dismisses the hint and the
second closes the screen, the way A always did. With the hint down it is the
plain town map again — the d-pad moves the cursor and the top strip names the
place it is on, where vanilla's AREA branch ignored the d-pad and stopped drawing
before either. B still leaves immediately.

**And a line for a species nobody can answer for.** The four legendary statics
live in no wild table and evolve from nothing, so AREA on MOLTRES drew a map
with nothing on it — which cannot be told apart from a hint that failed to
draw. The box comes up either way now and says `NO RECORD REMAINS` /
`GO ADVENTURING!`. A species a mod is deliberately withholding gets the same two
lines, which is load-bearing rather than lazy: Gen151 seals Mew until the
Mansion journals are read, and a seal that read differently from an ordinary
blank would tell the player there is something there. Mew's screen and
Moltres's are the same screen to the glyph, and the words are published as
`exports.area.unknown` for anyone who wants to match them.

Vanilla wrote `<NAME> AREA UNKNOWN` into a 19-column strip without measuring
it — `MOLTRES AREA UNKNOWN` is 20 glyphs, so every name of eight or more, half
the dex, lost its last word mid-letter. That line is this mod's now and drops
the word AREA rather than truncating the name: the screen you are standing on
is already called AREA, so the word was carrying nothing, and `MOLTRES UNKNOWN`
fits every name in the dex.

**Other mods can write that line for their own species.**
`mod.find("Gen1Dex").exports.area.provide` takes a function of `(game, species)`
and answers first: two lines to draw them, `false` to withhold an answer the
built-in readings must not fill in for — a spawn behind an event that has not
fired yet — or `nil` for no opinion. Providers are asked in registration order,
first opinion wins, and the table readings are last.
[Gen151](https://github.com/wild1walker/Gen151) 1.5.0 is the first through it:
all of this shipped inside that mod first, where reaching a dex list it did not
own meant wrapping the vanilla constructor and re-deriving each row's species,
which broke the moment a dex mod replaced the rows — and this mod replaces them
wholesale. The screen belongs to whoever draws it.

## The START menu says DEX

The overworld menu's first row is renamed through the engine's
`ui.start_menu.items` hook: same position, same key, same screen behind it, and
every other row untouched. Nothing else that says POKéDEX moves — the SAVE
panel's dex count and the list's own header are separate text. `START SAYS DEX`
turns it off.

## How it sits on the vanilla dex

`PokedexMenu` is built by the vanilla constructor and then re-dressed, so the
`DATA` / `CRY` / `AREA` / `QUIT` side menu, the cursor memory and the `QUIT`
path are exactly as they were. The mod has an opinion about how the list looks
and which entries are in it; what pressing A does is the engine's, apart from
the blank row it used to answer with nothing at all. Every entry point is
guarded rather than trusted — a Pokédex that fails to open is worse than a
vanilla one, so a factory that throws degrades to the builtin.

The icons sit on the vanilla list's own 16-pixel row pitch — sized to fit the
list rather than the list moved to fit them. The list draws six rows rather
than the vanilla seven, because the header and footer boxes cost a tile row at
each end.

## Settings

In the mod manager: **SPECIES COLOURS** (off restores the vanilla dex brown and
asks for no palette zones at all), **SELECT VIEWS**, **UP/DOWN SPECIES**,
**LIST WRAPS**, **HOLD TO SCROLL**, **START SAYS DEX**, **AREA ON UNSEEN** and
**AREA HINTS**. The last two are read when the screen opens rather than once at
load, so flipping either shows up the next time you open it — and turning AREA
HINTS off also takes the caption away from any mod that registered one.

## Compatibility

Red, Blue and Yellow. Requires `engine_internals`. Conflicts with `useful_dex`
and `pokedex_plus` — all three register `DexEntryMenu` and `PokedexMenu`, and
the last one loaded would win silently, so run one or the other. Picks up
optional art from `unique_menu_icons`, `new_icons`, the HGSS/Gold-Silver/Crystal
sprite sets and `crystal_animated_sprites_with_shiny_visuals` when they are
installed. MIT.
