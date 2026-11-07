#!/usr/bin/env python3
"""Build a fully-gated, local GitHub Release candidate from an actual Prism export.

Never uploads anything. No private/player files are read except the specific mod JARs.
Approvals are evidence records for human review, not self-granted copyright licenses.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

from validate_manifests import (ROOT, MANIFEST_SCHEMA, SOURCE_REQUIRED,
                                expected_tag, load_json, safe_https, validate_manifest)

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{1,119}$")
MOD_NATIVE_SUFFIXES = (".dll", ".so", ".dylib")


def sha256_file(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest(), path.stat().st_size


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def stable_notice_zip(notices: dict[str, bytes], destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for name, contents in sorted(notices.items()):
            entry = zipfile.ZipInfo(f"licenses/{name}.txt", date_time=(2020, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            output.writestr(entry, contents)


def require(cond: bool, description: str) -> None:
    if not cond:
        raise ValueError(description)


def load_approvals(path: Path) -> dict:
    data = load_json(path)
    require(isinstance(data, dict) and data.get("schemaVersion") == 1, "invalid approvals version")
    require(isinstance(data.get("mods"), dict), "approvals must have mods mapping")
    return data["mods"]


def build(zip_file: Path, inventory_path: Path, approval_path: Path, notices_dir: Path,
          sources_dir: Path, defaults_dir: Path, output_dir: Path, release: str,
          min_launcher: str, include_defaults: bool = True,
          upstream_lock: Path | None = None) -> dict:
    require(re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?", release) is not None,
            "invalid release version")
    inventory = load_json(inventory_path)
    require(inventory.get("targetId") == "mc-1.8.9-ornithe", "wrong target")
    approvals = load_approvals(approval_path)
    items = inventory["mods"]
    external = {}
    if upstream_lock:
        source = load_json(upstream_lock)
        require(source.get("targetId") == inventory["targetId"], "upstream lock target mismatch")
        external = {item["id"]: item for item in source["verified"]}
        require(len(external) == len(source["verified"]), "duplicate upstream mod ID")
    require(len(items) == 11, "expected exactly the reviewed 11-mod selection")
    require(set(approvals) == {mod["id"] for mod in items}, "approval IDs must match all official mods")
    require(not output_dir.exists() or not any(output_dir.iterdir()), "output must be empty")
    staged = output_dir / "assets"
    staged.mkdir(parents=True, exist_ok=True)
    manifest_files, notices = [], {}
    try:
        with zipfile.ZipFile(zip_file) as source:
            require(sha256_file(zip_file)[0] == inventory["sourceZipSha256"], "Prism ZIP hash does not match inventory")
            for item in items:
                mod_id, approval = item["id"], approvals[item["id"]]
                require(ID_PATTERN.fullmatch(mod_id) is not None, "invalid mod ID")
                if mod_id in external:
                    pinned = external[mod_id]
                    require(pinned["sha256"] == item["sha256"]
                            and pinned["bytes"] == item["bytes"]
                            and pinned["version"] == item["version"],
                            f"{mod_id}: upstream asset does not match original Prism ZIP")
                    with source.open("minecraft/mods/" + item["filename"]) as stream:
                        contents = stream.read(512 * 1024 * 1024 + 1)
                    require(len(contents) == item["bytes"]
                            and sha256_bytes(contents) == item["sha256"],
                            f"{mod_id}: imported ZIP does not match pinned hash")
                    delivery = pinned["download"]
                    require(delivery["asset"] == item["filename"],
                            f"{mod_id}: GitHub Release name not exact")
                    manifest_files.append({
                        "id": mod_id, "kind": "mod", "path": item["installPath"],
                        "sha256": item["sha256"], "bytes": item["bytes"],
                        "assetName": item["assetName"], "installPolicy": "managed",
                        "download": delivery, "origin": pinned["origin"],
                    })
                    continue  # The upstream author serves this binary; TFL does not mirror it.
                require(approval.get("status") == "approved",
                        f"{mod_id}: redistribution permission has not been verified")
                origin = approval.get("origin")
                require(isinstance(origin, dict), f"{mod_id}: origin data missing")
                for key in ("project", "projectVersion", "sourceRepository", "sourceRevision",
                            "licenseSpdx", "licenseEvidenceUrl", "redistributionBasis"):
                    require(bool(origin.get(key)), f"{mod_id}: missing approval origin.{key}")
                require(origin["projectVersion"] == item["version"],
                        f"{mod_id}: approval must match exact reviewed version")
                require(safe_https(origin["sourceRepository"]) and safe_https(origin["licenseEvidenceUrl"]),
                        f"{mod_id}: valid license/source HTTPS evidence required")
                basis = origin["redistributionBasis"]
                require(basis in {"owned", "open-source-license", "explicit-permission"},
                        f"{mod_id}: unsupported redistribution basis")
                if basis == "explicit-permission":
                    require(safe_https(origin.get("permissionEvidenceUrl", "")),
                            f"{mod_id}: missing written permission evidence URL")
                if mod_id in {"argentum", "argentum-extras", "cera"}:
                    require(basis == "explicit-permission" and safe_https(origin.get("permissionEvidenceUrl", "")),
                            f"{mod_id}: current upstream is ARR; explicit authorization required for exact JAR")
                name = "minecraft/mods/" + item["filename"]
                with source.open(name) as stream:
                    payload = stream.read(512 * 1024 * 1024 + 1)
                require(len(payload) == item["bytes"] and sha256_bytes(payload) == item["sha256"],
                        f"{mod_id}: ZIP JAR bytes do not match inventory")
                with zipfile.ZipFile(io.BytesIO(payload)) as jar:
                    native_names = [f.filename for f in jar.infolist()
                                    if f.filename.lower().endswith(MOD_NATIVE_SUFFIXES)]
                if native_names:
                    clearance = approval.get("nativeClearance", {})
                    require(isinstance(clearance, dict), f"{mod_id}: nativeClearance missing")
                    for native in native_names:
                        require(safe_https(clearance.get(native, "")),
                                f"{mod_id}: native library {native} requires separate rights evidence")
                if mod_id == "amplio":
                    require("natives/windows-x86_64/nvngx_dlss.dll" in native_names,
                            "the imported Amplio DLL structure unexpectedly changed")
                notice = notices_dir / (mod_id + ".txt")
                require(notice.is_file() and not notice.is_symlink() and notice.stat().st_size > 10,
                        f"{mod_id}: full license/notice text required")
                notices[mod_id] = notice.read_bytes()
                source_asset = None
                if origin["licenseSpdx"] in SOURCE_REQUIRED:
                    src = sources_dir / (mod_id + ".zip")
                    require(src.is_file() and not src.is_symlink(), f"{mod_id}: corresponding source ZIP required")
                    with zipfile.ZipFile(src) as z:
                        require(z.testzip() is None and any(f.filename.endswith((".java", ".kt")) for f in z.infolist()),
                                f"{mod_id}: corresponding source ZIP is invalid/incomplete")
                    sh, size = sha256_file(src)
                    file_name = f"source-{sh}.zip"
                    shutil.copyfile(src, staged / file_name)
                    source_asset = {"assetName": file_name, "sha256": sh, "bytes": size}
                jar_asset = staged / item["assetName"]
                jar_asset.write_bytes(payload)
                full_origin = {key: origin[key] for key in
                               ("project", "projectVersion", "sourceRepository", "sourceRevision",
                                "licenseSpdx", "licenseEvidenceUrl", "redistributionBasis")}
                if basis == "explicit-permission":
                    full_origin["permissionEvidenceUrl"] = origin["permissionEvidenceUrl"]
                if source_asset:
                    full_origin["correspondingSourceAsset"] = source_asset
                manifest_files.append({"id": mod_id, "kind": "mod", "path": item["installPath"],
                                       "sha256": item["sha256"], "bytes": item["bytes"],
                                       "assetName": item["assetName"], "installPolicy": "managed",
                                       "origin": full_origin})
        if include_defaults and defaults_dir.is_dir():
            for path in sorted(defaults_dir.rglob("*")):
                if not path.is_file() or path.is_symlink():
                    continue
                rel = path.relative_to(defaults_dir).as_posix()
                if not rel.startswith("config/"):
                    continue  # README and other documentation are not installable defaults
                require(".." not in rel.split("/"), "unsafe default configuration path")
                raw = path.read_bytes()
                require(0 < len(raw) < 1024 * 1024, "configuration too large")
                digest = sha256_bytes(raw)
                name = f"sha256-{digest}.bin"
                (staged / name).write_bytes(raw)
                ident = "tfl-default-" + re.sub(r"[^a-z0-9._-]", "-", rel.lower())[:92]
                notices[ident] = (b"TFL Selection curated configuration default.\n"
                                  b"Copyright TFLives / licensed only as source configuration.\n")
                manifest_files.append({"id": ident, "kind": "config", "path": rel,
                                       "sha256": digest, "bytes": len(raw), "assetName": name,
                                       "installPolicy": "seed-if-absent",
                                       "origin": {"project": "TFL Selection curated defaults",
                                                  "projectVersion": release,
                                                  "sourceRepository": "https://github.com/TFLivesStudio/TFLClientSelection",
                                                  "sourceRevision": subprocess.check_output(
                                                      ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                                      text=True).strip(),
                                                  "licenseSpdx": "LicenseRef-TFLives-Proprietary",
                                                  "licenseEvidenceUrl": "https://github.com/TFLivesStudio/TFLClientSelection",
                                                  "redistributionBasis": "owned"}})
        stable_notice_zip(notices, staged / "notices-tmp.zip")
        notice_hash, notice_size = sha256_file(staged / "notices-tmp.zip")
        notice_name = f"notices-{notice_hash}.zip"
        (staged / "notices-tmp.zip").rename(staged / notice_name)
        manifest = {"schemaVersion": 2, "packId": "tfl-selection", "targetId": "mc-1.8.9-ornithe",
                    "release": release, "status": "published", "selectionMode": "locked",
                    "publishedAt": datetime.now(timezone.utc).isoformat(),
                    "minimumLauncherVersion": min_launcher,
                    "minecraft": {"version": "1.8.9", "loader": "ornithe-gen2",
                                  "loaderVersion": "0.20.1", "javaMajor": 25,
                                  "bootstrap": "launcher-pinned-ornithe"},
                    "distribution": {"repository": "TFLivesStudio/TFLClientSelection",
                                     "tag": expected_tag("mc-1.8.9-ornithe", release)},
                    "files": manifest_files, "noticesAsset": {
                        "assetName": notice_name, "sha256": notice_hash, "bytes": notice_size}}
        errors = validate_manifest(manifest, load_json(MANIFEST_SCHEMA),
                                   "releases/mc-1.8.9-ornithe/" + release + ".json")
        require(not errors, "Manifest validation failed: " + "; ".join(errors))
        target = output_dir / "manifest.json"
        target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return manifest
    except Exception:
        # No partial output can be mistaken for a verified release.
        shutil.rmtree(output_dir, ignore_errors=True)
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prism", type=Path, required=True)
    p.add_argument("--inventory", type=Path,
                   default=ROOT / "inventory/mc-1.8.9-ornithe-2026-11-07.json")
    p.add_argument("--approvals", type=Path, required=True)
    p.add_argument("--upstream-lock", type=Path,
                   default=ROOT / "inventory/github-release-lock.mc-1.8.9-ornithe.json")
    p.add_argument("--notices", type=Path, required=True)
    p.add_argument("--sources", type=Path, required=True)
    p.add_argument("--defaults", type=Path,
                   default=ROOT / "defaults/mc-1.8.9-ornithe")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--release", required=True)
    p.add_argument("--minimum-launcher-version", required=True)
    args = p.parse_args()
    try:
        manifest = build(args.prism, args.inventory, args.approvals, args.notices,
                         args.sources, args.defaults, args.output, args.release,
                         args.minimum_launcher_version, upstream_lock=args.upstream_lock)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print(f"RELEASE BLOCKED: {exc}", file=sys.stderr)
        return 1
    print(f"Release candidate staged: {len(manifest['files'])} files; NO UPLOAD performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
