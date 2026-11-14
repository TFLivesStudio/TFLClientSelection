#!/usr/bin/env python3
"""Manually finalize a fully verified GitHub Release from an approved candidate.

Only run in a trusted, explicitly dispatched release workflow on main with an
Ed25519 signing seed secret. This program does not create or replace mod JARs.
Upstream five original-author JARs remain on their own GitHub Releases.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from selection_sign import private_key_from_env, public_key_raw, signature_from_file, verify_bytes
from selection_promote import prepare as promote_catalog
from validate_manifests import ROOT, load_json
from verify_uploaded_189 import INV, LOCK

REPO = "TFLivesStudio/TFLClientSelection"
TAG = "selection-mc-1.8.9-ornithe-v0.1.0-preview.1"

def must(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)

def gh(*args: str, capture: bool = False) -> str:
    cmd = ["gh", *args, "--repo", REPO]
    result = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE if capture else None)
    return (result.stdout or "").strip()

def file_hash(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def validate_draft(uploaded: Path, candidate: Path) -> dict:
    from verify_release_assets import verify_one, verify_notices
    from verify_uploaded_189 import validate
    errors = validate(uploaded)
    must(not errors, "Six original binary checks failed: " + "; ".join(errors))
    manifest=load_json(candidate/"manifest.json")
    must(manifest["distribution"]["repository"]==REPO
         and manifest["distribution"]["tag"]==TAG
         and manifest["status"]=="published", "Wrong signed release identity")
    own={row["id"] for row in load_json(LOCK)["pending"]}
    upstream={row["id"] for row in load_json(LOCK)["verified"]}
    entries={x["id"]:x for x in manifest["files"] if x["kind"]=="mod"}
    must(set(entries)==own|upstream and len(entries)==11,
         "Release contains wrong number of mods")
    inv={x["id"]:x for x in load_json(INV)["mods"]}
    for ident,e in entries.items():
        must(e["sha256"]==inv[ident]["sha256"] and e["bytes"]==inv[ident]["bytes"]
             and e["path"]==inv[ident]["installPath"],ident+" changed from ZIP")
        must(("download" in e)==(ident in upstream),ident+" wrong delivery source")
    errs=[]
    for e in manifest["files"]:
        if "download" not in e:
            verify_one(e,candidate/"assets",e["id"],errs)
            if "correspondingSourceAsset" in e["origin"]:
                verify_one(e["origin"]["correspondingSourceAsset"],candidate/"assets",
                           "source:"+e["id"],errs)
    verify_one(manifest["noticesAsset"],candidate/"assets","notices",errs)
    if "iconAsset" in manifest:
        verify_one(manifest["iconAsset"], candidate/"assets", "official icon", errs)
    verify_notices(candidate/"assets",manifest,errs)
    must(not errs,"Candidate incomplete: "+"; ".join(errs))
    return manifest

def commit_catalog(candidate: Path, public_key: Path, manifest: dict, channel: str) -> None:
    import os
    must(channel in ("beta","dev"),"first preview must be prerelease, never stable")
    release_file=ROOT/"releases"/manifest["targetId"]/(manifest["release"]+".json")
    signature_file=Path(str(release_file)+".sig")
    must(not release_file.exists() and not signature_file.exists(),
         "Release source-of-truth already exists; never overwrite")
    with tempfile.TemporaryDirectory(prefix="tflcatalog-") as temporary:
        out=Path(temporary)
        promote_catalog(candidate/"manifest.json",ROOT/"catalog/current.json",
                        ROOT/"catalog/current.json.sig",public_key,out,channel)
        release_file.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(candidate/"manifest.json",release_file)
        shutil.copyfile(candidate/"manifest.json.sig",signature_file)
        (ROOT/"catalog").mkdir(exist_ok=True)
        shutil.copyfile(out/"current.json",ROOT/"catalog/current.json")
        shutil.copyfile(out/"current.json.sig",ROOT/"catalog/current.json.sig")
        subprocess.run(["git","config","user.name","github-actions[bot]"],check=True)
        subprocess.run(["git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com"],check=True)
        subprocess.run(["git","add","keys/current.pub","catalog/current.json",
                        "catalog/current.json.sig",str(release_file.relative_to(ROOT)),
                        str(signature_file.relative_to(ROOT))],cwd=ROOT,check=True)
        subprocess.run(["python","scripts/validate_manifests.py"],cwd=ROOT,check=True)
        subprocess.run(["git","commit","-m",
                        f"release: TFLClient 1.8.9 {manifest['release']} [{channel}]"],
                       cwd=ROOT,check=True)
        subprocess.run(["git","push","origin","HEAD:main"],cwd=ROOT,check=True)

def finish(uploaded: Path, candidate: Path, channel: str, approval: bool) -> None:
    must(approval, "Operator must approve exact source snapshot and NVIDIA license conditions")
    must((ROOT/".git").exists(),"Only use in a trusted GitHub Actions checked-out main repo")
    proc=subprocess.run(["git","branch","--show-current"],cwd=ROOT,capture_output=True,text=True,check=True)
    must(proc.stdout.strip()=="main","Only release from main")
    record=json.loads(gh("release","view",TAG,"--json","isDraft,tagName",capture=True))
    must(record.get("isDraft") is True and record.get("tagName")==TAG,
         "Draft Release does not exist; refusal to overwrite a published release")
    manifest=validate_draft(uploaded,candidate)
    seed=private_key_from_env()
    key=base64.b64encode(public_key_raw(seed)).decode("ascii")+"\n"
    public_key=ROOT/"keys/current.pub"
    if public_key.exists():
        must(public_key.read_text().strip()==key.strip(),
             "Signing key changed; key rotation requires explicit separate process")
    else:
        public_key.parent.mkdir(parents=True,exist_ok=True)
        public_key.write_text(key,encoding="ascii")
    signature=candidate/"manifest.json.sig"
    must(not signature.exists(),"Refuse to overwrite existing manifest signature")
    signature.write_text(signature_from_file(candidate/"manifest.json"),encoding="ascii")
    verify_bytes((candidate/"manifest.json").read_bytes(),signature.read_text(),key)
    # Check no duplicate staged binary is re-uploaded (the draft already contains all six).
    inv={m["id"]:m for m in load_json(INV)["mods"]}
    originals={inv[x["id"]]["assetName"] for x in load_json(LOCK)["pending"]}
    planned=set(x.name for x in (candidate/"assets").iterdir() if x.is_file())
    must(originals <= planned, "Candidate lost original binary files")
    existing=json.loads(gh("release","view",TAG,"--json","assets",capture=True))["assets"]
    already={asset["name"] for asset in existing}
    must(originals <= already,"Owner has not uploaded all six exact mod assets")
    must(not any(name in already for name in planned-originals),
         "Release already contains generated assets, refusing overwrite")
    extras=already-originals-{"tflcore-source.zip"}
    must(not extras,"Unexpected asset already in draft: "+", ".join(sorted(extras)))
    additions=[str(p) for p in sorted((candidate/"assets").iterdir())
               if p.is_file() and p.name not in originals]
    additions += [str(candidate/"manifest.json"),str(signature),
                  str(candidate/"provenance-review.json")]
    gh("release","upload",TAG,*additions)
    # Download EVERY published asset back from GitHub and validate its raw SHA-256.
    with tempfile.TemporaryDirectory(prefix="tfl-release-remote-") as td:
        dest=Path(td)
        gh("release","download",TAG,"--dir",str(dest))
        expected=[*list((candidate/"assets").iterdir()),
                  candidate/"manifest.json",signature,candidate/"provenance-review.json"]
        for path in expected:
            remote=dest/path.name
            must(remote.is_file() and file_hash(remote)==file_hash(path),
                 "GitHub Release asset mismatch: "+path.name)
    gh("release","edit",TAG,"--draft=false","--prerelease")
    commit_catalog(candidate,public_key,manifest,channel)
    print(f"SUCCESS: public verified TFLClient 1.8.9 {channel} Release and signed catalog")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--uploaded-assets",type=Path,required=True)
    p.add_argument("--candidate",type=Path,required=True)
    p.add_argument("--channel",choices=["beta","dev"],default="beta")
    p.add_argument("--acknowledge-source-and-native-terms",action="store_true")
    opts=p.parse_args()
    try:
        finish(opts.uploaded_assets,opts.candidate,opts.channel,
               opts.acknowledge_source_and_native_terms)
        return 0
    except Exception as exc:
        print(f"RELEASE BLOCKED: {type(exc).__name__}: {exc}",file=sys.stderr)
        return 1

if __name__=="__main__":
    raise SystemExit(main())
