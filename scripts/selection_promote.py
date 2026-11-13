#!/usr/bin/env python3
"""Generate the next signed catalog from a verified immutable Release candidate.

This tool writes locally into --output only; it never uploads or commits.
Do NOT publish catalog pointers until the referenced GitHub Release is complete.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

from selection_sign import signature_from_file, verify_bytes
from validate_manifests import CATALOG_SCHEMA, MANIFEST_SCHEMA, ROOT, load_json, validate_catalog, validate_manifest

def prepare(manifest_file: Path, current_catalog: Path, current_signature: Path,
            trusted_public_key: Path, output_dir: Path, channel: str) -> dict:
    if channel not in ("stable", "beta", "dev"):
        raise ValueError("Invalid channel")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("Output directory must be empty")
    raw_manifest = manifest_file.read_bytes()
    manifest = json.loads(raw_manifest)
    problems = validate_manifest(manifest, load_json(MANIFEST_SCHEMA),
                                 f"releases/{manifest.get('targetId')}/{manifest.get('release')}.json")
    if problems:
        raise ValueError("Invalid release manifest: " + "; ".join(problems))
    if manifest["status"] != "published":
        raise ValueError("Unpublished candidate cannot be promoted")
    # Source of truth may be the last signed public catalog, or an unpublished template.
    if current_catalog.exists():
        if not current_signature.exists() or not trusted_public_key.exists():
            raise ValueError("Cannot trust existing catalog without signature/public key")
        raw_catalog = current_catalog.read_bytes()
        verify_bytes(raw_catalog, current_signature.read_text(encoding="ascii"),
                     trusted_public_key.read_text(encoding="ascii"))
        data = json.loads(raw_catalog)
        data["generation"] += 1
    else:
        data = load_json(ROOT / "catalog/catalog.template.json")
        data["generation"] = 1
    if data.get("distributionRepository") != "TFLivesStudio/TFLClientSelection":
        raise ValueError("Unexpected distribution repository")
    target = next((x for x in data["targets"] if x["targetId"] == manifest["targetId"]), None)
    if target is None:
        target = {"targetId": manifest["targetId"],
                  "minecraftVersion": manifest["minecraft"]["version"],
                  "loader": manifest["minecraft"]["loader"],
                  "displayName": "TFLClient " + manifest["minecraft"]["version"],
                  "summary": "TFLClient in the TFL Selection library",
                  "sortOrder": len(data["targets"]) + 1, "channels": {}}
        data["targets"].append(target)
    if (target["minecraftVersion"] != manifest["minecraft"]["version"] or
            target["loader"] != manifest["minecraft"]["loader"]):
        raise ValueError("Target's Minecraft/loader identity changed")
    # Presentation metadata is updated only in this new generation, before signing.
    name = target.get("displayName", "")
    if name.startswith("TFL Selection "):
        target["displayName"] = "TFLClient " + name[len("TFL Selection "):]
    target["channels"][channel] = {
        "release": manifest["release"],
        "tag": manifest["distribution"]["tag"],
        "manifestSha256": hashlib.sha256(raw_manifest).hexdigest(),
    }
    problems = validate_catalog(data, load_json(CATALOG_SCHEMA), require_local_files=False)
    if problems:
        raise ValueError("Catalog contract invalid: " + "; ".join(problems))
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "current.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Uses the protected ED25519 signing secret from the environment.
    (output_dir / "current.json.sig").write_text(signature_from_file(path), encoding="ascii")
    if trusted_public_key.exists():
        verify_bytes(path.read_bytes(), (output_dir / "current.json.sig").read_text(),
                     trusted_public_key.read_text())
    return data

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--current", type=Path, default=ROOT / "catalog/current.json")
    p.add_argument("--current-signature", type=Path, default=ROOT / "catalog/current.json.sig")
    p.add_argument("--public-key", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--channel", choices=["stable", "beta", "dev"], required=True)
    a = p.parse_args()
    try:
        data = prepare(a.manifest, a.current, a.current_signature, a.public_key, a.out, a.channel)
        print(f"Locally prepared signed catalog generation={data['generation']}; NOT PUBLISHED")
        return 0
    except Exception as exc:
        print(f"Catalog blocked: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
