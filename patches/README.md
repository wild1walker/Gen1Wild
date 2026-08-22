# patches

Fixes carried against **someone else's** mod. Nothing in here is part of the
index feed — `tools/build_index.py` only reads `mods/`, so this folder is
metadata for me, not for the launcher.

A patch lands here rather than becoming a `mods/` entry because an entry would
publish a modified build of another author's mod under their manifest id. The
launcher installs by id, so anyone who added this index would get my build in
place of theirs. Fixes go upstream; this folder just remembers what is
outstanding while they do.

Name a patch `<mod id>-<upstream version>-<short description>.patch` and put
what was verified in its header, so the claim travels with the diff.

| Patch | Mod | Upstream | Version | Status |
|---|---|---|---|---|
| `modern_bag-1.6.0-machine-label-width.patch` | Modern Bag | [FAFF0x/gen1recomp](https://github.com/FAFF0x/gen1recomp) | 1.6.0 | Not yet reported upstream |

Status is one of *not yet reported upstream*, *reported*, *merged upstream*, or
*carried locally* — upstream declined or never answered, and the patch is
reapplied on each release.
