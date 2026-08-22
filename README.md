# gen1wild-mod-index

A personal gen1recomp mod index. The launcher reads `index.json` directly, so
the whole feed is one static file served over https.

## Feed URL

```
https://raw.githubusercontent.com/wild1walker/gen1wild-mod-index/main/index.json
```

Add it in the launcher under **Find mods → add index source**. `ModIndex`
accepts any https URL ending in `.json` that returns the flat
`{schema_version, count, mods: [...]}` shape.

Two things worth knowing when a mod here shares an id with the community index:

- **Duplicate ids.** Both feeds are cached separately and merged in the UI
  layer, so which entry wins is worth eyeballing in **Find mods** rather than
  reasoning about. A higher `version` generally helps.
- **Cache ordering.** Mod-sync resolves entries from *cached* index data before
  it runs its "add index source" step, so a device that has never opened
  **Find mods** since the feed was added reports the mod missing on its first
  sync. Add the feed and open **Find mods** once on each device before sharing
  a mod list.

## Layout

```
index.json                     generated feed — do not hand-edit
mods/<Author>@<id>/meta.json   one entry per mod, the source of truth
mods/<Author>@<id>/description.md
build_index.py                 regenerates index.json from mods/
```

## Adding a mod

1. Create `mods/<Author>@<id>/meta.json`:

   ```json
   {
     "id": "MOD_ID",
     "title": "Display name",
     "author": "Original author",
     "version": "1.0.0",
     "categories": ["GAMEPLAY"],
     "repo": "https://github.com/owner/repo",
     "github": "owner/repo",
     "downloadURL": "https://github.com/owner/repo/releases/download/v1.0.0/mod.zip",
     "api": 2,
     "profile": "content"
   }
   ```

2. Run `python3 build_index.py` and commit both the entry and `index.json`.

Rules the installer enforces, so the build script checks what it can:

- `id` must match the `id` in the served zip's `manifest.json`, or the
  installer refuses the download. Keep a fork's id identical to upstream's —
  the engine keys enable state, per-version options and mod-sync entries by id.
- `downloadURL` must serve a **flat** zip, with `manifest.json` at the root.
  A GitHub source archive (`/archive/refs/tags/...`) will not work: it nests
  everything under a top-level directory.
- Ids must be unique within this feed.

`python3 build_index.py --check` fails if `index.json` is out of date, which
makes it usable as a pre-commit or CI check.

## Mod entries

| Mod | Version | Notes |
| --- | --- | --- |
| PokéPC Followers (W/Voxel Support) | 0.8.6 | Fork build carrying three follower HP-handling fixes on top of upstream 0.8.3. Drop this entry if the fixes land upstream, rather than leaving a stale duplicate id in circulation. |
