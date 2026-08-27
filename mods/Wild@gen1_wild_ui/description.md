# Gen1WildUI

The visual half of the Gen1Wild suite in one mod. Eleven features, each
switched on and off by itself from `OPTION > GEN1WILD UI`. All of them ship on.

| Feature | |
|---|---|
| **BACKDROPS** | 2D backdrops behind battles, picked by map, tileset and how the encounter started |
| **BATTLE MENUS** | The battle command and move menus as four buttons in a 2x2 grid instead of a list, plus the XP bar |
| **BATTLE INTRO** | The intro flash across the whole window instead of a centred 4:3 square, plus flashless intros and a fade to black |
| **POKEDEX** | A Pokémon beside every entry, base stats, evolutions, the full movelist, and an AREA screen |
| **POKEMON BOX** | Bill's PC as the box it stood in for: party left, twenty slots right |
| **PARTY MENU** | Every Pokémon in its own species colours instead of six sharing one |
| **BAG** | Seven pockets, an icon on every row, auto-sorting, favorites, search, no capacity limit |
| **MENU LAYOUT** | Reorder the START and PC menus, hide rows, pin field moves |
| **MOD MANAGER** | The mod manager redrawn in the game's own OPTION-screen idiom |
| **ITEM INFO** | What every item is, and a picture of it — in the mart's BUY and SELL lists where the clerk used to say *Take your time.*, in the item PC's WITHDRAW, DEPOSIT and TOSS lists, and on an ABOUT row in the bag. Those four lists are redrawn to match the rest of the suite |
| **ELEVATOR PANEL** | The lift's `WHICH FLOOR?` list as a small panel against the edge, with the car still on the screen behind it |

## Nothing is all-or-nothing

Every feature is a row you can switch off, with its own settings one press of
`A` behind it. `BACKDROPS`, `ITEM INFO` and `ELEVATOR PANEL` switch as you
change them; the rest need a relaunch, and the menu marks those rows rather
than pretending otherwise.

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

`BATTLE INTRO` is **ShaneMcGovernIE**'s *Widescreen Battle Intro*, maintained
here now; `BAG` is a derivative of **FAFF0x**'s Modern Bag; the item icons are
**Pokémon Polished Crystal**'s, by **Rangi** and that project's graphics
contributors; `BACKDROPS` draws the *Battle
Backgrounds Patch FR* by **LibertyTwins**, **princess-phoenix**, **carchagui**,
**aveontrainer**, **WesleyFG**, **kWharever**, **worldslayer608** and **knizz**.
The full list is in
[the README](https://github.com/wild1walker/Gen1WildUI#credits).
