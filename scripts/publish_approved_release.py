#!/usr/bin/env python3
"""Publish a VERIFIED local Selection candidate into GitHub Releases.

Safe by default: dry-run validation. --publish requires an explicit QA record,
GitHub CLI authentication, an Ed25519 signing secret, and a clean main branch.
Never use with the current unlicensed 1.8.9 JARs.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from selection_sign import signature_from_file, verify_bytes
from selection_promote import prepare as prepare_catalog
from validate_manifests import ROOT, load_json

REPO = "TFLivesStudio/TFLClientSelection"


def execute(*args: str, capture: bool = False) -> str:
    result = subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE if capture else None)
    return (result.stdout or "").strip()


def validate_local(candidate: Path) -> dict:
    manifest = candidate / "manifest.json"
    assets = candidate / "assets"
    if not manifest.is_file() or not assets.is_dir():
        raise ValueError("Candidate must contain manifest.json and assets/")
    execute(sys.executable, str(ROOT / "scripts/verify_release_assets.py"),
            "--manifest", str(manifest), "--assets", str(assets))
    data = load_json(manifest)
    if data["distribution"]["repository"] != REPO or data["targetId"] != "mc-1.8.9-ornithe":
        raise ValueError("Unexpected repo/target")
    if len([x for x in data["files"] if x["kind"] == "mod"]) != 11:
        raise ValueError("All 11 selected mods must be present")
    return data


def check_repo_checkout() -> str:
    top = Path(execute("git", "-C", str(ROOT), "rev-parse", "--show-toplevel", capture=True)).resolve()
    if top != ROOT.resolve():
        raise ValueError("Must run inside a real local checkout of TFLClientSelection")
    if execute("git", "-C", str(ROOT), "branch", "--show-current", capture=True) != "main":
        raise ValueError("Publishing requires the checked-out main branch")
    if execute("git", "-C", str(ROOT), "status", "--porcelain", capture=True):
        raise ValueError("Clean Git working tree required before publication")
    execute("git", "-C", str(ROOT), "fetch", "--quiet", "origin", "main")
    local = execute("git", "-C", str(ROOT), "rev-parse", "HEAD", capture=True)
    remote = execute("git", "-C", str(ROOT), "rev-parse", "origin/main", capture=True)
    if local != remote:
        raise ValueError("Local main must exactly match origin/main")
    return local


def compare_published(staged: Path, downloaded: Path) -> None:
    for src in staged.iterdir():
        if not src.is_file():
            continue
        remote = downloaded / src.name
        if not remote.is_file():
            raise ValueError(f"GitHub Release is missing {src.name}")
        if hashlib.sha256(src.read_bytes()).digest() != hashlib.sha256(remote.read_bytes()).digest():
            raise ValueError(f"Remote asset hash mismatch: {src.name}")


def publish(candidate: Path, pubkey: Path, qa_record: Path, channel: str) -> None:
    data = validate_local(candidate)
    if not qa_record.is_file() or qa_record.stat().st_size < 100:
        raise ValueError("Signed-off manual launch/compatibility QA record required")
    local_sha = check_repo_checkout()
    execute("gh", "auth", "status")
    try:
        execute("gh", "release", "view", data["distribution"]["tag"], "--repo", REPO)
    except subprocess.CalledProcessError:
        pass
    else:
        raise ValueError("Release tag exists: refusing to mutate a published/draft release")
    manifest = candidate / "manifest.json"
    signature = candidate / "manifest.json.sig"
    if signature.exists():
        raise ValueError("Staging signature already exists; refuse to re-sign in-place")
    signature.write_text(signature_from_file(manifest), encoding="ascii")
    verify_bytes(manifest.read_bytes(), signature.read_text(), pubkey.read_text())
    tag = data["distribution"]["tag"]
    upload = [str(p) for p in sorted((candidate / "assets").iterdir()) if p.is_file()]
    if len(upload) > 997:
        raise ValueError("GitHub Release asset count limit")
    # Create a draft release with all candidate assets. It will not be discoverable
    # via signed catalog until we verify GitHub's bytes and commit catalog pointer.
    execute("gh", "release", "create", tag, "--repo", REPO,
            "--target", local_sha, "--draft",
            "--title", "TFLClient 1.8.9 " + data["release"],
            "--notes-file", str(qa_record),
            str(manifest), str(signature), *upload)
    with tempfile.TemporaryDirectory(prefix="tfl-gh-verify-") as temporary:
        temp = Path(temporary)
        execute("gh", "release", "download", tag, "--repo", REPO, "--dir", str(temp))
        compare_published(candidate / "assets", temp)
        for part in (manifest, signature):
            if hashlib.sha256(part.read_bytes()).digest() != hashlib.sha256((temp / part.name).read_bytes()).digest():
                raise ValueError("Downloaded manifest/signature differs from verified staging")
    with tempfile.TemporaryDirectory(prefix="tfl-catalog-stage-") as catalog_dir:
        stage = Path(catalog_dir)
        prepare_catalog(manifest, ROOT / "catalog/current.json", ROOT / "catalog/current.json.sig",
                        pubkey, stage, channel)
        if channel == "stable":
            execute("gh", "release", "edit", tag, "--repo", REPO, "--draft=false")
        else:
            execute("gh", "release", "edit", tag, "--repo", REPO, "--draft=false", "--prerelease")
        release_dir = ROOT / "releases" / data["targetId"]
        release_dir.mkdir(parents=True, exist_ok=True)
        release_json = release_dir / (data["release"] + ".json")
        release_sig = release_dir / (data["release"] + ".json.sig")
        if release_json.exists() or release_sig.exists():
            raise ValueError("Release source-of-truth file already exists")
        shutil.copyfile(manifest, release_json)
        shutil.copyfile(signature, release_sig)
        (ROOT / "catalog").mkdir(exist_ok=True)
        shutil.copyfile(stage / "current.json", ROOT / "catalog/current.json")
        shutil.copyfile(stage / "current.json.sig", ROOT / "catalog/current.json.sig")
        execute("git", "-C", str(ROOT), "add", "--",
                str(release_json.relative_to(ROOT)), str(release_sig.relative_to(ROOT)),
                "catalog/current.json", "catalog/current.json.sig")
        execute("git", "-C", str(ROOT), "commit", "-m",
                f"release: {data['targetId']} {data['release']} to {channel}")
        execute("git", "-C", str(ROOT), "push", "origin", "main")
    print(f"Published and promoted {tag}; launcher can discover generation after catalog refresh")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--public-key", type=Path)
    p.add_argument("--qa-record", type=Path)
    p.add_argument("--channel", choices=["stable", "beta", "dev"], default="beta")
    p.add_argument("--publish", action="store_true", help="Explicitly perform remote publication")
    a = p.parse_args()
    try:
        data = validate_local(a.candidate)
        if not a.publish:
            print(f"DRY RUN ONLY: {data['distribution']['tag']} validates; no upload attempted")
            return 0
        if not a.public_key or not a.qa_record:
            raise ValueError("Public key and reviewed QA record required for --publish")
        publish(a.candidate, a.public_key, a.qa_record, a.channel)
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError, KeyError) as exc:
        print(f"PUBLISH BLOCKED: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
