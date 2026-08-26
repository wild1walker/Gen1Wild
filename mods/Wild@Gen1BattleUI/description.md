# Gen1BattleUI

The battle menu is a list of four words in one box. This makes it four
buttons, two by two, and does the same to the move menu.

Nothing new was invented to draw them. A button here is the game's own text
box — the same call, the same border glyphs, the same white interior — so a
skin or a font mod that redraws the border redraws these buttons with it.

```
rows 12-14   FIGHT | PKMN        four 10x3 boxes, tiling the
rows 15-17   ITEM  | RUN         twenty-by-six strip exactly
```

Three tile rows is the smallest box that holds a line of text, because the
first and last go to the border. Two rows of them is six, which is exactly
what the bottom of a Game Boy screen has.

## The grid was already in the numbers

The engine has always read the command menu as a 2×2 — which is why LEFT and
RIGHT already crossed between FIGHT and PKMN. It was only ever *drawn* as a
list. So none of the menu's behaviour is replaced: the index is still the
engine's, and still moved by the engine's own input handling.

The move menu is the one that actually changes, and the engine already had a
hook for it — the widescreen layout has navigated its moves as a grid all
along.

## Dialogue takes the strip back on its own

Only the three phases that are a *menu* are claimed. When the battle talks it
is still the engine's text box, in the engine's place, with its own scroll and
its own blinking arrow; the buttons are simply not drawn underneath it, and
they are back on the frame the menu is.

The same rule keeps PKMN and ITEM working: the strip is claimed only while the
battle is the top of the state stack, because opening the party or the bag
leaves the battle on the menu phase the whole time that screen is up.

## What two columns inside 160 pixels costs

A cell is seven glyphs where the vanilla list had fourteen, so long move names
are cut — `QUICK ATTACK` reads `QUICK.` It is paid back rather than hidden: a
panel above the grid carries the highlighted move's full name, its type and
its PP, which the vanilla list never showed at once. **MOVE PANEL** turns it
off.

## Widescreen too

`OPTION` → `BATTLE LAYOUT` → `WIDE` gets the same grid, built differently:
five tile rows will not hold two three-row boxes, so it is one box ruled into
four cells with its own border glyphs — border, text, rule, text, border. Its
cells are twelve glyphs, so names arrive whole there and nothing is cut.
