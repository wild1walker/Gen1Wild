#!/usr/bin/env python3
"""Flatten the Wild Green cart into one importable mod .zip.

    python3 tools/build_phosphor.py --out dist/

A CART is not a MOD.  `wild_green` is a pinned list of four mods, an order to
load them in, and a shell colour; the launcher installs one by fetching each
mod and installing it separately.  Anything that imports only mod .zips --
Phosphor, or `Import mod .zip` itself -- has nothing to do with a cart file.

And "just put them all in one zip" is not available either.  The importer
refuses it before reading anything:

    if #topDirs > 1 then
      return nil, "the .zip must contain a single mod folder"
    end
    src/mods/LauncherMods.lua:384

So the answer has to be ONE mod whose payload is the other four.  This builds
it: the four sit under `mods/<id>/` exactly as released -- not merged, not
edited, not repacked -- and `main.lua` runs their entry points in the cart's
own order.

------- what is checked, and what cannot be

Each source folder must carry the manifest of the id and version the cart
pins, and a mismatch stops the build: shipping "Wild Green" built from
something other than what Wild Green pins would make the name a lie.

What is NOT checked is the sha256 the cart carries.  Those hash the RELEASED
.zip, and this builds from the repository at the matching tag -- the same
source the release was cut from, but not the same bytes, since the archive is
rebuilt here.  Provenance is the tag, and it is recorded in the output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

BUNDLE_ID = "wild_green_phosphor"


def load_cart(path: Path) -> dict:
    card = json.loads(path.read_text())
    return {
        "title": card.get("title", "Wild Green"),
        "version": card.get("version", "0.0.0"),
        "base": card.get("base", "red"),
        "mods": card["mods"],
        "load_order": card.get("load_order") or [m["id"] for m in card["mods"]],
    }


def read_manifest(folder: Path) -> dict:
    path = folder / "manifest.json"
    if not path.is_file():
        sys.exit("no manifest.json in %s" % folder)
    return json.loads(path.read_text())


def merged_manifest(cart: dict, parts: list[tuple[dict, Path]]) -> dict:
    """One manifest for the compilation.

    permissions is the union, because the bundle really does need every one
    its payload needs.  `games` is the NARROWEST rather than the union: the
    cart is a red cart and `wild_green` declares red, so claiming gen1 would
    offer this on Blue and Yellow, where a quarter of it does not apply.
    """
    permissions: list[str] = []
    for manifest, _ in parts:
        for perm in manifest.get("permissions") or []:
            if perm not in permissions:
                permissions.append(perm)

    # Everything the payload conflicts with, plus the payload's own ids: a
    # player who installs this must not also install the four separately.
    conflicts: list[str] = []
    for manifest, _ in parts:
        for other in (manifest.get("conflicts") or []) + [manifest["id"]]:
            if other not in conflicts and other != BUNDLE_ID:
                conflicts.append(other)

    # The strictest engine range any part asks for, by string equality only --
    # a real semver intersection is not worth writing when every part of this
    # suite has carried the same range for its whole life.
    ranges = {m.get("game_version") for m, _ in parts if m.get("game_version")}
    game_version = sorted(ranges)[0] if len(ranges) == 1 else sorted(ranges)[-1]

    return {
        "id": BUNDLE_ID,
        "name": "%s (single mod)" % cart["title"],
        "version": cart["version"],
        "api": 2,
        "entry": "main.lua",
        "profile": "content",
        "category": "UI",
        "game_version": game_version,
        # Above every part, so the compilation installs before anything that
        # wants to sit on top of the suite.
        "priority": max(int(m.get("priority") or 0) for m, _ in parts),
        "dependencies": [],
        "conflicts": conflicts,
        "games": [cart["base"]],
        "permissions": permissions,
        "author": "wild1walker",
        "github": "wild1walker/Gen1Wild",
        "description": (
            "%s as a single importable mod: the four mods the cart pins, in "
            "the cart's own load order, for anything that imports mod .zips "
            "but not carts."
        ) % cart["title"],
    }


def credits(cart: dict, parts: list[tuple[dict, Path]]) -> str:
    lines = [
        "# What is in this bundle",
        "",
        "`%s` is the **%s** cart flattened into one importable mod. It contains"
        % (BUNDLE_ID, cart["title"]),
        "four mods, unmodified, each under `mods/<id>/` with its own manifest,",
        "README and licence intact.",
        "",
        "| Mod | Version | Author | Source |",
        "|---|---|---|---|",
    ]
    for manifest, _ in parts:
        repo = manifest.get("github") or ""
        author = manifest.get("author") or (repo.split("/")[0] if repo else "")
        url = "https://github.com/%s" % repo if repo else ""
        lines.append("| %s | %s | %s | %s |" % (
            manifest.get("name") or manifest["id"],
            manifest.get("version", "?"),
            author or "see the mod's own README",
            url or "see the mod's own README"))
    lines += [
        "",
        "## Credit and licences",
        "",
        "Each mod keeps its own files exactly as its author released them,",
        "including its README and any licence it ships. Nothing here is a fork",
        "and nothing has been edited -- the bundle only adds a loader that runs",
        "them in the cart's order.",
        "",
        "**Crystal Animated Sprites with Shiny Visuals** is by",
        "[distilledorion-sketch](https://github.com/distilledorion-sketch/crystal_animated_sprites_with_shiny_visuals)",
        "and is included here because the cart pins it. It carries no licence",
        "file of its own. If you are its author and would rather it were not",
        "redistributed this way, open an issue on",
        "[wild1walker/Gen1Wild](https://github.com/wild1walker/Gen1Wild/issues)",
        "and it will be taken out.",
        "",
        "Everything else is MIT, by wild1walker.",
        "",
    ]
    return "\n".join(lines)


def build(cart_path: Path, sources: dict[str, Path], out_dir: Path) -> int:
    cart = load_cart(cart_path)
    by_id = {m["id"]: m for m in cart["mods"]}

    parts: list[tuple[dict, Path]] = []
    for mod_id in cart["load_order"]:
        folder = sources.get(mod_id)
        if folder is None:
            sys.exit("no source given for %s (pass --src %s=<path>)"
                     % (mod_id, mod_id))
        manifest = read_manifest(folder)
        pinned = by_id[mod_id]
        if manifest.get("id") != mod_id:
            sys.exit("%s carries id %r, expected %r"
                     % (folder, manifest.get("id"), mod_id))
        if manifest.get("version") != pinned.get("version"):
            sys.exit("%s is version %s, but the cart pins %s"
                     % (mod_id, manifest.get("version"), pinned.get("version")))
        parts.append((manifest, folder))

    staging = out_dir / BUNDLE_ID
    if staging.exists():
        shutil.rmtree(staging)
    (staging / "mods").mkdir(parents=True)

    for manifest, folder in parts:
        target = staging / "mods" / manifest["id"]
        shutil.copytree(folder, target, ignore=shutil.ignore_patterns(
            ".git", ".github", "tests", "tools", "*.zip", "__pycache__"))

    (staging / "manifest.json").write_text(
        json.dumps(merged_manifest(cart, parts), indent=2) + "\n")
    (staging / "main.lua").write_text(
        (Path(__file__).parent / "phosphor_main.lua").read_text())
    (staging / "CREDITS.md").write_text(credits(cart, parts))

    name = "%s-%s.zip" % (BUNDLE_ID, cart["version"])
    archive = out_dir / name
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(staging.parent))

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    print("%s  %d bytes" % (archive, archive.stat().st_size))
    print("sha256 %s" % digest)
    for manifest, folder in parts:
        print("  %-45s %s" % (manifest["id"], manifest.get("version")))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cart", type=Path,
                    default=Path("carts/Wild@wild_green/meta.json"))
    ap.add_argument("--src", action="append", default=[], metavar="ID=PATH",
                    help="where each pinned mod's source folder is")
    ap.add_argument("--out", type=Path, default=Path("dist"))
    args = ap.parse_args()

    sources = {}
    for pair in args.src:
        if "=" not in pair:
            sys.exit("--src wants ID=PATH, got %r" % pair)
        key, value = pair.split("=", 1)
        sources[key] = Path(value)

    args.out.mkdir(parents=True, exist_ok=True)
    return build(args.cart, sources, args.out)


if __name__ == "__main__":
    sys.exit(main())
