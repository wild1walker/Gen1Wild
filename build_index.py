#!/usr/bin/env python3
"""Regenerate index.json from the per-mod entries under mods/.

Each mods/<Author>@<id>/meta.json is one mod. The generated index.json is the
flat feed shape the launcher's ModIndex.resolveSource accepts from any https
URL ending in .json.

Usage:  python3 build_index.py [--check]
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
MODS = ROOT / "mods"
OUT = ROOT / "index.json"

REQUIRED = ("id", "title", "author", "version", "downloadURL")


def load_mods():
    mods = []
    for meta_path in sorted(MODS.glob("*/meta.json")):
        with meta_path.open(encoding="utf-8") as fh:
            meta = json.load(fh)
        missing = [k for k in REQUIRED if not meta.get(k)]
        if missing:
            sys.exit(f"{meta_path}: missing required field(s): {', '.join(missing)}")
        if "REPLACE-WITH" in json.dumps(meta):
            sys.exit(f"{meta_path}: still contains a REPLACE-WITH placeholder")
        mods.append(meta)

    seen = {}
    for meta in mods:
        if meta["id"] in seen:
            sys.exit(f"duplicate mod id {meta['id']!r} in this feed")
        seen[meta["id"]] = meta
    return mods


def build():
    mods = load_mods()
    return {"schema_version": 1, "count": len(mods), "mods": mods}


if __name__ == "__main__":
    feed = json.dumps(build(), indent=2, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != feed:
            sys.exit("index.json is stale — run: python3 build_index.py")
        print(f"index.json up to date ({build()['count']} mod(s))")
    else:
        OUT.write_text(feed, encoding="utf-8")
        print(f"wrote index.json ({build()['count']} mod(s))")
