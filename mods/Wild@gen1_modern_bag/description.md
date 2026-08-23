Seven modern pockets over the vanilla Bag: FAVORITES, MEDICINE, BALLS, TM HM,
BATTLE, KEY ITEMS and OTHER, sorted automatically, with Favorites, pinned
items, quick search, TM/HM filtering and move information, and no carrying
limit on item types or stack sizes.

Originally by **FAFF0x**, in [gen1recomp](https://github.com/FAFF0x/gen1recomp)
as **Modern Bag**. This is Wild's derivative, listed here under Wild because
the build and the fix below are Wild's; the mod itself is FAFF0x's, and it
stays MIT under their notice. It is an independent parallel project, not
endorsed by them and not a replacement or successor to Modern Bag.

## What is different from upstream 1.6.0

One constant. Long TM/HM labels rendered past the right edge of the item
window because the truncation helper was budgeted for 15 characters and the
drawable run is 13: the window's inner right edge lands near x=152, names are
drawn from x=48 to leave the cursor its column, and 104px at 8px a glyph is 13.

Because the helper only truncates a label *longer* than its budget, a
15-character label went through untouched and clipped mid-word, and a
17-character one was cut to 15 -- putting the ellipsis itself off-screen, so
the label looked whole and had simply lost its tail.

| Label | Upstream 1.6.0 | Here |
|---|---|---|
| `TM01 MEGA PUNCH` | untruncated, clips to `PUNC` | `TM01 MEGA PU.` |
| `TM45 THUNDER WAVE` | cut to 15, `.` off-screen | `TM45 THUNDER.` |

The unmarked budget is 13 and the marked one 9, keeping upstream's
four-character allowance for the `P` / `F` / `PF` row markers. Everything else
is upstream's, unchanged.

The same fix is carried as a standalone diff in this index's `patches/` folder,
against Modern Bag's own id, for anyone who would rather patch upstream than
install this.

## Mod id

This build uses the id `gen1_modern_bag` rather than upstream's `modern_bag`.
The engine keys enable state, per-version options and mod-sync entries by id,
so **saved Favorites, pinned items and sort preferences do not carry over** --
they start fresh and need setting again. Item stacks live in the save file and
are untouched.

The id had to move. Installing by id means an entry keeping `modern_bag` would
serve this build in place of FAFF0x's to anyone who added this index, which is
not a call this index makes for someone else's mod. The `_G` dispatch,
unlimited-inventory and move-info patch keys are namespaced to match, so the
two cannot quietly share dispatch state through globals.

The manifest declares `"conflicts": ["modern_bag"]`. Both decorate the same
`src.ui.BagMenu` and double-patch it if enabled together -- run one or the
other.

## Compatibility

**Gen1 Modern UI** is optional. With 0.8.2 or newer enabled, the Bag uses its
pocket-aware presenter and the search keyboards render as real key grids
through the `gen1ModernUi` contract (`apiVersion = 1`). Without it, the Bag
keeps its 160x144 presentation and behaves identically.

Item effects are never reimplemented: the mod wraps the vanilla BagMenu, so
items are used, consumed, taught, thrown and validated by the engine's own
menu, in battle as well as the overworld.
