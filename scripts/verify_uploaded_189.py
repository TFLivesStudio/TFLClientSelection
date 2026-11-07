#!/usr/bin/env python3
"""Verify six exact JAR assets from the owner's Prism ZIP before publication.

This script never downloads or uploads. It rejects replacement versions, wrong
digests, unknown JAR files, duplicate IDs and malformed zip/JAR archives.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile, BadZipFile

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "inventory/mc-1.8.9-ornithe-2026-11-07.json"
LOCK = ROOT / "inventory/github-release-lock.mc-1.8.9-ornithe.json"
PINS = ROOT / "inventory/owned-source-pins.mc-1.8.9-ornithe.json"

def hash_path(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()

def validate(supplied: Path, inventory=None, lock=None, pins=None) -> list[str]:
    try:
        inventory = inventory or json.loads(INV.read_text(encoding="utf-8"))
        lock = lock or json.loads(LOCK.read_text(encoding="utf-8"))
        pins = pins or json.loads(PINS.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        return [f"Invalid committed metadata: {exc}"]
    errors = []
    original = {m["id"]: m for m in inventory["mods"]}
    external = {m["id"] for m in lock["verified"]}
    own = {m["id"] for m in lock["pending"]}
    if len(original) != 11 or len(external) != 5 or len(own) != 6:
        errors.append("Exactly 11 originals, 5 author-hosted and 6 TFL-owned required")
    if external & own or external | own != set(original):
        errors.append("Broken complete-mod coverage")
    if set(pins.get("assets", {})) != own:
        errors.append("Source pin IDs must match the six TFL-owned mods")
    expected = {original[mod_id]["assetName"] for mod_id in own}
    try:
        files = {p.name for p in supplied.iterdir() if p.is_file()}
    except OSError as exc:
        return errors + [f"Unable to inspect uploaded staging files: {exc}"]
    missing = expected - files
    extras = {name for name in files if re.fullmatch(r"sha256-[0-9a-f]{64}\.bin", name)} - expected
    for name in sorted(missing):
        errors.append("Missing required pinned binary: " + name)
    for name in sorted(extras):
        errors.append("Unexpected or forbidden substituted JAR: " + name)
    for mod_id in sorted(own):
        mod = original[mod_id]
        pin = pins.get("assets", {}).get(mod_id, {})
        if mod["version"] != pin.get("version"):
            errors.append(f"{mod_id}: pinned source version differs from the original JAR")
        path = supplied / mod["assetName"]
        if not path.is_file():
            continue
        if path.is_symlink() or path.stat().st_size != mod["bytes"]:
            errors.append(f"{mod_id}: unsafe file or size mismatch")
            continue
        if hash_path(path) != mod["sha256"]:
            errors.append(f"{mod_id}: SHA-256 differs from owner's original Prism JAR")
            continue
        try:
            with ZipFile(path) as jar:
                if jar.testzip() is not None:
                    errors.append(f"{mod_id}: damaged JAR entries")
                meta = json.loads(jar.read("fabric.mod.json"))
                if meta.get("id") != mod_id or meta.get("version") != mod["version"]:
                    errors.append(f"{mod_id}: embedded mod ID/version mismatch")
                if mod_id == "amplio" and "natives/windows-x86_64/nvngx_dlss.dll" not in jar.namelist():
                    errors.append("Amplio original native DLL is missing")
        except (OSError, BadZipFile, ValueError, KeyError) as exc:
            errors.append(f"{mod_id}: malformed Fabric JAR ({exc})")
    return errors

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--assets", required=True, type=Path)
    args = p.parse_args()
    errors = validate(args.assets)
    for error in errors:
        print("BLOCKED:", error, file=sys.stderr)
    if errors:
        return 1
    print("OK: all six exact original Prism mod JARs verified by bytes, SHA-256 and Fabric metadata")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
