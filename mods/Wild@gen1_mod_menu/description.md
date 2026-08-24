# Gen1ModMenu

The in-game **MODS** screen, redrawn. The mod list gets a status column,
sorting and filters; the per-mod **OPTIONS** page gets a help line, a
`CHANGED` marker and a `RESET DEFAULTS` row — all drawn in the same
framed-card idiom the game's own OPTION screen uses.

Nothing about how the manager *behaves* changes. Enabling and disabling,
dependency closures, staged changes, apply-and-restart, profiles and safe
mode are all still the engine's — this mod draws them.

## The look

Both list screens use the game's own **OPTION-screen idiom** — the same shape
`TEXT SPEED` and `BATTLE ANIMATION` are drawn in: full-width framed cards down
the screen, the label on the first line inside each and its value indented on
the second.

A card holds two whole lines, of 17 and 16 glyphs, so every mod name and every
option value is shown in full — neither has to share a row with the other.
All three tabs — `MODS`, `PROF` and `ERRS` — are drawn this way, and a row
with no readable label (a profile saved without a name) reads `(NO NAME)`
rather than drawing an empty box.

The list is banded the way **Gen1BillsBox** bands its storage screen: a
header box across the top naming the page you are on, with the position count
beside it; the rows under it; and an info box at the bottom naming what the
cursor is on. Left and right move between `MODS`, `PROFILES` and `ERRORS`,
and wrap at both ends.

A list row is one thing — a name — so it is a single-line box, and four fit
between the two bands. An option row is two things, a label and its value,
which is why a mod's options page keeps the four-tile cards the game's own
OPTION screen uses and the list does not.

On the mod list the second line carries the **category** on the left and the
**status** on the right. A mod that is enabled and running shows no status at
all; the column is for the exceptions.

| Status | Reads |
| --- | --- |
| *(blank)* | enabled and running |
| `OFF` | disabled |
| `STGD` | changed, waiting on a restart |
| `ERR` | failed to load |
| `BLKD` | a dependency is not satisfied |
| `SKIP` | enabled and fine, but not for this game |

The full word is always one A-press away, on the mod's own detail screen —
`ENABLED`, `DISABLED`, `FAILED`, `BLOCKED`, `NOT THIS GAME`.

There are **no control hints** on any screen: A chooses, B goes back and the
d-pad moves, the same as every other menu in the game.

Four mods fit on a screen, which is the price of the layout — and why the
position counter, the sorts and the filters are all there.

## The options page

The second line of each card is the value, with `CHANGED` right-aligned
against it on any row moved off the author's default. Below the cards, a help
line for whichever row the cursor is on, read off the schema:

| Row type | Help line |
| --- | --- |
| toggle | `ON / OFF` |
| choice | every choice label, `ONCE / N BEEPS / VANILLA` |
| number | the range, `1-8`, and the step when it is not 1 |
| text | `UP TO 12 CHARS` |

The last card is **`RESET DEFAULTS`**, which puts every row back to what its
author shipped. That row is the engine's own — it appends one to every
options page — and all this mod adds to it is the help line.

There is no description field in the engine's option schema, so the help line
says what the row *accepts* rather than inventing prose the author never
wrote.

## The list menu

**START** on the `MODS` tab opens a menu: the focused mod's `ENABLE` /
`DISABLE`, the four sort orders with the active one bracketed, and the two
filters showing their own state.

**SELECT** applies staged changes — what `START` used to do. The two keys
traded jobs because the manager has no spare ones, and nothing was lost in
the trade: vanilla's `SELECT` quick-toggle is the menu's first row with the
cursor already on it, and `SELECT` reaches `APPLY & RESTART` through the
engine's own handler, so safe mode and the `NO CHANGES` notice are unchanged.

Only on the `MODS` tab — `PROFILES` spends both keys itself, the `ERRORS` tab
keeps `START` as a second way to `APPLY`, and the detail screen keeps
`SELECT` for toggling the mod it is showing.

## Outside the manager

Two smaller edits, both switched off by `STYLE: VANILLA` along with
everything else.

- **The START menu's row reads `MOD MENU`.** The engine already puts one
  there and labels it `MODS`; this renames that row rather than adding a
  second beside it, matched on the label the engine would have produced so a
  translation is still recognised, and at the default hook priority so
  Gen1MenuManager can still move, hide or pin it.
- **`CANCEL` is gone from the game's own OPTION screen.** It was never one of
  the rows — the engine appends it after the rows hook and draws it as the
  fixed bottom line — and it is not the only exit: B and START both leave
  that menu, with the same sound and the same pop. The wrapper that removes
  it never touches input, so it can misplace the cursor but cannot take away
  the way out. **Gen 1 only**; Gold's options screen is a different screen
  with a different layout and is left alone.

## Options

| Option | Default | Notes |
| --- | --- | --- |
| `STYLE` | `MODERN` | `VANILLA` hands every screen back to the engine's own renderer. Read every frame, so it lands without leaving the screen. |
| `SORT BY` | `CATEGORY` | Or `NAME`, `ENABLED`, or `PROBLEMS` — which floats errored and blocked mods to the top. |
| `HIDE OFF` | off | Drop disabled mods from the list. |
| `WITH OPTIONS` | off | Show only the mods that have something to configure. |
| `HELP LINE` | on | Off gives its row back to the list, making it twelve. |
| `START ROW` | on | Label the START menu's row `MOD MENU` instead of `MODS`. |
| `HIDE CANCEL` | on | Drop `CANCEL` from the game's own OPTION screen (Gen 1). |
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
