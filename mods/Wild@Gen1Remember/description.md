A POKéMON can be taught a move it has forgotten — from the popup you already
open on it.

Gen 1 has no move reminder. A move that scrolled off the top of the four slots
on the way up is gone for the rest of the save, and the only thing the cartridge
ever offers back is a TM you have to own. Your BLASTOISE forgot BUBBLE
somewhere between Pallet Town and here, and there is no counter anywhere in the
game that will give it back.

## Where the row is

**REMEMBER** goes in the per-POKéMON popup — the one with STATS and SWITCH on
it — under the rows the engine put there. In the party menu that needs nothing
else installed: the engine's own `ui.party.submenu` hook is built for this and
dispatches a mod's row by calling it, so no screen is replaced and nothing is
patched.

With [Gen1BillsBox](https://github.com/wild1walker/Gen1BillsBox) **1.2.0 or
newer** installed, the same row appears in the box, between that screen's own
verbs and CANCEL — through the extension point that release added to its popup,
registered at `game.ready` so either install order works.

Not in battle. The submenu there is SWITCH / STATS / CANCEL, and a move learned
mid-turn is a mechanic rather than a convenience — which is a different mod.

## What it offers back

Every **level-up move** the POKéMON should already have had at the level it has
reached, minus the four it knows now. Each row names the move and the level it
comes in at, and the list is ordered by that level.

**The forms it evolved out of count.** A CHARIZARD's learnset is CHARIZARD's;
the moves it learned as a CHARMANDER are in CHARMANDER's, and a player who
evolved past EMBER did not stop having forgotten it. So the evolution chain is
walked backwards and every form's learnset counted, on the same level test.

**TM and HM moves are not offered.** A machine move is not forgotten, it is
bought: you still have the TM, or you knowingly spent it. Handing those back
free would quietly rewrite what a TM costs. Level-up moves are the ones the
game took away without asking.

## Picking one

Under four moves, it goes straight into the free slot with the same
`LearnedMove1Text` and jingle the bag's TM path uses — one event should sound
the same however it was started.

On four, the engine's own **MoveLearnMenu** takes over: "Delete an older move to
make room?", the forget list, the HM refusal, and "1, 2 and... Poof!". Every one
of those is text you already know, and a mod that redrew them would get one of
them subtly wrong. It is reached through `Screens.push`, so a mod that has
*replaced* that screen — a translation, a UI overhaul — is the one that answers
here too.

## Nothing is written to your save

The list is **derived**, not recorded. Gen 1 keeps no move history — a save
records the four moves a POKéMON has and not one byte about what it used to
know — so what it has forgotten cannot be read back and has to be worked out.
What this offers is exactly the set the level-up path threw away: it keeps the
most recent four and drops the rest.

Which is the reason to prefer deriving it over recording what got overwritten. A
POKéMON caught before this mod was installed answers exactly the same as one
caught after; a save that has never seen the mod loses nothing by adding it, and
nothing by removing it again; and there is no state to migrate, corrupt, or
disagree with the save.

The cost is the honest one: a TM move a POKéMON learned and then overwrote is
not offered back, because nothing records that it ever had it. That is also the
call this mod would make *with* a record available, for the reason above.

## Settings

`PARTY REMEMBER` and `BOX REMEMBER` turn each surface off. `PRE-EVO MOVES` off
reads the current form's learnset alone, which is the later-generation move
reminder's rule, for anyone who wants evolving to be a door that shuts.
`HIDE WHEN EMPTY` (on) means a POKéMON with nothing to remember carries no row
at all; off leaves the row everywhere and has it say so instead.
