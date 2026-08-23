# Gen1Wild

A personal mod index for [gen1recomp](https://github.com/bryanthaboi/gen1recomp):
the mods I maintain, one link, updates picked up on their own.

## Adding it in the game

**MODS > FIND MODS**, add the index

```
wild1walker/Gen1Wild
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

## Whose mods are in here

Ones I maintain -- which is not the same as ones I wrote. Some started here.
Others are someone else's mod that I took and tweaked until it did what I
wanted, and those keep the original authors' credit and their own licence:
Gen1Follower is built from Antigravity and gamecorner33's PokéPC Followers,
and Gen1Arena's backdrops come from the Battle Backgrounds Patch FR. Where a
mod started as someone else's, or leans on their art, its description says so
and names who it belongs to.

What this index does not take is listings for mods I have nothing to do with.
Adding an index is an act of trust, and this one is only worth trusting
because the list stays short enough that I can vouch for every line in it --
which I can only do for something I maintain. A wider list is what the
community index is for.

Contributions are the opposite of unwelcome: issues, fixes, art,
translations, ideas. They belong in the mod's own repo, behind the **source**
link on its card, and I would rather have them than not.

## What is in here

Metadata, and nothing else. No mod is vendored: every entry points at a
release in that mod's own repo.

```
mods/<Author>@<mod id>/
  meta.json        required
  description.md   optional — the long form the card links to
  thumbnail.png    optional — a square icon; tools/make_icons.py draws them
site/data/index.json   generated; this is the feed
```

## Adding one of mine

Make the folder, write `meta.json`, push. The rest happens on its own. It is
written down because I forget, not because the index is open -- but it is also
the shape to match if you are working on one of my mods and the entry needs to
change with it.

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

## The icons

Every entry's `thumbnail.png` is a square 512x512 icon drawn by

```sh
python3 tools/make_icons.py            # redraw every icon
python3 tools/make_icons.py gen1arena  # ... or just the ones named
```

Each one is pixel art on a 32x32 grid scaled 16x with no resampling, so a
drawn pixel stays a hard-edged block, and nothing is read off disk -- no font,
no source image -- so any machine redraws the same bytes. A new mod gets an
icon by adding a draw function to that file and listing it in `ICONS` against
the mod's `id` -- an entry's folder carries its author and an author can
change, an id cannot. Run without arguments the script names any folder it has
no icon for and exits non-zero, so an entry cannot quietly go without one.

## Rebuilding the feed

```sh
python3 tools/build_index.py                    # rebuild
GITHUB_TOKEN=... python3 tools/build_index.py   # ... without the 60/hour limit
```

CI does it on every push that touches `mods/` or `tools/`, nightly at 05:17
UTC, and on demand from the Actions tab. A rebuild that changes nothing keeps
the previous `generated_at` and commits nothing, so a quiet night stays quiet.

## Where it is served from

The launcher tries the Pages URL first and falls back to the raw file on
`main`:

```
https://wild1walker.github.io/Gen1Wild/data/index.json   (Pages)
https://raw.githubusercontent.com/wild1walker/Gen1Wild/main/site/data/index.json
```

`.github/workflows/pages.yml` publishes `site/` to Pages, and Pages is on, so
the first URL answers. Turning it on was a one-time manual step —
**Settings > Pages > Build and deployment > Source: GitHub Actions** — because
creating a Pages site needs admin rights on the repository and the Actions
token does not have them; the workflow keeps it up to date from here on
without being touched.

It has to be the **GitHub Actions** source rather than a branch: branch
publishing only offers the repo root or `/docs`, and the feed lives in
`site/`. What is served is whatever the job uploads, so `site/index.html`
becomes the page at the root.

It deploys after **Build index** as well as on a push, because that job
commits a regenerated feed and the deploy has to follow it rather than race
it. The fallback stays a fallback: if Pages is ever off or mid-deploy, the raw
file on `main` still answers.

This repo was `wild1walker/gen1wild-mod-index` before it was renamed, and an
index anyone already added is stored as whatever they typed. The old slug keeps
working: GitHub redirects the repo, and `raw.githubusercontent.com` serves the
old path unchanged, so the fallback URL still answers. The Pages URL is the one
that moves with a rename — the old one stops answering, so a launcher holding
the old slug quietly lands on the mirror every time instead of the CDN.
Re-adding the index as `wild1walker/Gen1Wild` puts it back on Pages.

## How this is written

Worth saying plainly, because it changes how much weight to give any of it:
none of this comes from expertise. The code here, and in the mods this index
lists, is either borrowed from other people's work or vibe coded — generated,
then baby-sat by me through a long run of trial and error until it did what it
was supposed to. What is actually mine is the testing, the fixing, and the
call on what ships.

Two things follow. Credit for the borrowed parts stays with whoever earned it,
named in the description of the mod that uses it. And a bug report is worth
more here than on a project with someone's expertise behind it — trial and
error is how everything else got found, so if something breaks, tell me.

## Licence

The index metadata is CC0 — take it. Each mod is licensed by its own author.
