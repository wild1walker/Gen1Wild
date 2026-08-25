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

Two things are added on top. Vanilla refuses to open the dex side menu at all on
an entry you have never seen, which is exactly backwards for a mod whose job is
helping you find the ones you have never met — so an undiscovered entry opens,
with AREA and QUIT on it and nothing that would hand over the dex paragraph you
have not earned. And the map gets a line under it saying how to get there, for
**all 151** rather than only the ones this mod placed: the nests say *where*,
and they cannot say *in the grass, around level ten, and rare*, which is the
half you actually need.

A placed POKéMON is described from the same rows the roll layer uses, so its
hint cannot drift from its spawn. Everything else is read straight out of the
live encounter tables, and anything in no table at all falls back to the
evolution table — `EVOLVE ODDISH / AT LV21`, `LINK CABLE / ON KADABRA`. Nothing
there is invented. Turn **AREA HINTS** off and the dex is exactly what the
cartridge shipped.

Both screens are wrapped rather than replaced, so a dex-replacing mod that calls
through — [Gen1Dex](https://github.com/wild1walker/Gen1Dex) does — keeps
working, and one that does not simply never grows the extra AREA rather than
growing a broken one. This is the one part of the mod that needs
`engine_internals`, which is why it wears a **PATCHES ENGINE CODE** badge.

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
| AREA HINTS | on | AREA on undiscovered entries, and the line under the map |

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
all, so the AREA screen cannot spoil the location, and there is no caption
either — a caption would give the basement away more precisely than a nest ever
could.

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
thing to switch off if a game update breaks it. Derived from the pret
disassemblies of Red, Blue and Yellow, and built on the encounter, merge and
hook seams of [Pokemon Gen1Recomp](https://github.com/bryanthaboi/gen1recomp).
Tested against a vanilla install and against Gen1Dex.
