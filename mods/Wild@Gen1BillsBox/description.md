A Gen 3-style storage screen that **replaces** Bill's PC rather than sitting
next to it: your party down the left, the open box as a 5x4 grid of twenty on
the right, and a cursor that picks a POKéMON up and puts it down.

Gen 1's PC is a menu of four verbs over a list of twenty names, and moving one
POKéMON from box 3 to box 7 costs a withdraw, a box change and a deposit. This
is the box that list was always standing in for, and nothing more than that:
drawn in the Game Boy's own font, black line art and its standard bordered
boxes. No type colours, no card chrome, no widescreen layout. The grid is Gen
3's idea; every pixel drawing it is Gen 1's.

## The screen

The slots draw through the party menu's own icon renderer, so whatever menu
sprites you already run show up in the box exactly as they show up in the
party — a menu-icon mod is visible here without either mod knowing about the
other.

Each POKéMON also gets its own palette. The screen emits one SGB zone per
POKéMON, carrying that species' colours, the way the battle and summary
screens do, so a box shows twenty sets of colours where the Game Boy could
show four. That is what forces the tile-aligned layout: a zone is addressed in
tiles, so every cell is 24x24 and every party row 16 tall. The chrome stays
black — shade 3 is `{0,0,0}` in the grey ramp, in `MEWMON` and in all 151
species palettes alike, so the lines stay black whatever is laid over them.
Your COLORS setting still decides what those palettes are.

## Controls

A picks a POKéMON up, puts it down, or swaps it with whatever is in the target
slot. B is back and only back: it returns a carried POKéMON to the slot, and
the box, it came from, and closes the screen only when your hands are empty —
there is no way to leave holding a POKéMON. LEFT out of the first column
crosses to the party and RIGHT crosses back, or SELECT from anywhere. UP out
of the top row lands on the box header, where LEFT and RIGHT change box and A
opens the twelve-box list. STATS and RELEASE moved to START, because A became
pick up and put down.

A carried POKéMON stays with the cursor across a box change, which makes a
cross-box move one operation instead of three. Dropping onto an occupied slot
swaps the two, so a full party and a full box can still trade and nothing is
refused for want of space.

The cursor in the grid is an arrow in the band above a POKéMON's head pointing
down at it, and the same arrow hollow while that POKéMON is in your hand. The
party pane keeps the party menu's own sideways filled and hollow glyphs, since
six rows of sixteen fill that pane exactly and leave no band to put an arrow
in.

## BILL'S PC is BILL'S BOX

The Pokémon Center PC's storage row reads SOMEONE'S BOX until you meet Bill
and BILL'S BOX after, following the same `EVENT_MET_BILL` gate the vanilla
names follow, and the three sentences that name the machine elsewhere follow
it. Those are re-worded rather than replaced — one substitution of the
machine's name over the extracted line — so a localized import keeps its own
wording for the rest of the sentence.

## Catching into a full box

The engine's own `Boxes.deposit` already walks forward from the box you have
open and drops the POKéMON in the first one with room; a catch only fails once
all 240 places are taken. What it never did was tell you, because the line it
prints is the cart's own and the cart never needed to name a box. So this mod
adds one line after it — *"BOX 1 was full! / Now using BOX 7."* — and moves the
open box to match, which stops the PC opening on a box with no room in it and
aims the next overflow at one that has space. Only when the two differ; an
ordinary catch is exactly as quiet as it always was.

## Settings

In the mod manager's row for this mod: **PLACE CRY** (the cry of whichever
POKéMON just landed in a slot), **HOLD TO MOVE**, **OPEN ON** (which side the
cursor starts on), **FULL BOX NOTE** and **SWITCH ON FULL**.

## Compatibility

Replaces the PC's storage screen, so it conflicts with `modern_pc_ui` — run
one or the other. Requires `engine_internals`, which is the first thing to
switch off if a game update breaks the screen. Red, Blue and Yellow.
