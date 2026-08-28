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

Set "featured": true on an entry to pin it above the alphabetical run. It is
for the two bundles, which are the suite rather than mods in it; a feed where
everything is featured is a feed where nothing is.

Each carts/<Author>@<id>/ folder holds the same three files and lists a custom
cart instead -- a version-pinned mod set that plays as its own game.  Carts
ride this feed additively: `carts` is a second array beside `mods`, and a feed
without it lists no carts (src/mods/ModIndex.lua, parse).  A cart listing
names its repo in "cart_source" and its pins are read from that repo's own
cart.json on every rebuild, never copied here by hand -- a hand-copied pin
array rots the first time the cart re-pins anything, and ModIndex drops a cart
row whose pins are empty.

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
CARTS = ROOT / "carts"
FEED = ROOT / "site" / "data" / "index.json"

OWNER, REPO = "wild1walker", "Gen1Wild"
RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main"

SCHEMA_VERSION = 1
CART_FILE = "cart.json"
REQUIRED = ("id", "title", "author", "version", "categories", "repo")

# A cart listing's own gate.  src/mods/ModIndex.lua's parseCartEntry drops a
# row missing any of these -- plus a non-empty `mods` array, which is not
# written by hand here but pulled from the cart's own cart.json.
CART_REQUIRED = ("id", "title", "author", "version", "base", "seal", "repo",
                 "cart_source")

# the launcher's own vocabulary, in its own order; the panel shows the ones
# the feed's mods actually use and ignores the rest
CATEGORIES = [
    "GAMEPLAY", "CONTENT", "BALANCE", "ART", "AUDIO", "UI",
    "QOL", "TRANSLATION", "TOTAL_CONVERSION", "LIBRARY", "TOOL", "OTHER",
]

# The cart-side twin of CATEGORIES: a cart plays as exactly one game and has
# no categories, so `base` is what the panel groups them by.  Same list and
# same order as cartkit's BASES and CartManifest's vocabulary.
BASE_GAMES = ["red", "blue", "yellow", "gold", "silver", "crystal"]

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


def pick_asset(release, entry_id, suffix):
    """The asset to install: the entry's own name first, any match after it."""
    matches = [a for a in release.get("assets", [])
               if str(a.get("name", "")).lower().endswith(suffix)]
    if not matches:
        return None
    named = [a for a in matches if entry_id.lower() in str(a["name"]).lower()]
    a = (named or matches)[0]
    return {"name": a["name"], "url": a["browser_download_url"],
            "size": a.get("size")}


def pick_zip(release, mod_id):
    return pick_asset(release, mod_id, ".zip")


def pick_cart(release, cart_id):
    """A cart publishes one .g1rcart, never a .zip -- see Guide: Cartkit."""
    return pick_asset(release, cart_id, ".g1rcart")


def version_of(release):
    tag = str(release.get("tag_name") or "")
    m = SEMVER_TAG.match(tag)
    if m:
        return m.group(1)
    return str(release.get("name") or tag or "")


def resolve_releases(entry, pick=pick_zip):
    """-> (latest, update_check, downloads, first_release, last_release).

    `pick` is what counts as the installable asset: a mod publishes a .zip,
    a cart a .g1rcart.  Everything else about resolving a release -- the
    prerelease preference, the download tally, the first/last stamps -- is
    the same question for both, so it is asked once here.
    """
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
        asset = pick(release, entry["id"])
        if asset:
            latest = {
                "version": version_of(release),
                "tag": release.get("tag_name"),
                "name": release.get("name") or version_of(release),
                "prerelease": bool(release.get("prerelease")),
                "published_at": release.get("published_at"),
                "zip": asset,
            }
            return latest, "ok", downloads, first_release, last_release
    return None, "no installable release", downloads, first_release, last_release


def read_dir(root, required):
    entries, problems = [], []
    if not root.is_dir():
        return entries, problems
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        path = folder / "meta.json"
        if not path.exists():
            problems.append(f"{folder.name}: no meta.json")
            continue
        try:
            meta = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"{folder.name}/meta.json: {e}")
            continue
        missing = [k for k in required if not meta.get(k)]
        if missing:
            problems.append(f"{folder.name}: missing {', '.join(missing)}")
            continue
        entries.append((folder, meta))
    return entries, problems


def read_entries():
    return read_dir(MODS, REQUIRED)


def read_cart_entries():
    return read_dir(CARTS, CART_REQUIRED)


def fetch_raw(slug, path):
    """One file out of another repo, off whichever default branch it uses."""
    for branch in ("main", "master"):
        url = f"https://raw.githubusercontent.com/{slug}/{branch}/{path}"
        req = urllib.request.Request(url, headers={
            "User-Agent": f"{OWNER}-mod-index",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read(), None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            return None, f"GitHub {e.code} reading {branch}/{path}"
        except Exception as e:                               # network, DNS, ...
            return None, f"{type(e).__name__} reading {branch}/{path}"
    return None, f"no {path} on main or master"


def fetch_cart_json(slug):
    """A cart's own cart.json, off its default branch.

    The pins are not written by hand here.  A cart listing has to carry the
    exact set the cart pins -- ModIndex drops a cart row with no pins, and a
    row whose pins disagree with the cart is worse than no row at all -- and
    a hand-copied array is a copy that rots the first time the cart re-pins
    anything.  So the listing declares `cart_source` and the pins are read
    from the source of truth on every rebuild, the same way a mod's version
    is read from its release rather than trusted from meta.json.
    """
    body, problem = fetch_raw(slug, CART_FILE)
    if body is None:
        return None, problem
    try:
        return json.loads(body.decode("utf-8")), None
    except (ValueError, UnicodeDecodeError) as e:
        return None, f"{CART_FILE} is not JSON: {e}"


def sync_cart_label(slug, cart, folder):
    """The cart's own label art, as this listing's thumbnail.

    A mod's icon is drawn here by make_icons.py; a cart's is its cartridge,
    and the cartridge is drawn in the cart's repo.  Copying it by hand is a
    copy that rots -- it already did once, when the shell colour changed and
    the card kept the old label -- so it is fetched like the pins are, and
    written verbatim.  No scaling: the page sizes icons in CSS, and the
    hourly job runs on the standard library alone.
    """
    name = cart.get("label")
    if not isinstance(name, str) or not name.lower().endswith(".png"):
        return None
    body, problem = fetch_raw(slug, name)
    if body is None:
        return problem
    thumbnail = folder / "thumbnail.png"
    if thumbnail.exists() and thumbnail.read_bytes() == body:
        return None
    thumbnail.write_bytes(body)
    print(f"  synced {folder.name}'s thumbnail from {slug}/{name}")
    return None


def build_carts():
    """The `carts` array beside `mods`, or [] when there is no carts/ yet.

    Carts ride the same feed additively at schema_version 1 (ModIndex.parse:
    an absent `carts` is the old-feed case, not an error), so this can be
    empty and nothing downstream minds.
    """
    entries, problems = read_cart_entries()
    if problems:
        for p in problems:
            print(f"::error::carts/{p}", file=sys.stderr)
        raise SystemExit(1)
    if not entries:
        return []

    print(f"reading {CARTS.relative_to(ROOT)}/")
    carts = []
    for folder, meta in entries:
        source = meta["cart_source"]
        cart, problem = fetch_cart_json(source)

        row = dict(meta)
        row["folder"] = folder.name
        row.pop("cart_source", None)                 # a build input, not feed data
        row.pop("automatic_version_check", None)

        if cart:
            problem = sync_cart_label(source, cart, folder)
            if problem:
                print(f"::warning::{folder.name}: {problem}", file=sys.stderr)
            # The cart decides what it is; the listing only says where to find
            # it.  Everything the cart's own manifest owns is taken from there
            # and written back into meta.json, so a reader of this repo sees
            # the same pins the cart ships rather than a stale echo of them.
            # not `summary`: the cart's own is what the launcher shows off
            # the .g1rcart, and this is a listing -- the card is where the
            # longer, written-for-a-reader line belongs, the same way every
            # mod's meta.json summary here is longer than its manifest's.
            for key in ("title", "base", "seal", "shell", "finish", "speeds",
                        "mods", "load_order"):
                if cart.get(key) is not None:
                    row[key] = cart[key]
            changed = {k: (meta.get(k), row[k]) for k in ("base", "seal", "shell")
                       if meta.get(k) != row.get(k)}
            pins_changed = meta.get("mods") != row.get("mods") \
                or meta.get("load_order") != row.get("load_order")
            if changed or pins_changed:
                written = dict(meta)
                for key in ("title", "base", "seal", "shell", "finish",
                            "speeds", "mods", "load_order"):
                    if row.get(key) is not None:
                        written[key] = row[key]
                (folder / "meta.json").write_text(
                    json.dumps(written, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
                print(f"  synced {folder.name}'s pins from {source}/cart.json")
        else:
            print(f"::warning::{folder.name}: {problem}; keeping the committed "
                  "pins", file=sys.stderr)

        latest, update_check, downloads, first_release, last_release = \
            resolve_releases(meta, pick=pick_cart)
        if latest and latest.get("version"):
            row["version"] = latest["version"]

        if (folder / "thumbnail.png").exists():
            row["thumbnail"] = f"{RAW}/carts/{folder.name}/thumbnail.png"
        if (folder / "description.md").exists():
            row["description_url"] = f"{RAW}/carts/{folder.name}/description.md"

        row["update_check"] = update_check
        if latest:
            row["latest"] = latest
        if downloads:
            row["downloads"] = downloads
        if first_release:
            row["first_release"] = first_release
        if last_release:
            row["last_release"] = last_release

        if not row.get("mods"):
            print(f"::error::{folder.name}: no pins; ModIndex drops a cart "
                  "row with an empty mods array", file=sys.stderr)
            raise SystemExit(1)

        state = update_check if update_check != "ok" else f"ok, {latest['version']}"
        print(f"  {folder.name:<32} {state}")
        carts.append(row)

    carts.sort(key=lambda c: str(c.get("title", "")).lower())
    return carts


def build():
    entries, problems = read_entries()
    if problems:
        for p in problems:
            print(f"::error::{p}", file=sys.stderr)
        raise SystemExit(1)

    mods, synced = [], []
    for folder, meta in entries:
        latest, update_check, downloads, first_release, last_release = \
            resolve_releases(meta)

        # meta.json's "version" is only the fallback a card shows when no
        # release resolves -- which is exactly why it rots unwatched.  It goes
        # stale on its own every time a mod ships, and nothing notices until
        # the day a lookup fails and the fallback is what a reader is handed.
        # So a rebuild writes the resolved version back here rather than
        # leaving a number that is right only until someone needs it.  An
        # entry that resolves nothing keeps whatever it was given by hand.
        if latest and latest.get("version") \
                and meta.get("version") != latest["version"]:
            synced.append((folder.name, meta["version"], latest["version"]))
            meta["version"] = latest["version"]
            (folder / "meta.json").write_text(
                json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8")

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

    for name, was, now in synced:
        print(f"  synced {name}'s fallback version: {was} -> {now}")

    # Featured first, then alphabetical inside each group.
    #
    # The two bundles are the suite rather than mods in it -- either one
    # installs most of this list in a single card -- so they go at the top
    # instead of falling wherever G sorts. Everything downstream reads the
    # feed in order: site/index.html draws it as given, and FIND MODS lists
    # it as given, so ordering here is the only place this has to be said.
    mods.sort(key=lambda m: (not m.get("featured"), str(m.get("title", "")).lower()))

    carts = build_carts()
    feed = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(mods),
        "categories": CATEGORIES,
        "mods": mods,
    }
    # Additive, and only when there is something to add: a feed with no carts
    # stays byte-for-byte the feed it was before carts existed.
    if carts:
        feed["cart_count"] = len(carts)
        feed["base_games"] = BASE_GAMES
        feed["carts"] = carts
    return feed


def stable(doc):
    """The feed with its every-run timestamps removed, for comparison only."""
    out = {k: v for k, v in doc.items() if k != "generated_at"}

    def undated(rows):
        cleaned = []
        for row in rows:
            row = dict(row)
            if isinstance(row.get("downloads"), dict):
                row["downloads"] = {k: v for k, v in row["downloads"].items()
                                    if k != "as_of"}
            cleaned.append(row)
        return cleaned

    out["mods"] = undated(out.get("mods", []))
    if "carts" in out:
        out["carts"] = undated(out["carts"])
    return out


def tally(feed):
    counts = f"{feed['count']} mod(s)"
    if feed.get("cart_count"):
        counts += f", {feed['cart_count']} cart(s)"
    return counts


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
            print(f"{FEED.relative_to(ROOT)} already current ({tally(feed)})")
            return 0

    FEED.parent.mkdir(parents=True, exist_ok=True)
    FEED.write_text(json.dumps(feed, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"wrote {FEED.relative_to(ROOT)} ({tally(feed)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
