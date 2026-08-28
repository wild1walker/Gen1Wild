#!/usr/bin/env python3
"""Copy this index's entries into a checkout of the community mod index.

The community index is a second, wider feed with its own repo:

    https://github.com/bryanthaboi/gen1recomp-mod-index

An entry there is the same three files an entry here is -- meta.json,
description.md, thumbnail.png in a <Author>@<id> folder -- so a submission is
a copy, not a rewrite.  Two fields do not travel:

    featured       ours; it pins the bundles above the alphabetical run here,
                   and their schema is additionalProperties: false
    cart_source    a build input.  Their cart entries carry the pins inline,
                   which is what our carts/ folder already holds after a
                   rebuild reads them out of the cart's own cart.json

Everything else is theirs too: same field names, same shapes, same folder
convention.

An entry already listed there keeps its version.  Their nightly job reads
releases off GitHub for any entry with "github" and automatic_version_check
left on, and their CONTRIBUTING asks in as many words that a pull request not
bump a version.  Description, categories, tags and thumbnail are what a pull
request is for, and those this does carry over.

    python3 tools/make_submission.py ../gen1recomp-mod-index
    python3 tools/make_submission.py ../gen1recomp-mod-index --dry-run

Then, in that checkout:

    node scripts/validate.mjs mods/Wild@gen1_sprint     # or no path for all
    git switch -c wild-mods && git add mods carts && git commit
"""

import argparse
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Ours, and nowhere in their schema, which refuses what it does not name.
DROP = ("featured", "cart_source")

FILES = ("meta.json", "description.md", "thumbnail.png", "thumbnail.jpg")

# Their schema is stricter than this feed in two places: a summary is at most
# 200 characters and an entry carries at most 8 tags.  A summary cut to length
# reads like a summary that was cut to length, so the ones that do not fit are
# rewritten short here rather than truncated, and the tag lists that run long
# drop their weakest terms.  Anything else that overruns is an error, not a
# silent trim -- see check_limits.
SUMMARY_MAX = 200
TAGS_MAX = 8

TRIM = {
    "Wild@Gen1Dex": {
        "summary": "The Pokédex with a POKéMON beside every entry: a party icon on "
                   "every row, a silhouette until you have seen it, three pages "
                   "behind each one, and an AREA screen that says how to get there.",
        "tags": ["pokedex", "dex", "ui", "icons", "stats", "movelist", "area",
                 "town map"],
    },
    "Wild@Gen1Follower": {
        "summary": "All 251 Gen 1 and Gen 2 overworld followers, sized by Pokédex "
                   "proportions, with voxel support. Built from Antigravity & "
                   "gamecorner33's PokéPC Followers.",
    },
    "Wild@Gen1Remember": {
        "tags": ["moves", "move reminder", "relearn", "ui", "party", "box",
                 "quality of life", "learnset"],
    },
    "Wild@gen1_wild_qol": {
        "summary": "The quality-of-life half of the suite in one mod: sprinting, "
                   "autosave, auto continue, sound, followers, all 151, EXP share, "
                   "the move reminder and the mod manager.",
        "tags": ["bundle", "collection", "quality of life", "sprint", "autosave",
                 "followers", "exp share", "move reminder"],
    },
    "Wild@gen1_wild_ui": {
        "summary": "The visual half of the suite in one mod: battle backdrops and "
                   "intro, the battle menus, the Pokédex, the box, the party menu, "
                   "the bag, item icons and descriptions, the lift panel.",
        "tags": ["bundle", "collection", "ui", "pokedex", "party", "bag",
                 "backdrops", "item descriptions"],
    },
    "Wild@wild_green": {
        "tags": ["cart", "bundle", "collection", "green", "player", "sprites",
                 "ui", "quality of life"],
    },
}


def entries(root: pathlib.Path):
    """Every <Author>@<id> folder under mods/ and carts/, in that order."""
    for kind in ("mods", "carts"):
        folder = root / kind
        if not folder.is_dir():
            continue
        for path in sorted(folder.iterdir()):
            if path.is_dir() and (path / "meta.json").is_file():
                yield kind, path


def tracks_releases(meta: dict) -> bool:
    """Their nightly job owns this entry's version, so a submission must not."""
    return bool(meta.get("github")) and meta.get("automatic_version_check", True)


def listed(target: pathlib.Path, path: pathlib.Path) -> dict | None:
    """The entry as their repo has it committed, or None if it is new there.

    Read out of HEAD rather than off disk: a second run of this script would
    otherwise see the first run's files and hold a version this index has never
    submitted.
    """
    rel = path.relative_to(target).as_posix()
    try:
        blob = subprocess.run(["git", "-C", str(target), "show", f"HEAD:{rel}"],
                              capture_output=True, text=True, check=False)
    except OSError:
        return None
    if blob.returncode != 0:
        return None
    try:
        return json.loads(blob.stdout)
    except json.JSONDecodeError:
        return None


def port(name: str, meta: dict, existing: dict | None) -> dict:
    out = {k: v for k, v in meta.items() if k not in DROP}
    out.update(TRIM.get(name, {}))
    if existing and tracks_releases(out) and "version" in existing:
        out["version"] = existing["version"]
    return out


def check_limits(name: str, meta: dict) -> list[str]:
    """Their two caps, checked here so a bad entry fails before their CI does."""
    problems = []
    if len(meta.get("summary", "")) > SUMMARY_MAX:
        problems.append(f"{name}: summary is {len(meta['summary'])} characters, "
                        f"over their {SUMMARY_MAX} -- add a short one to TRIM")
    if len(meta.get("tags", [])) > TAGS_MAX:
        problems.append(f"{name}: {len(meta['tags'])} tags, over their "
                        f"{TAGS_MAX} -- pick eight in TRIM")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", type=pathlib.Path,
                    help="a checkout of bryanthaboi/gen1recomp-mod-index")
    ap.add_argument("--dry-run", action="store_true",
                    help="say what would be written, write nothing")
    args = ap.parse_args()

    target = args.target.expanduser().resolve()
    if not (target / "schema" / "mod.schema.json").is_file():
        print(f"{target} does not look like the community index "
              f"(no schema/mod.schema.json)", file=sys.stderr)
        return 1

    plan, problems = [], []

    for kind, folder in entries(ROOT):
        meta = json.loads((folder / "meta.json").read_text())
        dest = target / kind / folder.name
        existing = listed(target, dest / "meta.json")

        ported = port(folder.name, meta, existing)
        problems += check_limits(folder.name, ported)
        plan.append((folder, dest, ported, existing, meta.get("version")))

    # One bad entry fails their CI for the whole pull request, so nothing is
    # written until every entry is within their limits.
    if problems:
        for line in problems:
            print(line, file=sys.stderr)
        return 1

    written = updated = 0

    for folder, dest, ported, existing, ours in plan:
        if existing:
            updated += 1
            note = " (already listed)"
            if ported.get("version") != ours:
                note += (f"; version left at {ported['version']}, not {ours} -- "
                         f"their release job owns it")
        else:
            written += 1
            note = ""
        print(f"{'would write' if args.dry_run else 'wrote'} "
              f"{dest.parent.name}/{folder.name}{note}")

        if args.dry_run:
            continue

        dest.mkdir(parents=True, exist_ok=True)
        dest.joinpath("meta.json").write_text(
            json.dumps(ported, indent=2, ensure_ascii=False) + "\n")
        for name in FILES[1:]:
            src = folder / name
            if src.is_file():
                shutil.copy2(src, dest / name)

    print(f"\n{written} new, {updated} updated. Next:")
    print(f"  cd {target} && node scripts/validate.mjs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
