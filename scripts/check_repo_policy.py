#!/usr/bin/env python3
"""Prevent accidental binary/secret commits and published-manifest rewriting."""
from __future__ import annotations
import subprocess
from pathlib import PurePosixPath

BLOCKED_SUFFIXES = {".jar", ".zip", ".mrpack", ".pem", ".p12", ".pfx", ".jks", ".keystore", ".key"}
BLOCKED_NAMES = {".env", "id_rsa", "id_ed25519"}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def main() -> int:
    paths = [p.decode() for p in git("ls-files", "-z").split(b"\x00") if p]
    problems = []
    names = set(paths)
    for path in paths:
        p = PurePosixPath(path)
        if p.suffix.lower() in BLOCKED_SUFFIXES or p.name in BLOCKED_NAMES or p.name.startswith(".env."):
            problems.append(f"prohibited tracked binary/secret filename: {path}")
        if path.startswith("releases/") and path.endswith(".json") and path + ".sig" not in names:
            problems.append(f"release must have detached signature: {path}.sig")
    try:
        base_entries = git("ls-tree", "-r", "origin/main").decode().splitlines()
    except subprocess.CalledProcessError:
        base_entries = []
    base = {}
    for item in base_entries:
        try:
            meta, path = item.split("\t", 1)
            base[path] = meta.split()[-1]
        except ValueError:
            continue
    head_entries = git("ls-tree", "-r", "HEAD").decode().splitlines()
    head = {}
    for item in head_entries:
        try:
            meta, path = item.split("\t", 1)
            head[path] = meta.split()[-1]
        except ValueError:
            continue
    for path, old_blob in base.items():
        if path.startswith("releases/") and (path not in head or head[path] != old_blob):
            problems.append(f"immutable published release was removed/edited: {path}")
    if problems:
        print("FAILED repository policy:")
        for problem in problems:
            print(" -", problem)
        return 1
    print(f"OK: {len(paths)} tracked paths, no forbidden binaries or edited published releases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
