# Gen1WildUI

The visual half of the Gen1Wild suite in one mod. Seven features, each switched
on and off by itself from `OPTION > GEN1WILD UI`. All of them ship on.

| Feature | |
|---|---|
| **BACKDROPS** | 2D backdrops behind battles, picked by map, tileset and how the encounter started |
| **POKEDEX** | A Pokémon beside every entry, base stats, evolutions, the full movelist, and an AREA screen |
| **POKEMON BOX** | Bill's PC as the box it stood in for: party left, twenty slots right |
| **PARTY MENU** | Every Pokémon in its own species colours instead of six sharing one |
| **BAG** | Seven pockets, auto-sorting, favorites, search, no capacity limit |
| **MENU LAYOUT** | Reorder the START and PC menus, hide rows, pin field moves |
| **MOD MANAGER** | The mod manager redrawn in the game's own OPTION-screen idiom |

## Nothing is all-or-nothing

Every feature is a row you can switch off, with its own settings one press of
`A` behind it. Every feature here except `BACKDROPS` needs a relaunch to switch,
and the menu marks those rows rather than pretending otherwise.

`PARTY MENU` reads `POKEDEX` and `POKEMON BOX` when they are on, the same way it
does when the three are installed separately.

`MENU LAYOUT` and `MOD MANAGER` are also in
[Gen1WildQOL](https://github.com/wild1walker/Gen1WildQOL). Install both and
exactly one of them sets each up — they will not collide, and their settings are
stored so it does not matter which won.

## Before you install

Uninstall the standalone versions of anything above. The manifest declares them
as conflicts because they install the same hooks. Settings do not carry over.

## Credit

`BAG` is a derivative of **FAFF0x**'s Modern Bag; `BACKDROPS` draws the *Battle
Backgrounds Patch FR* by **LibertyTwins**, **princess-phoenix**, **carchagui**,
**aveontrainer**, **WesleyFG**, **kWharever**, **worldslayer608** and **knizz**.
The full list is in
[the README](https://github.com/wild1walker/Gen1WildUI#credits).
