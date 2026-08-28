# Gen1BillsBox

Bill's PC, as the box it was always standing in for. Your party down the left,
twenty slots in a grid on the right, and a cursor that picks a Pokémon up and
puts it down.

Gen 1's PC is a menu of four verbs over a list of twenty names, and moving one
Pokémon from box 3 to box 7 costs you a withdraw, a box change and a deposit.
This is the same storage, laid out so you can see it.

The layout is Gen 3's idea; every pixel drawing it is Gen 1's. The game's own
font, black line art, its standard bordered boxes. No type colours, no card
chrome, no widescreen. It looks like it was always in there.

## Every Pokémon in its own colours

Twenty of them at once, each wearing its own species palette, where the Game
Boy could only manage four. The slots draw through the party menu's own icon
renderer, so whatever menu-sprite mod you already run shows up in the box too,
without either mod knowing about the other.

## Picking things up

**A** picks a Pokémon up, puts it down, or swaps it with whatever is already
there. **B** is back, and only back. It puts a carried Pokémon down where it
came from, and there is no way to leave the screen holding one.

**LEFT** and **RIGHT** cross between the party and the box, **UP** off the top
row lands on the box header where you can change box, and STATS and RELEASE
moved to **START**, since A became pick-up-and-put-down.

A Pokémon stays in your hand across a box change, so a cross-box move is one
operation instead of three. Drop onto an occupied slot and the two swap, so a
full party and a full box can still trade.

## Two smaller things

The PC's storage row reads **SOMEONE'S BOX** until you meet Bill and **BILL'S
BOX** after, following the same rule the vanilla names already follow.

And when you catch something into a full box, the game finally tells you:
*"BOX 1 was full! / Now using BOX 7."* It always did move you to the next box
with room. It just never said so.

## Switches

The cry when a Pokémon lands in a slot, hold-to-move, which side the cursor
starts on, and the full-box note are all options.

## Worth knowing

Red, Blue and Yellow. It replaces the PC's storage screen, so it conflicts
with `modern_pc_ui`. Run one or the other.
