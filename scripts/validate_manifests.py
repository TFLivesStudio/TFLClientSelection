#!/usr/bin/env python3
"""Validate TFL Selection v2 *authoring* contracts. Publication requires separate checks."""
from __future__ import annotations
import hashlib
import ipaddress
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = ROOT / "schemas/manifest.v2.schema.json"
CATALOG_SCHEMA = ROOT / "schemas/catalog.v2.schema.json"
DISTRIBUTION = "TFLivesStudio/TFLSelectionDistribution"
KIND_ROOT = {
    "mod": "mods", "config": "config", "resourcepack": "resourcepacks",
    "shaderpack": "shaderpacks", "asset": "assets", "datapack": "datapacks",
    "loader-bootstrap": "bootstrap",
}
WINDOWS_RESERVED = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
# Not a legal opinion: this allowlist simply requires an explicit licensing review.
OPEN_SOURCE_REVIEWED = {
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC",
    "GPL-3.0-only", "GPL-3.0-or-later", "LGPL-3.0-only",
    "LGPL-3.0-or-later", "MPL-2.0", "CC0-1.0",
}
SOURCE_REQUIRED = {"GPL-3.0-only", "GPL-3.0-or-later", "LGPL-3.0-only", "LGPL-3.0-or-later"}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def schema_errors(document: dict, schema: dict) -> list[str]:
    v = Draft202012Validator(schema, format_checker=FormatChecker())
    return [f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
            for e in sorted(v.iter_errors(document), key=lambda e: str(list(e.absolute_path)))]


def safe_https(value: str) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parts = urlsplit(value)
        if parts.scheme != "https" or not parts.netloc or parts.username or parts.password:
            return False
        hostname = (parts.hostname or "").lower()
        if not hostname or hostname == "localhost" or hostname.endswith((".localhost", ".local", ".internal")):
            return False
        try:
            ipaddress.ip_address(hostname)
            return False
        except ValueError:
            return True
    except ValueError:
        return False


def safe_install_path(path: str, kind: str) -> bool:
    if not isinstance(path, str) or not isinstance(kind, str) or len(path) > 300:
        return False
    if "\\" in path or ":" in path or any(ord(c) < 32 or ord(c) == 127 for c in path):
        return False
    parts = path.split("/")
    if len(parts) < 2 or parts[0] != KIND_ROOT.get(kind):
        return False
    if any(p in ("", ".", "..") or p.endswith((" ", ".")) for p in parts):
        return False
    if any(p.split(".")[0].casefold() in WINDOWS_RESERVED for p in parts):
        return False
    if any(any(c in '<>"|?*' for c in p) for p in parts):
        return False
    if kind in ("mod", "loader-bootstrap") and not path.endswith(".jar"):
        return False
    return True


def expected_tag(target_id: str, release: str) -> str:
    return f"selection-{target_id}-v{release}"


def validate_manifest(data: dict, schema: dict, location: str = "drafts/example.json") -> list[str]:
    errors = schema_errors(data, schema)
    if not isinstance(data, dict):
        return errors
    seen_ids, seen_paths = set(), set()
    status = data.get("status")
    if location.startswith("drafts/") and status != "draft":
        errors.append("drafts must have status=draft")
    if location.startswith("releases/"):
        parts = location.split("/")
        if status != "published" or len(parts) != 3 or parts[1] != data.get("targetId") or parts[2] != str(data.get("release")) + ".json":
            errors.append("published manifests live at releases/<targetId>/<release>.json")
    minecraft = data.get("minecraft", {})
    if isinstance(minecraft, dict):
        target = data.get("targetId")
        if target == "mc-1.8.9-ornithe" and (minecraft.get("version") != "1.8.9" or minecraft.get("loader") != "ornithe-gen2"):
            errors.append("Ornithe target mismatch")
        if target == "mc-26.3-fabric" and (minecraft.get("version") != "26.3" or minecraft.get("loader") != "fabric"):
            errors.append("Fabric target mismatch")
        if status == "published":
            expected = "launcher-pinned-ornithe" if minecraft.get("loader") == "ornithe-gen2" else "launcher-pinned-fabric"
            if minecraft.get("bootstrap") != expected:
                errors.append("bootstrap strategy must match pinned loader")
    distribution = data.get("distribution", {})
    if isinstance(distribution, dict) and distribution:
        if distribution.get("tag") != expected_tag(data.get("targetId", ""), data.get("release", "")):
            errors.append("distribution tag must match target and release")
    files = data.get("files", [])
    if not isinstance(files, list):
        return errors
    for entry in files:
        if not isinstance(entry, dict):
            continue
        fid, kind, path, digest = entry.get("id"), entry.get("kind"), entry.get("path"), entry.get("sha256")
        if not isinstance(fid, str) or not isinstance(path, str):
            continue
        if fid in seen_ids:
            errors.append(f"duplicate file id: {fid}")
        seen_ids.add(fid)
        if path.casefold() in seen_paths:
            errors.append(f"duplicate installed path (case-insensitive): {path}")
        seen_paths.add(path.casefold())
        if not safe_install_path(path, kind):
            errors.append(f"unsafe path or wrong artifact kind: {path}")
        if kind == "mod" and entry.get("installPolicy") != "managed":
            errors.append(f"{fid}: mods must be managed, not seed-if-absent")
        if isinstance(digest, str) and entry.get("assetName") != f"sha256-{digest}.bin":
            errors.append(f"{fid}: release assetName must exactly match sha256")
        origin = entry.get("origin", {})
        if not isinstance(origin, dict):
            continue
        basis, license_id = origin.get("redistributionBasis"), origin.get("licenseSpdx")
        if basis == "open-source-license" and license_id not in OPEN_SOURCE_REVIEWED:
            errors.append(f"{fid}: SPDX license not yet reviewed; do not publish")
        if basis == "explicit-permission" and not origin.get("permissionEvidenceUrl"):
            errors.append(f"{fid}: explicit redistribution permission needs evidence")
        if basis == "owned" and license_id != "LicenseRef-TFLives-Proprietary" and license_id not in OPEN_SOURCE_REVIEWED:
            errors.append(f"{fid}: unreviewed owned artifact license")
        for key in ("sourceRepository", "licenseEvidenceUrl", "permissionEvidenceUrl"):
            if key in origin and not safe_https(origin[key]):
                errors.append(f"{fid}: origin.{key} must be safe HTTPS")
        if license_id in SOURCE_REQUIRED and not isinstance(origin.get("correspondingSourceAsset"), dict):
            errors.append(f"{fid}: GPL/LGPL requires mirrored corresponding source archive")
        if license_id in SOURCE_REQUIRED and isinstance(origin.get("correspondingSourceAsset"), dict):
            source = origin["correspondingSourceAsset"]
            digest_source = source.get("sha256", "")
            if source.get("assetName") != f"source-{digest_source}.zip":
                errors.append(f"{fid}: GPL/LGPL source asset must be content-addressed")
    if status == "published":
        notices = data.get("noticesAsset", {})
        if isinstance(notices, dict) and notices.get("assetName") != f"notices-{notices.get('sha256', '')}.zip":
            errors.append("published notices ZIP must be content-addressed")
    return errors


def validate_catalog(data: dict, schema: dict, require_local_files: bool = False) -> list[str]:
    errors = schema_errors(data, schema)
    if not isinstance(data, dict):
        return errors
    if any(t.get("channels") for t in data.get("targets", []) if isinstance(t, dict)) and data.get("generation", 0) < 1:
        errors.append("active catalog requires positive generation (signed monotonic revision)")
    seen = set()
    for target in data.get("targets", []):
        if not isinstance(target, dict):
            continue
        tid = target.get("targetId", "")
        if tid in seen:
            errors.append(f"duplicate target: {tid}")
        seen.add(tid)
        for channel, item in target.get("channels", {}).items():
            if item.get("tag") != expected_tag(tid, item.get("release", "")):
                errors.append(f"{tid}/{channel}: noncanonical release tag")
            if require_local_files:
                release_path = ROOT / "releases" / tid / f"{item.get('release')}.json"
                if not release_path.is_file():
                    errors.append(f"{tid}/{channel}: manifest missing: {release_path}")
                    continue
                raw = release_path.read_bytes()
                if hashlib.sha256(raw).hexdigest() != item.get("manifestSha256"):
                    errors.append(f"{tid}/{channel}: manifest hash does not match exact bytes")
                if not Path(str(release_path) + ".sig").is_file():
                    errors.append(f"{tid}/{channel}: detached manifest signature missing")
                manifest = load_json(release_path)
                if (manifest.get("targetId") != tid or manifest.get("release") != item.get("release")
                    or manifest.get("distribution", {}).get("tag") != item.get("tag")
                    or manifest.get("minecraft", {}).get("version") != target.get("minecraftVersion")
                    or manifest.get("minecraft", {}).get("loader") != target.get("loader")):
                    errors.append(f"{tid}/{channel}: channel target differs from release manifest")
    return errors


def main() -> int:
    manifest_schema, catalog_schema = load_json(MANIFEST_SCHEMA), load_json(CATALOG_SCHEMA)
    Draft202012Validator.check_schema(manifest_schema)
    Draft202012Validator.check_schema(catalog_schema)
    problems, inspected = [], 0
    paths = sorted((ROOT / "drafts").glob("*.json")) + sorted((ROOT / "releases").glob("*/*.json"))
    if not paths:
        problems.append("no manifest drafts or releases")
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        try:
            errors = validate_manifest(load_json(path), manifest_schema, relative)
        except (OSError, ValueError) as exc:
            errors = [str(exc)]
        problems.extend(f"{relative}: {e}" for e in errors)
        inspected += 1
    for path in (ROOT / "catalog" / "catalog.template.json", ROOT / "catalog" / "current.json"):
        if path.name == "current.json" and not path.exists():
            continue
        try:
            errors = validate_catalog(load_json(path), catalog_schema, require_local_files=path.name == "current.json")
        except (OSError, ValueError) as exc:
            errors = [str(exc)]
        problems.extend(f"{path.relative_to(ROOT)}: {e}" for e in errors)
        inspected += 1
    if problems:
        print(f"FAILED: {len(problems)} issues in {inspected} files")
        for issue in problems:
            print(" -", issue)
        return 1
    print(f"OK: {inspected} JSON documents passed v2 contract and static safety checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
