#!/usr/bin/env python3
"""Strict local staging preflight for an approved release (does not publish)."""
from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

from validate_manifests import ROOT, load_json, validate_manifest

MAX_FILE_BYTES = 2 * 1024 * 1024 * 1024


def verify_one(asset: dict, staging: Path, label: str, errors: list[str]) -> None:
    name, expected, length = asset["assetName"], asset["sha256"], asset["bytes"]
    path = staging / name
    if not path.is_file() or path.is_symlink():
        errors.append(f"{label}: missing or symlinked asset: {name}")
        return
    size = path.stat().st_size
    if size != length or size > MAX_FILE_BYTES:
        errors.append(f"{label}: size mismatch: {name} expected={length} actual={size}")
        return
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    if h.hexdigest() != expected:
        errors.append(f"{label}: SHA-256 mismatch: {name}")


def verify_notices(staging: Path, manifest: dict, errors: list[str]) -> None:
    notices = manifest["noticesAsset"]
    path = staging / notices["assetName"]
    if not path.is_file():
        return
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            for name in names:
                if name.startswith("/") or "\\" in name or ".." in Path(name).parts:
                    errors.append(f"unsafe license archive path: {name}")
            for entry in manifest["files"]:
                expected = f"licenses/{entry['id']}.txt"
                if expected not in names:
                    errors.append(f"license notice missing for {entry['id']} ({expected})")
    except (zipfile.BadZipFile, OSError) as exc:
        errors.append(f"invalid notices archive: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--assets", required=True, type=Path)
    args = parser.parse_args()
    from validate_manifests import MANIFEST_SCHEMA
    try:
        manifest = load_json(args.manifest)
        schema = load_json(MANIFEST_SCHEMA)
        errors = validate_manifest(manifest, schema, f"releases/{manifest['targetId']}/{manifest['release']}.json")
        if manifest.get("status") != "published":
            errors.append("not a published manifest: staging cannot certify a draft")
        if errors:
            raise ValueError("; ".join(errors))
        staging = args.assets.resolve(strict=True)
        if not staging.is_dir():
            raise ValueError("assets path must be a directory")
        for entry in manifest["files"]:
            verify_one(entry, staging, entry["id"], errors)
            source = entry["origin"].get("correspondingSourceAsset")
            if source:
                verify_one(source, staging, f"source:{entry['id']}", errors)
        verify_one(manifest["noticesAsset"], staging, "notices", errors)
        verify_notices(staging, manifest, errors)
        if errors:
            raise ValueError("; ".join(errors))
    except (OSError, KeyError, ValueError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"OK: all release assets, GPL source snapshots and per-mod notices present and hashed locally")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
