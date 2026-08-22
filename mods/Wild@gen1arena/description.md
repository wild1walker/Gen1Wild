# Gen1Arena

Battles happen somewhere. A wild encounter in Viridian Forest gets trees
behind it, a gym trainer gets the gym, a hooked Goldeen on Route 12 gets open
sea, and Lance gets Lance's own scene. The white field is gone.

Works in both layouts: **OG** at 160x144 and **WIDE** at 304x144. Nothing is
resampled — one backdrop pixel is one sprite pixel in both.

## How a backdrop is chosen

Two questions, in order: **where are you**, and **how did the battle start**.

| Where | What you get |
| --- | --- |
| Route grass, wild | Grass |
| Route, trainer | Route |
| Viridian Forest | Forest |
| Any cave | Cave |
| A gym's trainers | Gym Trainer |
| A gym leader | that gym, in their town's colour |
| A town | that town, roofs and all |
| Surfing or fishing, open coast | Sea |
| Surfing or fishing, inland | Lake |
| Surfing or fishing, inside a cave | Underwater |
| Pokemon Tower | Indoors, drained to GRAYMON |
| Giovanni, the Elite Four, the Champion | one scene each, their own |

A boss's scene outranks the room, and so does water: Agatha's room carries the
tower's tileset and she still gets Agatha's backdrop, and a fish hooked on a
route does not come up against grass.

## Towns are their own colour

The eleven Kanto cities differ in exactly one way in the GBC overworld — the
roofs change and nothing else does. So that is what the town backdrops do,
using the roof pairs out of the engine's own `palettes_gbc.lua` rather than an
invented tint. Cerulean is blue, Fuchsia is magenta, Cinnabar is red. Gyms
follow their town, walls only: the floor, the court lines and the Poke Ball
are the same everywhere, so the ball reads as the same ball in every gym.

Interiors are untouched. A Pokemon Center looks like a Pokemon Center in every
city, because it does in the game.

## Options

| Option | What it does |
| --- | --- |
| `BACKDROPS` | On or off. |
| `DIAGNOSTIC` | Logging, plus a startup audit that walks every map in the game and writes what each one resolves to. Changes nothing on screen. |
| `FIELD TEST` | Paints the battlefield flat magenta instead of the backdrop — tells "the patch never ran" apart from "the patch ran and the image was lost". |

## Compatibility

- **Link play** — `affects_link: false`. Purely presentational; it draws a
  picture and touches no battle state.
- **Permissions** — requests **`engine_internals`**, and genuinely needs it:
  it patches `BattleState.drawClassic`, `WideBattle.draw` and
  `BattleState.newWild`. The draw patches match the field fill by geometry and
  fall back to vanilla rather than crashing if the engine moves underneath
  them.
- **Palette modes** — backdrops bypass the palette bake, so they do not shift
  with COLORS. Built for **ADVANCED**; the other modes put full-colour art
  behind four-shade sprites.
- **Dark scenes** — Gen 1 back sprites use the white field for their light
  shades, so on Cave and Forest your own mon can read as a silhouette.

## Art credit — required

**None of the art was drawn for this mod.** Every backdrop comes from the
**Battle Backgrounds Patch FR** for Pokemon FireRed, and its authors ask for
credit wherever it is used:

> **LibertyTwins · princess-phoenix · carchagui · aveontrainer · WesleyFG ·
> kWharever · worldslayer608 · knizz**

What the mod adds is the selection logic and three mechanical passes — a
chroma correction into the GBC palette range, a crop to the engine's two
layouts, and the per-town roof recolours. The composition, linework and colour
choices in every scene are theirs. Carry those names anywhere the art goes.

Parts of that pack are original fan art and parts are FireRed-derived, and the
files do not distinguish between the two — so unlike the rest of this index,
this one is **not** MIT and ships no blanket licence. The mod's own code is
Wild's; the art is credited, not relicensed.
