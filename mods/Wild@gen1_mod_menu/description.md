# Gen1ModMenu

The in-game **MODS** screen, redrawn to look like the rest of the game.

Same framed cards the OPTION screen uses for `TEXT SPEED` and `BATTLE
ANIMATION`: the name on one line, its value on the next, so nothing is
squeezed or abbreviated. Every mod name and every option value is shown in
full.

## What it adds

- **A status column**, for the exceptions only. A mod that is enabled and
  running says nothing; one that is off, staged for a restart, errored,
  blocked or not-for-this-game says which.
- **Sorting and filters**, by category, name, enabled, or problems-first, and
  filters for hiding disabled mods or showing only the ones with something to
  configure.
- **A help line** on every options page, saying what the row you are on
  actually accepts.
- **A `CHANGED` marker** on any row you have moved off its author's default.
- **`RESET DEFAULTS`**, to put a mod's options back the way it shipped.

Nothing about how the manager *behaves* changes. Enabling, disabling,
dependencies, staged changes, apply-and-restart, profiles and safe mode are
all still the engine's, and this mod just draws them.

## It also fixes two things

The options page on Gold, which the engine was drawing with Red's chrome over
Gold's layout. And a mod detail screen that ran off the bottom of the screen
when a mod carried enough action rows.

## Getting out of the way

This is the one screen you use to switch off a mod that is misbehaving, so
there are three separate ways back to the vanilla one: `STYLE: VANILLA`, an
automatic fall back if the drawing ever fails, and the engine's own builtin
underneath all of it.

## Worth knowing

Link play is unaffected, it works on Gen 2, and nothing is stored in your
saves. Contains no ROM-derived content.
