#!/usr/bin/env python3
"""Build exact 1.8.9 Selection candidate from six draft GitHub Release assets.

GitHub Actions downloads five public upstream JARs from author Releases. The
owner's six unchanged .bin JARs and private TFL Core source ZIP are required.
Fail closed on any missing/different hash or source/notice; never auto-upgrade.
THIS SCRIPT CREATES ONLY A LOCAL CANDIDATE. It does not publish or sign.
"""
from __future__ import annotations
import argparse
from contextlib import closing
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.request import Request, urlopen
from zipfile import ZipFile, ZIP_STORED

from build_release_bundle import build, sha256_file
from validate_manifests import ROOT, load_json

INV_PATH = ROOT / "inventory/mc-1.8.9-ornithe-2026-11-07.json"
LOCK_PATH = ROOT / "inventory/github-release-lock.mc-1.8.9-ornithe.json"
PIN_PATH = ROOT / "inventory/owned-source-pins.mc-1.8.9-ornithe.json"
MAX_SOURCE_BYTES = 400 * 1024 * 1024

def must(test: bool, why: str) -> None:
    if not test:
        raise ValueError(why)

def safe_zip(z: ZipFile, label: str) -> None:
    infos = z.infolist()
    must(len(infos) < 100000, label + " too many files")
    must(sum(x.file_size for x in infos) < 4 * 1024**3, label + " source archive too large")
    for x in infos:
        p = x.filename
        must(not p.startswith("/") and "\\" not in p
             and not any(a in ("", "..") for a in p.strip("/").split("/")),
             label + " unsafe ZIP path")
        must((x.external_attr >> 16) & 0o170000 != 0o120000,
             label + " contains symbolic link")

def sha_matches(path: Path, item: dict, label: str) -> None:
    must(path.is_file() and not path.is_symlink(), label + " missing or symlink")
    sha, length = sha256_file(path)
    must((sha, length) == (item["sha256"], item["bytes"]),
         label + " does not match exact Prism JAR SHA-256 and bytes")

def run(*cmd: str) -> None:
    subprocess.run(cmd, check=True)

def source_download(repo: str, commit: str, dest: Path) -> None:
    must(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) is not None,
         "invalid source GitHub repo")
    must(re.fullmatch(r"[a-f0-9]{40}", commit) is not None,
         "source must be pinned to a full commit SHA")
    url = "https://api.github.com/repos/" + repo + "/zipball/" + commit
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "TFL-Selection-Release-Assembler"}
    token = os.getenv("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = "Bearer " + token
    with closing(urlopen(Request(url, headers=headers), timeout=120)) as stream:
        with dest.open("wb") as output:
            remaining = MAX_SOURCE_BYTES
            while True:
                part = stream.read(min(1024 * 1024, remaining + 1))
                if not part:
                    break
                remaining -= len(part)
                must(remaining >= 0, "source archive exceeds max download")
                output.write(part)
    with ZipFile(dest) as z:
        safe_zip(z, repo)
        must(any(m.filename.endswith((".java", ".kt", ".c", ".cpp"))
                 for m in z.infolist()), "empty corresponding-source tree: " + repo)

def find_source_file(archive: Path, path_suffix: str) -> bytes | None:
    with ZipFile(archive) as z:
        matches = [x for x in z.infolist()
                   if not x.is_dir()
                   and (x.filename == path_suffix or x.filename.endswith("/" + path_suffix))]
        if len(matches) != 1:
            return None
        must(matches[0].file_size <= 2 * 1024 * 1024, "oversized license/source text")
        return z.read(matches[0])

def source_version_check(archive: Path, mod_id: str, version: str) -> None:
    path = "build.gradle.kts" if mod_id == "pulse" else "gradle.properties"
    source = find_source_file(archive, path)
    must(source is not None, mod_id + " missing version source file")
    text = source.decode("utf-8", "replace")
    # Source declares the exact *version*, not necessarily bit-for-bit deterministic build provenance.
    short = version.removesuffix("+1.8.9").removesuffix("+mc1.8.9")
    must(short in text, mod_id + " pinned source commit declares a different version")

def source_notices(mod_id: str, source: Path, jar: Path,
                   reference_licenses: dict[str, bytes]) -> bytes:
    parts = [f"MOD: {mod_id}\nThis is the original upstream license/notice text.\n"
             "Source snapshots accompany the exact pinned JAR.\n\n".encode()]
    main = find_source_file(source, "LICENSE")
    if mod_id == "soundfix" and main is None:
        parts.append(b"SoundFix fabric.mod.json declares LGPL-3.0.\n"
                     b"Full LGPLv3 and GPLv3 license texts included below.\n\n")
        main = reference_licenses["LGPL-3.0-only"]
        parts.append(reference_licenses["GPL-3.0-only"])
    if mod_id == "tflcore" and main is None:
        # Original private source may be packaged without top-level LICENSE.
        parts.append(b"TFL Core fabric.mod.json declares GPL-3.0-only.\n\n")
        main = reference_licenses["GPL-3.0-only"]
    must(main is not None and len(main) > 100,
         mod_id + " license text absent from pinned corresponding source")
    parts.append(main)
    copying = find_source_file(source, "COPYING")
    if copying:
        parts.extend([b"\n\nADDITIONAL COPYING TERMS:\n", copying])
    with ZipFile(jar) as z:
        for filename in ("META-INF/LICENSE", "META-INF/NOTICE", "LICENSE",
                         "META-INF/licenses/NVIDIA-DLSS.txt",
                         "META-INF/licenses/AMD-FSR.txt", "natives/LICENSE-tracy"):
            if filename in z.namelist():
                info = z.getinfo(filename)
                must(info.file_size <= 200000, "oversized embedded notice")
                parts.extend([("\n\nEMBEDDED " + filename + ":\n").encode(), z.read(filename)])
    return b"\n".join(parts) + b"\n"

def assemble(owner_assets: Path, result_dir: Path, public_upstream: bool = True) -> dict:
    inv, lock, pins = load_json(INV_PATH), load_json(LOCK_PATH), load_json(PIN_PATH)
    must(inv["targetId"] == lock["targetId"] == pins["targetId"], "target mismatch")
    original = {m["id"]: m for m in inv["mods"]}
    public = {m["id"]: m for m in lock["verified"]}
    owned = {m["id"]: m for m in lock["pending"]}
    must(len(original) == 11 and len(public) == 5 and len(owned) == 6, "invalid fixed pack")
    must(not result_dir.exists() or not any(result_dir.iterdir()), "output already populated")
    from verify_uploaded_189 import validate as check_upload
    errs = check_upload(owner_assets)
    must(not errs, "; ".join(errs))
    private_src_info = pins["assets"]["tflcore"]
    private_source = owner_assets / private_src_info["privateSourceAsset"]
    sha_matches(private_source, {"sha256":private_src_info["privateSourceSha256"],
                                 "bytes":private_src_info["privateSourceBytes"]}, "TFL Core source ZIP")
    with ZipFile(private_source) as z:
        safe_zip(z, "private TFL Core source")
        must(any(i.filename.endswith((".java", ".kt")) for i in z.infolist()),
             "TFL Core source archive has no Java/Kotlin source")
    with tempfile.TemporaryDirectory(prefix="tfl-189-assemble-") as temporary:
        tmp = Path(temporary)
        jar_dir, src_dir, notices_dir = tmp / "jars", tmp / "sources", tmp / "notices"
        jar_dir.mkdir()
        src_dir.mkdir()
        notices_dir.mkdir()
        for mod_id in owned:
            meta = original[mod_id]
            shutil.copyfile(owner_assets / meta["assetName"], jar_dir / meta["filename"])
        if public_upstream:
            for mod_id, pinned in public.items():
                download = pinned["download"]
                repo, tag, name = download["repository"], download["tag"], download["asset"]
                dest = tmp / ("upstream-" + mod_id)
                dest.mkdir()
                run("gh", "release", "download", tag, "--repo", repo,
                    "--pattern", name, "--dir", str(dest))
                candidate = dest / name
                sha_matches(candidate, original[mod_id], "upstream " + mod_id)
                shutil.copyfile(candidate, jar_dir / name)
        else:
            # Synthetic fixture option intended for offline unit tests only.
            for mod_id in public:
                meta = original[mod_id]
                candidate = owner_assets / ("upstream-" + meta["filename"])
                sha_matches(candidate, meta, "test upstream " + mod_id)
                shutil.copyfile(candidate, jar_dir / meta["filename"])
        source_contents = {}
        for mod_id, pin in pins["assets"].items():
            if mod_id == "tflcore":
                shutil.copyfile(private_source, src_dir / (mod_id + ".zip"))
            else:
                source_download(pin["repo"], pin["commit"], src_dir / (mod_id + ".zip"))
                source_version_check(src_dir / (mod_id + ".zip"), mod_id, pin["version"])
            source_contents[mod_id] = src_dir / (mod_id + ".zip")
        lgl = find_source_file(source_contents["lucerna"], "LICENSE")
        gpl = find_source_file(source_contents["pulse"], "LICENSE")
        must(bool(lgl) and bool(gpl), "GPL/LGPL reference license text unavailable")
        refs = {"LGPL-3.0-only": lgl, "GPL-3.0-only": gpl}
        for mod_id, pin in pins["assets"].items():
            notice = source_notices(mod_id, source_contents[mod_id],
                                    jar_dir / original[mod_id]["filename"], refs)
            (notices_dir / (mod_id + ".txt")).write_bytes(notice)
        approvals = {"schemaVersion": 1, "mods": {}}
        for mod_id, pin in pins["assets"].items():
            src_revision = pin["commit"]
            repo = pin["repo"]
            url = f"https://github.com/{repo}"
            if mod_id == "tflcore":
                license_url = url + "/releases/tag/v0.5.0-visual-preview.1"
            elif mod_id == "soundfix":
                license_url = f"{url}/blob/{src_revision}/src/main/resources/fabric.mod.json"
            else:
                license_url = f"{url}/blob/{src_revision}/LICENSE"
            origin = {"project":mod_id,"projectVersion":original[mod_id]["version"],
                      "sourceRepository":url,"sourceRevision":src_revision,
                      "licenseSpdx":pin["license"],"licenseEvidenceUrl":license_url,
                      "redistributionBasis":"open-source-license"}
            approval = {"status":"approved", "origin":origin, "nativeClearance":{}}
            with ZipFile(jar_dir / original[mod_id]["filename"]) as mod_jar:
                for name in mod_jar.namelist():
                    if not name.lower().endswith((".dll", ".so", ".dylib")):
                        continue
                    if mod_id == "amplio" and "nvngx_dlss" in name:
                        evidence = url + "/blob/" + src_revision + "/src/main/resources/META-INF/licenses/NVIDIA-DLSS.txt"
                    elif mod_id == "pulse" and "Tracy" in name:
                        evidence = url + "/blob/" + src_revision + "/src/main/resources/natives/LICENSE-tracy"
                    elif mod_id == "pulse" and ("asyncProfiler" in name or "attach_hotspot" in name):
                        evidence = "https://github.com/async-profiler/async-profiler/blob/master/LICENSE"
                    else:
                        evidence = url + "/blob/" + src_revision + "/LICENSE"
                    approval["nativeClearance"][name] = evidence
            approvals["mods"][mod_id] = approval
        # The upstream direct-download assets are not TFL-hosted, so their
        # license approval entries are placeholders but never used to stage.
        for mod_id in public:
            approvals["mods"][mod_id] = {"status": "pending"}
        approvals_path = tmp / "approvals.json"
        approvals_path.write_text(json.dumps(approvals), encoding="utf-8")
        assembled_prism = tmp / "exact-11-mods.zip"
        with ZipFile(assembled_prism, "w", ZIP_STORED) as z:
            z.writestr("mmc-pack.json", json.dumps({"components": [
                {"uid":"net.minecraft","version":"1.8.9"},
                {"uid":"net.fabricmc.fabric-loader","version":"0.20.1"}]}))
            for mod in inv["mods"]:
                z.write(jar_dir / mod["filename"], "minecraft/mods/" + mod["filename"])
        import_copy = dict(inv)
        import_copy["sourceZipSha256"] = sha256_file(assembled_prism)[0]
        import_path = tmp / "inventory.json"
        import_path.write_text(json.dumps(import_copy), encoding="utf-8")
        manifest = build(assembled_prism, import_path, approvals_path, notices_dir,
                         src_dir, ROOT / "defaults/mc-1.8.9-ornithe",
                         result_dir, pins["release"], "0.1.0",
                         upstream_lock=LOCK_PATH)
    from verify_release_assets import verify_one, verify_notices
    errors: list[str] = []
    assets = result_dir / "assets"
    for file in manifest["files"]:
        if "download" not in file:
            verify_one(file, assets, file["id"], errors)
    verify_one(manifest["noticesAsset"], assets, "notices", errors)
    if "iconAsset" in manifest:
        verify_one(manifest["iconAsset"], assets, "official icon", errors)
    verify_notices(assets, manifest, errors)
    must(not errors, "; ".join(errors))
    for mod_id in public:
        must(not (assets / original[mod_id]["assetName"]).exists(),
             "author-hosted mod cannot be rehosted")
    must(sum(x["kind"]=="mod" for x in manifest["files"]) == 11, "incomplete 11-mod manifest")
    (result_dir / "provenance-review.json").write_text(json.dumps({
        "originalZipSha256": inv["sourceZipSha256"],
        "originalModDigests":{k:v["sha256"] for k,v in original.items()},
        "sourcePins": pins["assets"],
        "note":pins["sourceBuildNote"],
        "sourceBuildEquivalenceProven":False,
        "humanReviewRequiredBeforePublicRelease":True
    },indent=2)+"\n",encoding="utf-8")
    return manifest

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uploaded-assets",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    try:
        manifest=assemble(args.uploaded_assets,args.output)
        print(f"Candidate built: {len(manifest['files'])} files and exactly 11 original mods; NO UPLOAD")
        return 0
    except Exception as e:
        print(f"BLOCKED: {type(e).__name__}: {e}",file=sys.stderr)
        shutil.rmtree(args.output,ignore_errors=True)
        return 1

if __name__=="__main__":
    raise SystemExit(main())
