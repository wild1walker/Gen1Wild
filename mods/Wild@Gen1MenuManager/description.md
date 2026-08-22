# Gen1 Menu Manager

Rearrange the START menu and the Pokémon Center PC menu: reorder the rows,
hide the ones you never touch, and pin field items and moves so they get a row
of their own once you own them.

Each menu keeps its own arrangement. Open the editor from the START menu and
you are editing the START menu; open it from a PC and you are editing that.

## Getting in

Three ways, and no arrangement can close all of them:

- press **SELECT** with the START menu or a PC menu open
- pick **MENU MGR**, the row on either menu
- pick **MENU MANAGER** on the OPTION screen

SELECT is free in both menus — the START menu watches only up, down, START, B
and A, and the shared menu widget reads up, down, A, B and START — so the
shortcut takes nothing away from the vanilla controls.

## The buttons

| Press | What happens |
| --- | --- |
| Up / Down | Moves the cursor |
| A | Grabs the row, then A again to drop it |
| Up / Down while grabbed | Moves the row |
| SELECT | Shows / hides a row, or switches a pin on and off |
| B | Leaves |

The right-hand column reads `ON`, `OFF`, `PIN`, `LOCK` (a row that cannot be
hidden), or `----` for a pin you have not unlocked yet.

## What can be pinned

| Pin | Appears once |
| --- | --- |
| TOWN MAP | the TOWN MAP is in the bag |
| BICYCLE | the BICYCLE is in the bag |
| OLD / GOOD / SUPER ROD | that rod is in the bag |
| FLY | a party member knows FLY and you hold the THUNDERBADGE |
| CUT, SURF, STRENGTH, FLASH | a party member knows it and you hold its badge |
| DIG, TELEPORT | a party member knows it |

ITEMFINDER and the POKé FLUTE are deliberately absent. Their behaviour lives
inside the bag's own result dispatch, which is file-local and exported
nowhere; pinning them would mean duplicating engine logic that can drift out
of step. They stay in the bag.

## Options

| Option | Default | Notes |
| --- | --- | --- |
| `SELECT OPENS` | on | Off locks the MENU MGR row, since it becomes the only way in. |
| `MENU ROW` | on | Shows MENU MGR on the START menu. |
| `PC ROW` | on | Shows MENU MGR on the PC menu. |
| `HIDE UNUSABLE` | on | Drops a pin whose action cannot run right now — the BICYCLE indoors, SURF facing dry land. |

## What it does with rows it did not make

- **Other mods' rows are arrangeable too.** The hook runs outermost, so QUESTS,
  ACHIEVEMENTS, NG PLUS and anything else appended by another mod can be moved
  and hidden like a vanilla row.
- **New rows are never lost.** A row the saved order does not mention — a mod
  installed since, or one that only appears with a party — is appended in
  engine order rather than dropped.
- **The PC's exit is never at risk.** The engine appends LOG OFF *after* the
  hook this mod uses, so it cannot be reordered or hidden by anything.

## Worth knowing

- **Layouts follow the save,** and seed from an installation-wide template, so
  a new file starts from your last arrangement instead of from scratch. The
  two menus are stored separately.
- **Editing a PC menu takes effect immediately.** The PC session stays open
  underneath, so the menu is rebuilt and its box resized when you leave.
- **Rows are keyed by label,** except three cases: rows carrying a stable id
  are keyed by that instead (Gold's PC rows do), and the START menu's
  trainer-card row and the PC's `<name>'s PC` row are matched against your
  player name.
- **A renamed row loses its place once.** The box PC becomes BILL'S PC when you
  meet Bill, and a translation mod rewrites everything. A key that no longer
  matches falls to the end of the menu, where you can put it back. Nothing is
  ever dropped.
- **With HIDE UNUSABLE on, a pin can still show when it cannot fire.**
  Readiness is judged when you pick the row rather than when it is drawn;
  selecting one that cannot run is a silent no-op with a line in the log.

## Compatibility

- **Link play** — `affects_link: false`. This only rearranges menus.
- **Gen 2** — works. Gold's PC rows carry stable ids, which this keys on.
- **Other menu mods** — the hook runs outermost and reorders the list it is
  handed, so a mod that appends a row keeps it; the row just becomes movable.

Requests **no permissions**, and contains no ROM-derived content.
