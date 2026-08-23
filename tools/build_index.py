#!/usr/bin/env python3
"""Build site/data/index.json: the feed gen1recomp's MODS > FIND MODS tab reads.

Add the index in the game as

    wild1walker/Gen1Wild

which src/mods/ModIndex.lua resolves to

    https://wild1walker.github.io/Gen1Wild/data/index.json   (Pages)
    https://raw.githubusercontent.com/wild1walker/Gen1Wild/main/site/data/index.json

the second being the mirror it falls back to when the first fails -- which is
also what makes this feed work with Pages switched off entirely.

An index is metadata only.  Nothing here vendors a mod: every entry points at
a release in the mod's own repo, and installing from a card runs the same zip
import "Import mod .zip" does.

Each mods/<Author>@<id>/ folder holds:

    meta.json        required -- id, title, author, version, categories, repo
    description.md   optional -- the long form the card links to
    thumbnail.png    optional -- a square icon, drawn by make_icons.py

Releases are resolved from GitHub so a listing does not go stale: tag a
release in the mod's own repo and the nightly rebuild picks it up.  Set
"automatic_version_check": false on an entry to opt out and rely on its own
downloadURL instead.

    python3 tools/build_index.py          # rebuild the feed
    GITHUB_TOKEN=... python3 tools/build_index.py   # ... without rate limits
"""

import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODS = ROOT / "mods"
FEED = ROOT / "site" / "data" / "index.json"

OWNER, REPO = "wild1walker", "Gen1Wild"
RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main"

SCHEMA_VERSION = 1
REQUIRED = ("id", "title", "author", "version", "categories", "repo")

# the launcher's own vocabulary, in its own order; the panel shows the ones
# the feed's mods actually use and ignores the rest
CATEGORIES = [
    "GAMEPLAY", "CONTENT", "BALANCE", "ART", "AUDIO", "UI",
    "QOL", "TRANSLATION", "TOTAL_CONVERSION", "LIBRARY", "TOOL", "OTHER",
]

SEMVER_TAG = re.compile(r"^v?(\d+\.\d+\.\d+(?:[-+].*)?)$")


def api(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{OWNER}-mod-index",
    })
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def pick_zip(release, mod_id):
    """The asset to install: the mod's own name first, any .zip after it."""
    zips = [a for a in release.get("assets", [])
            if str(a.get("name", "")).lower().endswith(".zip")]
    if not zips:
        return None
    named = [a for a in zips if mod_id.lower() in str(a["name"]).lower()]
    a = (named or zips)[0]
    return {"name": a["name"], "url": a["browser_download_url"],
            "size": a.get("size")}


def version_of(release):
    tag = str(release.get("tag_name") or "")
    m = SEMVER_TAG.match(tag)
    if m:
        return m.group(1)
    return str(release.get("name") or tag or "")


def resolve_releases(entry):
    """-> (latest, update_check, downloads, first_release, last_release)."""
    slug = entry.get("github")
    if not slug:
        # nothing to check; an entry can still ship a fixed downloadURL
        return None, ("pending" if entry.get("downloadURL") else "off"), None, None, None
    if entry.get("automatic_version_check") is False:
        return None, "off", None, None, None

    try:
        releases = api(f"https://api.github.com/repos/{slug}/releases?per_page=50")
    except urllib.error.HTTPError as e:
        return None, f"error: GitHub {e.code} listing releases", None, None, None
    except Exception as e:                                   # network, DNS, ...
        return None, f"error: {type(e).__name__} listing releases", None, None, None

    live = [r for r in releases if not r.get("draft")]
    if not live:
        return None, "no installable release", None, None, None

    stamps = sorted(str(r.get("published_at") or "") for r in live if r.get("published_at"))
    first_release = stamps[0] if stamps else None
    last_release = stamps[-1] if stamps else None

    total = sum(int(a.get("download_count") or 0)
                for r in live for a in r.get("assets", []))
    downloads = {"total": total,
                 "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

    # newest first is the API's own order; prefer a real release over a
    # prerelease, but take a prerelease over nothing at all
    ordered = [r for r in live if not r.get("prerelease")] or live
    for release in ordered:
        zip_asset = pick_zip(release, entry["id"])
        if zip_asset:
            latest = {
                "version": version_of(release),
                "tag": release.get("tag_name"),
                "name": release.get("name") or version_of(release),
                "prerelease": bool(release.get("prerelease")),
                "published_at": release.get("published_at"),
                "zip": zip_asset,
            }
            return latest, "ok", downloads, first_release, last_release
    return None, "no installable release", downloads, first_release, last_release


def read_entries():
    entries, problems = [], []
    for folder in sorted(p for p in MODS.iterdir() if p.is_dir()):
        path = folder / "meta.json"
        if not path.exists():
            problems.append(f"{folder.name}: no meta.json")
            continue
        try:
            meta = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"{folder.name}/meta.json: {e}")
            continue
        missing = [k for k in REQUIRED if not meta.get(k)]
        if missing:
            problems.append(f"{folder.name}: missing {', '.join(missing)}")
            continue
        entries.append((folder, meta))
    return entries, problems


def build():
    entries, problems = read_entries()
    if problems:
        for p in problems:
            print(f"::error::{p}", file=sys.stderr)
        raise SystemExit(1)

    mods = []
    for folder, meta in entries:
        latest, update_check, downloads, first_release, last_release = \
            resolve_releases(meta)

        row = dict(meta)
        row["folder"] = folder.name
        row.pop("automatic_version_check", None)     # a build input, not feed data

        # Absolute, so the card's picture and text load whether or not Pages
        # is serving this repo.
        if (folder / "thumbnail.png").exists():
            row["thumbnail"] = f"{RAW}/mods/{folder.name}/thumbnail.png"
        if (folder / "description.md").exists():
            row["description_url"] = f"{RAW}/mods/{folder.name}/description.md"

        row["update_check"] = update_check
        if latest:
            row["latest"] = latest
        if downloads:
            row["downloads"] = downloads
        if first_release:
            row["first_release"] = first_release
        if last_release:
            row["last_release"] = last_release

        state = update_check if update_check != "ok" else f"ok, {latest['version']}"
        print(f"  {folder.name:<32} {state}")
        mods.append(row)

    mods.sort(key=lambda m: str(m.get("title", "")).lower())
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(mods),
        "categories": CATEGORIES,
        "mods": mods,
    }


def stable(doc):
    """The feed with its every-run timestamps removed, for comparison only."""
    out = {k: v for k, v in doc.items() if k != "generated_at"}
    mods = []
    for m in out.get("mods", []):
        m = dict(m)
        if isinstance(m.get("downloads"), dict):
            m["downloads"] = {k: v for k, v in m["downloads"].items()
                              if k != "as_of"}
        mods.append(m)
    out["mods"] = mods
    return out


def main():
    print(f"reading {MODS.relative_to(ROOT)}/")
    feed = build()

    # Two stamps move on every run whether or not anything happened: the
    # feed's generated_at and each entry's downloads.as_of.  Rewriting the
    # file for those alone would have the nightly job commit noise every
    # night, so they are ignored when deciding whether anything changed, and
    # a quiet rebuild leaves the file exactly as it was.
    if FEED.exists():
        try:
            old = json.loads(FEED.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            old = None
        if old is not None and stable(old) == stable(feed):
            print(f"{FEED.relative_to(ROOT)} already current ({feed['count']} mod(s))")
            return 0

    FEED.parent.mkdir(parents=True, exist_ok=True)
    FEED.write_text(json.dumps(feed, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"wrote {FEED.relative_to(ROOT)} ({feed['count']} mod(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
