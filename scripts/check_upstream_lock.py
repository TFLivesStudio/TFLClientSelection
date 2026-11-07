#!/usr/bin/env python3
"""Validate the exact 1.8.9 mod inventory against author-hosted GitHub Releases.

Default mode checks local trusted metadata without network calls. --online uses
GitHub's release metadata to compare exact asset SHA-256 and byte length.
Never substitutes a newer mod, downloads from Modrinth, or publishes anything.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from urllib.parse import quote
from urllib.request import Request, urlopen

from validate_manifests import ROOT, load_json, MANIFEST_SCHEMA, validate_manifest

INVENTORY = ROOT / "inventory/mc-1.8.9-ornithe-2026-11-07.json"
LOCK = ROOT / "inventory/github-release-lock.mc-1.8.9-ornithe.json"
DRAFT = ROOT / "drafts/mc-1.8.9-ornithe.json"

def verify_local(inventory: dict, lock: dict, manifest: dict) -> list[str]:
    errors = []
    jars = {m["id"]: m for m in inventory["mods"]}
    delivered = {m["id"]: m for m in lock["verified"]}
    pending = {m["id"]: m for m in lock["pending"]}
    listed = {m["id"]: m for m in manifest["files"]}
    if len(jars) != 11 or len(listed) != 11 or set(jars) != set(listed):
        errors.append("The complete original 11-JAR Selection is required")
    if len(lock["verified"]) != len(delivered) or len(lock["pending"]) != len(pending):
        errors.append("Duplicate locked mod entries")
    if set(delivered) & set(pending) or set(delivered) | set(pending) != set(jars):
        errors.append("Every original mod must have exactly one delivery state")
    if manifest.get("status") != "draft":
        errors.append("This inventory is a draft, not a published Release")
    for mod_id, entry in jars.items():
        if mod_id not in listed:
            continue
        f = listed[mod_id]
        if (f.get("sha256"), f.get("bytes"), f.get("path")) != (
                entry["sha256"], entry["bytes"], entry["installPath"]):
            errors.append(f"{mod_id}: manifest bytes/path differ from owner-provided ZIP")
        if mod_id in delivered:
            locked = delivered[mod_id]
            dl = locked["download"]
            if (f.get("download") != dl
                    or locked["sha256"] != entry["sha256"]
                    or locked["bytes"] != entry["bytes"]
                    or locked["version"] != entry["version"]
                    or dl.get("asset") != entry["filename"]
                    or f.get("origin") != locked["origin"]):
                errors.append(f"{mod_id}: GitHub Release must be pinned to exact inspected asset")
            if f["origin"].get("redistributionBasis") == "upstream-direct":
                if dl.get("repository", "").lower() != "quicksilvermc/argentum":
                    errors.append(f"{mod_id}: ARR only from upstream original author")
        elif mod_id in pending:
            if "download" in f:
                errors.append(f"{mod_id}: no exact matching public asset has been verified")
            if not f.get("origin", {}).get("sourceRevision", "").startswith("PENDING"):
                errors.append(f"{mod_id}: unpublished own-release asset needs provenance")
    errors.extend(validate_manifest(manifest, load_json(MANIFEST_SCHEMA),
                                    "drafts/mc-1.8.9-ornithe.json"))
    return errors

def verify_github_online(lock: dict) -> list[str]:
    errors = []
    caches = {}
    for item in lock["verified"]:
        dl = item["download"]
        repo, tag, asset = dl["repository"], dl["tag"], dl["asset"]
        if not re.fullmatch(r"[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+", repo):
            errors.append("Malformed GitHub owner/repo")
            continue
        if (repo, tag) not in caches:
            url = (f"https://api.github.com/repos/{repo}/releases/tags/"
                   f"{quote(tag, safe='')}")
            req = Request(url, headers={"Accept": "application/vnd.github+json",
                                        "User-Agent": "TFL-Selection-Release-Check"})
            try:
                with urlopen(req, timeout=20) as response:
                    payload = response.read(2 * 1024 * 1024)
                caches[(repo, tag)] = json.loads(payload)
            except Exception as error:
                errors.append(f"{repo}@{tag}: cannot verify public GitHub Release ({error})")
                continue
        assets = [a for a in caches[(repo, tag)].get("assets", [])
                  if a.get("name") == asset]
        if len(assets) != 1:
            errors.append(f"{item['id']}: missing or duplicate upstream asset")
            continue
        expected_digest = "sha256:" + item["sha256"]
        a = assets[0]
        if a.get("size") != item["bytes"] or a.get("digest") != expected_digest:
            errors.append(f"{item['id']}: upstream bytes/SHA no longer match locked ZIP")
    return errors

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--online", action="store_true",
                    help="Call GitHub Releases API to check published asset sizes and hashes")
    args = ap.parse_args()
    try:
        lock = load_json(LOCK)
        errs = verify_local(load_json(INVENTORY), lock, load_json(DRAFT))
        if args.online and not errs:
            errs.extend(verify_github_online(lock))
    except (OSError, ValueError, KeyError, TypeError) as error:
        errs = [str(error)]
    if errs:
        for err in errs:
            print("LOCK INVALID:", err, file=sys.stderr)
        return 1
    print(f"OK: 11 original mods, 6 author-hosted pinned GitHub assets, 5 pending TFL-hosted binaries. "
          f"{'Online hashes verified.' if args.online else 'Local lock only.'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
