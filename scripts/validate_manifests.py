#!/usr/bin/env python3
"""Validate schema and distribution safety for TFL Selection manifests.

This is CI/static validation, not a proof that remote blobs exist or licenses are valid.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = ROOT / "schemas" / "manifest.v1.schema.json"
CATALOG_SCHEMA = ROOT / "schemas" / "catalog.v1.schema.json"
KIND_ROOT = {
    "mod": "mods", "config": "config", "resourcepack": "resourcepacks",
    "shaderpack": "shaderpacks", "asset": "assets", "datapack": "datapacks",
}
WINDOWS_RESERVED = {
    "con", "prn", "aux", "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def schema_errors(document: dict, schema: dict) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{'/'.join(str(p) for p in err.absolute_path) or '<root>'}: {err.message}"
        for err in sorted(validator.iter_errors(document), key=lambda err: str(list(err.path)))
    ]


def safe_https(value: str) -> bool:
    try:
        parts = urlsplit(value)
        if parts.scheme != "https" or not parts.netloc or parts.username or parts.password:
            return False
        host = parts.hostname or ""
        if not host or host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
            return False
        try:
            ipaddress.ip_address(host)
            return False  # do not offer direct IP URLs to the downloader
        except ValueError:
            pass
        return True
    except ValueError:
        return False


def safe_install_path(path: str, kind: str) -> bool:
    if not isinstance(path, str) or not path or len(path) > 300 or "\\" in path:
        return False
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in path) or ":" in path:
        return False
    segments = path.split("/")
    if len(segments) < 2 or segments[0] != KIND_ROOT.get(kind):
        return False
    if any(part in ("", ".", "..") or part.endswith((".", " ")) for part in segments):
        return False
    if any(part.split(".")[0].casefold() in WINDOWS_RESERVED for part in segments):
        return False
    if any(any(ch in '<>"|?*' for ch in part) for part in segments):
        return False
    return True


def validate_manifest(data: dict, schema: dict, location: str = "drafts/example.json") -> list[str]:
    errors = schema_errors(data, schema)
    seen_paths: set[str] = set()
    seen_ids: set[str] = set()
    feature_ids: set[str] = set()

    for feature in data.get("features", []):
        if not isinstance(feature, dict):
            continue
        fid = feature.get("id")
        if fid in feature_ids:
            errors.append(f"duplicate feature id: {fid}")
        feature_ids.add(fid)

    for file in data.get("files", []):
        if not isinstance(file, dict):
            continue
        fid, path = file.get("id"), file.get("path")
        if not isinstance(fid, str) or not isinstance(path, str):
            continue
        if fid in seen_ids:
            errors.append(f"duplicate file id: {fid}")
        seen_ids.add(fid)
        normalized = path.casefold()
        if normalized in seen_paths:
            errors.append(f"duplicate install path (case-insensitive): {path}")
        seen_paths.add(normalized)
        if not safe_install_path(path, file.get("kind", "")):
            errors.append(f"unsafe or wrong-kind install path: {path}")
        if "featureId" in file and file["featureId"] not in feature_ids:
            errors.append(f"unknown featureId for {fid}: {file['featureId']}")

        delivery, origin = file.get("delivery", {}), file.get("origin", {})
        if not isinstance(delivery, dict) or not isinstance(origin, dict):
            continue
        mode, rights = delivery.get("mode"), origin.get("redistribution")
        if mode == "private-object":
            if rights not in ("owned", "authorized"):
                errors.append(f"{fid}: private storage requires ownership or redistribution authorization")
            if rights == "authorized" and not origin.get("evidenceUrl"):
                errors.append(f"{fid}: authorized redistribution requires evidenceUrl")
            digest = file.get("sha256")
            if isinstance(digest, str):
                expected = f"sha256/{digest[:2]}/{digest}"
                if delivery.get("objectKey") != expected:
                    errors.append(f"{fid}: objectKey must match content hash {expected}")
        elif mode == "upstream":
            if not safe_https(delivery.get("url", "")):
                errors.append(f"{fid}: upstream download must be a safe HTTPS URL")
        if rights == "upstream-only" and mode != "upstream":
            errors.append(f"{fid}: upstream-only licensing forbids private distribution")
        for key in ("homepage", "evidenceUrl"):
            if key in origin and not safe_https(origin[key]):
                errors.append(f"{fid}: origin.{key} must be safe HTTPS")

    status = data.get("status")
    if location.startswith("drafts/") and status != "draft":
        errors.append("drafts/ can only contain draft manifests")
    if location.startswith("releases/"):
        if status != "published":
            errors.append("releases/ must contain published manifests")
        parts = location.split("/")
        if len(parts) != 4 or parts[1] != data.get("targetId") or parts[2] != data.get("release"):
            errors.append("release path must be releases/<targetId>/<release>/<channel>.json")
        elif parts[3] != data.get("channel", "") + ".json":
            errors.append("release filename must match channel")
    return errors


def validate_catalog(data: dict, schema: dict, require_local_files: bool) -> list[str]:
    errors = schema_errors(data, schema)
    targets: set[str] = set()
    for target in data.get("targets", []):
        tid = target.get("targetId")
        if tid in targets:
            errors.append(f"duplicate target: {tid}")
        targets.add(tid)
        for channel, entry in target.get("channels", {}).items():
            path = entry.get("manifestPath", "")
            if not path.startswith(f"releases/{tid}/") or not path.endswith(f"/{channel}.json"):
                errors.append(f"{tid}/{channel}: mismatched release manifest path")
                continue
            parts = path.split("/")
            if len(parts) != 4 or parts[2] != entry.get("release"):
                errors.append(f"{tid}/{channel}: release does not match catalog path")
                continue
            if require_local_files:
                manifest_path = ROOT / path
                if not manifest_path.is_file():
                    errors.append(f"{tid}/{channel}: referenced manifest missing: {path}")
                else:
                    raw = manifest_path.read_bytes()
                    digest = hashlib.sha256(raw).hexdigest()
                    if digest != entry.get("manifestSha256"):
                        errors.append(f"{tid}/{channel}: manifestSha256 does not match file bytes")
                    signature_path = ROOT / (path + ".sig")
                    if not signature_path.is_file():
                        errors.append(f"{tid}/{channel}: detached Ed25519 signature missing: {path}.sig")
    return errors


def main() -> int:
    manifest_schema, catalog_schema = load_json(MANIFEST_SCHEMA), load_json(CATALOG_SCHEMA)
    Draft202012Validator.check_schema(manifest_schema)
    Draft202012Validator.check_schema(catalog_schema)
    checked = 0
    failures: list[str] = []
    paths = sorted((ROOT / "drafts").glob("*.json")) + sorted((ROOT / "releases").glob("*/*/*.json"))
    if not paths:
        failures.append("No manifests or drafts found")
    for path in paths:
        location = path.relative_to(ROOT).as_posix()
        try:
            errs = validate_manifest(load_json(path), manifest_schema, location)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errs = [str(exc)]
        failures.extend(f"{location}: {error}" for error in errs)
        checked += 1
    catalog_paths = [ROOT / "catalog" / "catalog.template.json"]
    current = ROOT / "catalog" / "current.json"
    if current.exists():
        catalog_paths.append(current)
    for path in catalog_paths:
        location = path.relative_to(ROOT).as_posix()
        try:
            errs = validate_catalog(load_json(path), catalog_schema, require_local_files=path == current)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errs = [str(exc)]
        failures.extend(f"{location}: {error}" for error in errs)
        checked += 1
    if failures:
        print(f"FAILED ({len(failures)} issues; {checked} documents inspected)")
        for error in failures:
            print(f" - {error}")
        return 1
    print(f"OK: {checked} JSON documents verified against schemas and safety policies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
