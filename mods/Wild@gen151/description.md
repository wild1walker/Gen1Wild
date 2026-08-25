Every one of the 151 becomes obtainable **renewably** in a single save, on any
one version, without trading — while every encounter that exists in the vanilla
game keeps its exact vanilla behaviour.

Two words carry the whole mod.

**Renewable.** Not "obtainable". A one-time static, a gift NPC or a scripted
event does not count, even when it fills the dex slot. If you KO it, flee, run
out of Balls, or want a second one to evolve, the game has to be able to produce
another. Every species Gen151 touches ends up in a table that can be rolled
again tomorrow.

**Additive.** It never rewrites a vanilla encounter slot, never changes a
vanilla encounter rate, and never removes a species from a table it already
occupies. The only new thing that can happen is a new thing.

What that costs, stated plainly: a vanilla species' *share* of a placed map's
encounters shifts by the substitution rate. Probability is conserved and
something has to give. Two ceilings bound it — no placement is ever more than
**4.30%** of a map, which is vanilla's own ninth slot, and no map gives away
more than **25%** of its encounters — so three encounters in four are vanilla
everywhere. It is also a single number you can turn down, or off, in the
options.

## How rare is rare

Gen 1 picks a wild slot from ten buckets out of 256, whose widths are
`51 51 39 25 25 25 13 13 11 3`. The rarest thing the cartridge ever asks you to
find is a tenth-slot species at **3/256 = 1.17%**, about 85 encounters. Nothing
here is rarer than that: a mod whose premise is that the vanilla encounter is
untouched has no business charging more for its own additions than the game
charges for its own.

| tier | anchored to | the hunt |
|---|---|---|
| uncommon | vanilla's 9th slot, 11/256 | ~160 steps |
| rare | between the 9th and the 10th | ~280 steps |
| very rare | vanilla's 10th slot, 3/256 | ~600 steps |

A tier is a promise about the **hunt**, not about the share. A fixed share costs
nearly twice as much on a quiet map as on a busy one — same word on the tin,
twice the walk — so the share is re-solved from each map's own encounter rate
and the walk is what stays constant. Seeing all 23 additions on Red, one after
another, is about two and a half hours; the worst single hunt is Snorlax at
eleven minutes.

## Where the placements come from

Nothing was hand-listed. The derivation reads the [pret](https://github.com/pret)
disassembly with the same parse the engine's own extractor performs and works
out, for Red, Blue and Yellow separately, which of the 151 have no renewable
source. That gap set is what the placements answer: 23 species placed per
version, 16 to 18 more following by evolution, four behind the LINK CABLE, and
four left alone on purpose.

**Version exclusives** get the answer the sibling cartridge already gave. Blue
puts Sandshrew on Routes 4, 8, 9, 10, 11 and 23, so Red gets the same maps at
the substitution rate, carrying Blue's own levels. It is the most defensible
source there is, and it makes the addition feel like it was always there —
because on the other cartridge it was.

**Everything else** is a design decision with a written justification, one per
row. Where a later official Kanto game answered "where does this live" — Let's
Go's wild Bulbasaur in Viridian Forest, its Charmander on Route 3, its Squirtle
on Route 25 — that answer is used verbatim. Where no official game ever placed
the species in Kanto, the location is invented and the reasoning is written down
next to it.

**Levels** come from the destination map, never from the species' vanilla gift
level. A Charmander that spawns on Victory Road at level 5 is a dex checkbox; at
the area's band it is a POKéMON you might actually use.

## Trade evolutions: the LINK CABLE

Alakazam, Machamp, Golem and Gengar are not spawns. Their pre-evolutions are
already in the vanilla grass on every version; what was missing was the trade.

**Celadon Department Store 4F** sells a LINK CABLE for 2100, on the same shelf
and at the same price as the four evolution stones. It buys exactly one
evolution, the same as a stone does, and it runs it as a *trade* evolution — so
B is read and thrown away exactly as `evolution.asm` does, and the cable snaps
on the way out.

## Finding what is left

The dex **AREA** screen already works: it scans the live encounter tables and
blinks a nest on every matching map, so anything Gen151 adds to a slot table
shows up there on its own.

A nest says *where*. It cannot say *in the grass, around level ten, and rare*,
which is the half you actually need — so the map gets a line under it. **That
screen belongs to [Gen1Dex](https://github.com/wild1walker/Gen1Dex)**, 1.3.0
and later: opening AREA on an entry you have never met, the box under the map,
the press that takes it down and the START that brings it back are all its. All
of it shipped here first, and reaching a list this mod does not own meant
wrapping two engine screens from the outside and stamping every row with its
species so a dex mod replacing them wholesale did not strand the lookup — which
is exactly the bug that shipped, because Gen1Dex replaces them wholesale. A
content mod has no business owning a UI surface it has to reach two screens deep
to install.

What Gen151 keeps is the half that was always its: the **sentence**. The
encounter tables cannot carry which tier this mod rolled a placement at, or that
a map needs SURF to reach — those are facts about the placement, and the
placement is here. So it registers one caption provider with that screen and
answers for the species it placed, from the same resolved rows the roll layer is
using, so a hint cannot drift from its spawn. It also covers the two Super Rod
placements, which have no slot for AREA to find and so blink no nest at all.

Everything else on that screen is Gen1Dex reading the live encounter tables by
itself — right by construction, and costing no placement data at all.

**Mew is the exception, on purpose.** While its gate is shut it is not in the
encounter table, so there is no nest, and Gen151 answers for it with a refusal
rather than a silence — otherwise the generic reading would fill the gap. With
Gen1Dex 1.4.0 that refusal draws the same `NO RECORD REMAINS` / `GO
ADVENTURING!` screen the four legendary statics get, to the glyph: a seal that
read differently from an ordinary blank would tell you there is something in
there, which is the one thing it exists not to say. The moment the journals are
read, Mew is captioned like anything else.

**Without Gen1Dex there is no screen to write on.** AREA is the cartridge's own,
the mod says so once in the log, and nothing else about Gen151 changes. Turn
**AREA HINTS** off and Gen1Dex's screen goes back to saying whatever it reads out
of the encounter tables by itself.

Gen151 still declares `engine_internals`, so it still wears the **PATCHES ENGINE
CODE** badge — but there is one call behind it now: the LINK CABLE's own sound
effect reaches `src.core.Sound`, which the mod surface has no facade for. The two
screen wraps that used to be the reason for it are Gen1Dex's, and it is Gen1Dex
that wears the badge for them.

## Every decision is its own row

The single biggest complaint about the existing all-151 mod is that it is
all-or-nothing; someone who wants the version exclusives but not a wild Mew
should not have to fork it.

| Option | Default | What it does |
|---|---|---|
| GEN151 | on | master switch; off registers nothing at all |
| EXCLUSIVES | on | the version-exclusive spawns |
| GIFT MONS | on | starters, Eevee, Lapras, Porygon, the Dojo pair, the NPC-trade mons |
| FOSSILS | on | Omanyte, Kabuto, Aerodactyl |
| SNORLAX | on | the renewable Snorlax |
| TRADE EVOS | LINK CABLE | LINK CABLE, or off entirely |
| CABLE SOUND | on | the snap |
| MEW EVENT | on | the Mansion journals and what they unlock |
| LEGENDARIES | stay til caught | one shot each, but a fled or fainted one comes back |
| RARITY % | 100 | scales every tier at once; 0 disables every substitution |
| AREA HINTS | on | this mod's own words under Gen1Dex's AREA map (needs Gen1Dex) |

## Decisions worth knowing about

**Legendaries.** Articuno, Zapdos, Moltres and Mewtwo keep their vanilla
statics: same object, same level, same one-at-a-time, and they stay the sole
exception to the renewability rule. What they are no longer is *losable*. On the
cartridge the beat flag is set on any non-blackout end — win, catch or flee
alike — so knocking one out by accident deletes that species from the file.
That is not a rare encounter, it is a saving throw. Beat one or flee it and it
is standing there again when you come back; catch it and it is gone for good,
exactly as in vanilla. It also repairs a save that lost one before the mod was
installed, and **LEGENDARIES: ONE SHOT** puts the cartridge's behaviour back.

**Snorlax** is not a legendary and does not inherit the exception. Both statics
stay, and a third, very rare Snorlax turns up on Routes 13 and 17 — next door to
each sleeper — so KOing or fleeing both is not a lockout.

**Mew** is the one invention rather than a restoration, which is why it has a
switch of its own. Reading all four Pokémon Mansion journals flips an event
flag, and only then does Mew become a very rare renewable encounter in the
basement the journals describe. Before that it is not in the encounter table at
all, which is what keeps the dex from spoiling the location — see above for the
refusal that holds the rest of the way shut.

## The honest limits

- **The encounter rate per map is never touched**, so a species placed on a map
  with a low rate is genuinely slow to find. `RARITY %` is there for players who
  would rather it were not.
- **Red and Blue give a live surf rate to Routes 19, 20 and 21 and nothing
  else.** Raising a rate is the one thing this mod will not do, so on those two
  versions water placement is nearly unavailable and almost everything lands in
  grass or on the Super Rod instead.
- **The roll layer deliberately ignores any `buckets` list on an encounter
  record**, so another encounter mod's eleventh-and-beyond slots stay
  unreachable on the maps Gen151 touches — which is what they already were
  without a bucket list of their own.

## Compatibility

Red, Blue and Yellow, mod api 2. Requires `engine_internals`, which is the first
thing to switch off if a game update breaks it.
[Gen1Dex](https://github.com/wild1walker/Gen1Dex) 1.3.0 is an optional
dependency and the only thing AREA HINTS needs — 1.4.0 for Mew's sealed screen
to say anything at all; everything else here — the
spawns, the LINK CABLE, the journals, the legendaries — never touches the dex
and runs without it. Derived from the pret disassemblies of Red, Blue and
Yellow, and built on the encounter, merge and hook seams of
[Pokemon Gen1Recomp](https://github.com/bryanthaboi/gen1recomp).
