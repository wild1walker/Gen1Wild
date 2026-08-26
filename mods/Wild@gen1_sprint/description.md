Hold **B** to run. The same speed FireRed's running shoes give you.

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
| `SPRINT SPEED` | `2x` / `1.5x` / `3x` | `2x` |
| `SPRINT SURFING` | on / off | off |
| `SPRINT ON BIKE` | on / off | off |

The two `off` rows are the FireRed answer: running shoes are a thing you do on
foot, so surfing and cycling stay at exactly the speeds they have always been
until you say otherwise.

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

`SPRINT: OFF` goes further and unsubscribes the hook outright rather than
returning early inside it. The engine only builds a context table when some mod
is listening, so switched off this mod costs precisely what it costs
uninstalled.

Runs on Red, Blue, Yellow, Gold, Silver and Crystal, and requests no
permissions.
