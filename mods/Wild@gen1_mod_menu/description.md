# Gen1ModMenu

The in-game **MODS** screen, redrawn. The mod list gets a status column,
sorting and filters; the per-mod **OPTIONS** page gets eleven rows on screen
instead of four, each with its value beside it and a line underneath saying
what it accepts.

Nothing about how the manager *behaves* changes. Enabling and disabling,
dependency closures, staged changes, apply-and-restart, profiles and safe
mode are all still the engine's — this mod draws them.

## The options page

Vanilla renders it through the engine's shared option widget: four bordered
20×4 boxes, the label on one line and the value on the next, four options
visible at a time. A mod with seven rows is two pages, and there is no room
to say what any of them do.

Here every option is one line — label left, value right — so eleven fit,
under the mod's name and version. Below them, a help line for whichever row
the cursor is on, read straight off the schema.

| Row type | Help line |
| --- | --- |
| toggle | `ON / OFF` |
| choice | every choice label, `ONCE / N BEEPS / VANILLA` |
| number | the range, `1-8`, and the step when it is not 1 |
| text | `UP TO 12 CHARS` |

A `.` beside a value marks a row that differs from the default its author
shipped, and **RESET DEFAULTS** at the bottom puts every one of them back.

There is no description field in the engine's option schema, so the help line
says what the row *accepts* rather than inventing prose the author never
wrote.

## The mod list

A mod that is enabled and running carries **no mark at all** — a column
reading `ON` down the whole screen is not information, and leaving it blank
hands three more glyphs to every name. The marks are the exceptions:

| Column | Reads |
| --- | --- |
| *(blank)* | enabled and running |
| `OFF` | disabled |
| `STGD` | changed, waiting on a restart |
| `ERR` | failed to load |
| `BLKD` | a dependency is not satisfied |
| `SKIP` | enabled and fine, but not for this game |

The same six appear as a legend on the `ERRORS` tab whenever there is nothing
wrong to show there, and the full word is always one A-press away on the
mod's own detail screen.

## Options

| Option | Default | Notes |
| --- | --- | --- |
| `STYLE` | `MODERN` | `VANILLA` hands every screen back to the engine's own renderer. Read every frame, so it lands without leaving the screen. |
| `SORT BY` | `CATEGORY` | Or `NAME`, `ENABLED`, or `PROBLEMS` — which floats errored and blocked mods to the top. |
| `HIDE OFF` | off | Drop disabled mods from the list. |
| `WITH OPTIONS` | off | Show only the mods that have something to configure. |
| `HELP LINE` | on | Off gives its row back to the list, making it twelve. |
| `RESET ROW` | on | Show `RESET DEFAULTS` on each mod's options page. |
| `KEEP CURSOR` | on | Reopen the manager on the row you left it on. |

Neither filter can hide Gen1ModMenu itself — both are set from its own
options page, and that page is reached through the list they filter.

## Two things it fixes

- **The options page on Gold.** The engine draws it through a module its own
  loader lists as Gen 1 only, which "paints Red's chrome over Gold's options
  screen, whose layout is one 18×16 box rather than four 20×4 ones". Drawing
  the rows here makes the page right on Gold as well.
- **A detail screen that ran off the bottom.** Vanilla starts the action rows
  at tile 11 and draws one per line, so a mod carrying all nine of them puts
  its last row at tile 19 of an 18-tile screen. The rows are pinned to the
  bottom here and the description takes what is left.

## Getting out of the way

This is the one screen a player uses to switch off a mod that is
misbehaving, so there are three independent ways back to the vanilla one:
`STYLE: VANILLA`; a renderer that throws, which is logged once and
demoted to the engine's own draw for the rest of the visit; and the engine's
own screen builder, which falls back to its builtin manager if this mod's
screen cannot be constructed at all.

## Compatibility

- **Link play** — `affects_link: false`. This only draws a menu.
- **Gen 2** — works, and fixes the options page there.
- **Your saves** — nothing is stored in them. The mod's own settings are
  option rows, which is what lets them work on the title screen too, before a
  playthrough has been adopted.

Requests `engine_internals`, because replacing the manager's drawing means
reaching the engine's own manager module by name to keep its logic. Nothing
is patched in place: the substitutions land on one screen instance, built
fresh each time it is opened. Contains no ROM-derived content.
