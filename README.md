# gen1wild mod index

A personal mod index for [gen1recomp](https://github.com/bryanthaboi/gen1recomp).
One link, every mod in it, updates picked up on their own.

## Adding it in the game

**MODS > FIND MODS**, add the index

```
wild1walker/gen1wild-mod-index
```

The repo page URL, the Pages root and the feed URL itself all resolve to the
same source, so any of them works in that box.

Adding an index is a deliberate act of trusting whoever publishes it. A
listing buys a mod no trust it would not otherwise have: installing from a
card runs the same import an **Import mod .zip** does, and the installer still
refuses an archive whose manifest id is not the one being installed.

## When a mod here is also in the community index

- **Duplicate ids.** Both feeds are cached separately and merged in the UI
  layer, so which entry wins is worth eyeballing in **FIND MODS** rather than
  reasoning about. A higher `version` generally helps.
- **Cache ordering.** Mod-sync resolves entries from *cached* index data before
  it runs its "add index source" step, so a device that has never opened
  **FIND MODS** since the feed was added reports the mod missing on its first
  sync. Add the feed and open **FIND MODS** once on each device before sharing
  a mod list.

## What is in here

Metadata, and nothing else. No mod is vendored: every entry points at a
release in that mod's own repo.

```
mods/<Author>@<mod id>/
  meta.json        required
  description.md   optional — the long form the card links to
  thumbnail.png    optional — 16:9 reads best on a card
site/data/index.json   generated; this is the feed
```

## Adding a mod

Make the folder, write `meta.json`, push. The rest happens on its own.

```jsonc
{
  "id": "your_mod",              // must equal the mod's manifest.json id
  "title": "Your Mod",
  "author": "Wild",
  "summary": "One line for the card.",
  "version": "1.0.0",
  "categories": ["GAMEPLAY"],    // GAMEPLAY CONTENT BALANCE ART AUDIO UI QOL
                                 // TRANSLATION TOTAL_CONVERSION LIBRARY TOOL OTHER
  "tags": ["something", "else"],
  "repo": "https://github.com/wild1walker/YourMod",
  "github": "wild1walker/YourMod",
  "api": 2,
  "game_version": ">=0.0.0-dev <1.0.0",
  "profile": "content",
  "license": "MIT"
}
```

`id`, `title`, `author`, `version`, `categories` and `repo` are required; the
build fails and names anything missing.

Three rules the installer enforces, so an entry is worth checking against them
before it goes in:

- `id` must match the `id` in the served zip's `manifest.json`, or the
  installer refuses the download. Keep a fork's id identical to upstream's --
  the engine keys enable state, per-version options and mod-sync entries by id.
- The zip must be **flat**, with `manifest.json` at the root. A GitHub source
  archive (`/archive/refs/tags/...`) will not work: it nests everything under a
  top-level directory. `modkit.py add-release-workflow` produces the right
  shape.
- Ids must be unique within this feed.

**Versions look after themselves.** With `github` set, the nightly rebuild
reads that repo's Releases, takes the newest one with a `.zip` asset, and puts
it on the card — so tag a release in the mod's own repo and this index catches
up without being touched. The `version` in `meta.json` is only the fallback
shown when no release can be resolved.

Opt out with `"automatic_version_check": false` and give the entry its own
`"downloadURL"` pointing at an installable `.zip`.

## Rebuilding the feed

```sh
python3 tools/build_index.py                    # rebuild
GITHUB_TOKEN=... python3 tools/build_index.py   # ... without the 60/hour limit
```

CI does it on every push that touches `mods/` or `tools/`, nightly at 05:17
UTC, and on demand from the Actions tab. A rebuild that changes nothing keeps
the previous `generated_at` and commits nothing, so a quiet night stays quiet.

## GitHub Pages is optional

The launcher tries the Pages URL first and falls back to the raw file on
`main`, so the index works with Pages switched off. Turning it on for `/site`
on `main` makes the first URL answer, and serves the small page in
`site/index.html` that lists what is in here.

## Licence

The index metadata is CC0 — take it. Each mod is licensed by its own author.
