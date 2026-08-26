Hold **B** to run — the same speed FireRed's running shoes give you — and
ride the **BICYCLE** at twice the speed Gen 1 gives it.

## Twice walking, on a button you were not using

Walking in Gen 1 is 16 frames per tile. FireRed's running shoes halve that to
8, and that is what holding B does here — from the first step out of your
bedroom. There is no item to find, no flag to set and nobody to talk to.

Eight frames per tile is not a number picked to feel right. It is a pace this
engine has drawn since the day it booted, because it is exactly what the
**BICYCLE** rides at. So the sprint is not a new motion the game has to learn:
it is the bike's motion, on foot, on a button.

Everything else about a step is untouched. Encounters still roll per step, so
running does not change how often you meet anything. Ledges, warps, collision,
Cycling Road, the boulder push and the turn-in-place delay are all vanilla, and
your follower keeps up on its own.

Nothing else in the overworld reads B, so nothing is being taken away — but if
you would rather keep it clear, `HOLD` moves the sprint to `SELECT`, which the
overworld reads nowhere at all.

| Row | Values | Default |
| --- | --- | --- |
| `SPRINT` | on / off | on |
| `HOLD` | `B` / `SELECT` | `B` |
| `SPRINT SPEED` | `1.5x` / `2x` / `3x` | `2x` |
| `BIKE SPEED` | `VANILLA` / `1.5x` / `2x` / `3x` | `2x` |
| `SPRINT SURFING` | on / off | off |
| `SPRINT ON BIKE` | on / off | off |

The two `off` rows are the FireRed answer: running shoes are a thing you do on
foot, so surfing stays at exactly the speed it has always been until you say
otherwise.

## The bicycle, so it stays worth riding

`BIKE SPEED` puts the **BICYCLE at 4 frames per tile** instead of 8, out of the
box and with nothing held. It is the one default here that departs from vanilla
rather than preserving it, and it exists because the sprint would otherwise
make the bike pointless: Gen 1's bicycle is 8 frames per tile, which is exactly
what a `2x` sprint already gives you on foot.

`2x` restores the ladder — **16 walking, 8 sprinting, 4 riding**, each rung
twice the one before it. `BIKE SPEED: VANILLA` puts Gen 1's 8 back exactly.

This one is game feel rather than FireRed parity, and it is worth being straight
about which. FireRed's bicycle is `MOVE_SPEED_FAST_1` — 8 frames per tile, the
*same constant* its running shoes use — so in FireRed the two really are the
same speed, and the bike is the worse deal: across 425 maps, 85 allow running
but not cycling and **none** allow cycling but not running. So 4 is not
FireRed's ordinary bike speed; it is FireRed's Cycling Road roll
(`MOVE_SPEED_FASTER`), borrowed because it is the speed that game does reach on
a bicycle.

## It does not cost you frames

A movement mod is an easy place to make a game stutter, so this one sits on the
engine's own seam rather than beside it. `Player:stepLength` already asks mods
how long a step should last, through the `movement.speed` hook — the one whose
comment reads *"lets a mod multiply or replace that (running shoes, dash,
etc.)"*. Running shoes is precisely what this is, so nothing is patched,
overridden or polled.

That seam is a cold path. It runs **once per step**, as the step begins, not
once per frame: four to eight calls a second while you are moving, and none at
all while you stand still, sit in a menu or fight a battle. The link allocates
nothing, and the option rows are read from a snapshot rebuilt only when you
change one.

Turned all the way off — `SPRINT: OFF` *and* `BIKE SPEED: VANILLA` — it goes
further and unsubscribes the hook outright rather than returning early inside
it. The engine only builds a context table when some mod is listening, so with
nothing to say this mod costs precisely what it costs uninstalled. Either row
on its own keeps the link, because dropping it would quietly take the other
one's setting with it.

Runs on Red, Blue, Yellow, Gold, Silver and Crystal, and requests no
permissions.
