# Gen1BattleUI

The battle menu is a list of four words in one box. This makes it four
buttons, two by two, and does the same to the move menu.

Nothing new was invented to draw them. A button here is the game's own text
box: the same call, the same border glyphs, the same white interior. So a skin
or a font mod that redraws the game's borders redraws these buttons with it.

```
FIGHT | PKMN
ITEM  | RUN
```

## The grid was already in there

The engine has always read the command menu as a 2x2, which is why LEFT and
RIGHT already crossed between FIGHT and PKMN. It was only ever *drawn* as a
list. So none of the menu's behaviour is replaced: the cursor is still the
engine's, moved by the engine's own input handling.

## Dialogue still gets the bottom of the screen

Only the parts that are actually a *menu* are claimed. When the battle is
talking it is the engine's text box, in the engine's place, with its own
scroll and its own blinking arrow; the buttons simply are not drawn
underneath, and they are back the frame the menu is. Same rule keeps PKMN and
ITEM working.

## What two columns costs

A cell holds seven characters where the vanilla list had fourteen, so a long
move name gets cut: `QUICK ATTACK` reads `QUICK.` That is paid back rather
than hidden. A panel above the grid carries the highlighted move's full name,
its type and its PP, which the vanilla list never showed at once. One switch
turns it off.

Widescreen gets the same grid, built to fit its own layout, and there the
cells are wide enough that nothing is cut at all.
