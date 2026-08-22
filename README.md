# gen1wild-mod-index

Wild's personal index of Gen 1 Recomp mods — mods written from scratch, and
fixes carried against someone else's mod.

This is a working index, not a distribution channel. Nothing here is a release
feed and nothing links to it automatically. For publishing a mod so the launcher
can install and update it, use the community index instead.

## My mods

| Mod | ID | Version | Repo | Notes |
|---|---|---|---|---|
| Gen1AutoSave | `gen1autosave` | 1.2.1 | [wild1walker/Gen1AutoSave](https://github.com/wild1walker/Gen1AutoSave) | Community-index submission still open, not merged |

## Patches to other people's mods

One row per fix carried against an upstream mod. "Upstream version" is the
release the patch was written and verified against — if upstream moves, re-check
the anchor before reusing it.

| Mod | Upstream | Upstream version | Change | Status | Fix |
|---|---|---|---|---|---|
| Modern Bag | [FAFF0x/gen1recomp](https://github.com/FAFF0x/gen1recomp) | 1.6.0 | Machine-label width — TM/HM labels ran past the right edge of the item window | Not yet reported upstream | [patch](patches/modern_bag-1.6.0-machine-label-width.patch) · [build](https://github.com/wild1walker/gen1recomp/commit/e9c518c5230db6f0adc1c3a2bde650c6813417ae) |

## Adding an entry

Write mods you authored into **My mods**, and fixes against someone else's mod
into **Patches**. Both tables sort by mod name.

For a patch, drop the diff in `patches/` named
`<mod id>-<upstream version>-<short description>.patch` and link it from the
row. Keep **Status** honest — one of *not yet reported upstream*, *reported*,
*merged upstream*, or *carried locally* (upstream declined or never answered,
and the patch is reapplied on each release).

Record what you actually verified in the patch's own header comment rather than
in the table, so the claim travels with the diff.
