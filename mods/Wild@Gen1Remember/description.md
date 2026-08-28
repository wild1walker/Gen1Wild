# Gen1Remember

A Pokémon can be taught a move it has forgotten, from the popup you already
open on it.

Gen 1 has no move reminder. A move that scrolled off the top of the four slots
on the way up is gone for the rest of the save, and the only thing the
cartridge ever offers back is a TM you have to own. Your BLASTOISE forgot
BUBBLE somewhere between Pallet Town and here, and nothing in the game will
give it back.

## Where to find it

**REMEMBER** sits in the per-Pokémon popup, the one with STATS and SWITCH on
it, in the party menu, and in the box too if you run
[Gen1BillsBox](https://github.com/wild1walker/Gen1BillsBox). Nothing else
needs installing; it uses a hook the engine already has for exactly this.

Not in battle. A move learned mid-turn is a mechanic rather than a
convenience, which is a different mod.

## What it offers back

Every level-up move that Pokémon should already have had by the level it has
reached, minus the four it knows now, each one listed with the level it comes
in at.

**The forms it evolved out of count.** A CHARIZARD's learnset is CHARIZARD's,
but the moves it learned as a CHARMANDER are in CHARMANDER's, and a player who
evolved past EMBER did not stop having forgotten it. So the whole evolution
chain is walked back.

**TM and HM moves are not offered.** A machine move is not forgotten, it is
bought: you still have the TM, or you knowingly spent it. Handing those back
free would quietly rewrite what a TM costs. Level-up moves are the ones the
game took away without asking.

Picking one works exactly like the bag's TM path, with the same jingle and, on
a full moveset, the same "Delete an older move to make room?" screen you
already know.

## Nothing is written to your save

The list is worked out, not recorded. Which means a Pokémon caught before you
installed this answers exactly the same as one caught after; a save loses
nothing by adding the mod and nothing by removing it again; and there is no
new state to corrupt or migrate.

## Switches

Each surface, party and box, can be turned off on its own. `PRE-EVO MOVES`
off reads only the current form's learnset, which is the later-generation
rule, for anyone who wants evolving to be a door that shuts. And a Pokémon
with nothing to remember carries no row at all, unless you would rather it
said so.
