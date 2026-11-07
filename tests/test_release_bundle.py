"""End-to-end synthetic tests of binary release staging and rights gates.

All binaries generated here are synthetic test fixtures, not third-party assets.
"""
from __future__ import annotations
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_release_bundle import build, load_approvals
from validate_manifests import SOURCE_REQUIRED
from verify_release_assets import verify_notices, verify_one

MOD_IDS = ["amplio", "argentum", "argentum-extras", "cera", "legacy-lwjgl3",
           "lucerna", "osl", "pulse", "sarcio", "soundfix", "tflcore"]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fake_jar(mod_id: str) -> bytes:
    buf = io.BytesIO()
    with ZipFile(buf, "w") as jar:
        jar.writestr("fabric.mod.json", json.dumps({"id": mod_id, "version": "1.0.0"}))
        if mod_id == "amplio":
            jar.writestr("natives/windows-x86_64/nvngx_dlss.dll", b"SYNTHETIC-NOT-NVIDIA")
    return buf.getvalue()


def fixture(root: Path):
    source_zip = root / "prism.zip"
    approvals = {"schemaVersion": 1, "mods": {}}
    inv = {"targetId": "mc-1.8.9-ornithe", "mods": []}
    notices, sources = root / "notices", root / "sources"
    notices.mkdir()
    sources.mkdir()
    with ZipFile(source_zip, "w") as prism:
        for mod_id in MOD_IDS:
            name = mod_id + ".jar"
            payload = fake_jar(mod_id)
            prism.writestr("minecraft/mods/" + name, payload)
            sha = digest(payload)
            inv["mods"].append({
                "id": mod_id, "version": "1.0.0", "filename": name,
                "installPath": "mods/" + name, "sha256": sha,
                "bytes": len(payload), "assetName": f"sha256-{sha}.bin"})
            lic = "GPL-3.0-only" if mod_id in ("tflcore", "pulse") else "MIT"
            basis = "explicit-permission" if mod_id in ("argentum", "argentum-extras", "cera") else "open-source-license"
            origin = {
                "project": mod_id, "projectVersion": "1.0.0",
                "sourceRepository": f"https://github.com/example/{mod_id}",
                "sourceRevision": "deadbeef1234",
                "licenseSpdx": lic,
                "licenseEvidenceUrl": f"https://github.com/example/{mod_id}/LICENSE",
                "redistributionBasis": basis,
                "permissionEvidenceUrl": f"https://github.com/example/{mod_id}/PERMISSION",
            }
            approvals["mods"][mod_id] = {
                "status": "approved", "origin": origin,
                "nativeClearance": {
                    "natives/windows-x86_64/nvngx_dlss.dll": "https://github.com/example/test/license",
                } if mod_id == "amplio" else {},
            }
            (notices / f"{mod_id}.txt").write_text(f"{mod_id} LICENSE, SYNTHETIC TEST ONLY", encoding="utf-8")
            if lic in SOURCE_REQUIRED:
                with ZipFile(sources / (mod_id + ".zip"), "w") as src:
                    src.writestr("src/Example.java", "class Example {}")
    inv["sourceZipSha256"] = digest(source_zip.read_bytes())
    inventory_path = root / "inventory.json"
    inventory_path.write_text(json.dumps(inv))
    approvals_path = root / "approvals.json"
    approvals_path.write_text(json.dumps(approvals))
    return source_zip, inventory_path, approvals_path, notices, sources


class ReleaseBundle(unittest.TestCase):
    def test_unapproved_binary_cannot_stage(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            z, inventory, approvals, notices, sources = fixture(root)
            record = json.loads(approvals.read_text())
            record["mods"]["argentum"]["status"] = "pending"
            approvals.write_text(json.dumps(record))
            dist = root / "dist"
            with self.assertRaisesRegex(ValueError, "argentum.*redistribution"):
                build(z, inventory, approvals, notices, sources, root / "defaults",
                      dist, "1.0.0", "0.1.0")
            self.assertFalse(dist.exists())

    def test_native_clearance_is_required(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            z, inventory, approvals, notices, sources = fixture(root)
            record = json.loads(approvals.read_text())
            record["mods"]["amplio"]["nativeClearance"] = {}
            approvals.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "native library"):
                build(z, inventory, approvals, notices, sources, root / "defaults",
                      root / "dist", "1.0.0", "0.1.0")

    def test_synthetic_release_and_notices(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            z, inventory, approvals, notices, sources = fixture(root)
            defaults = root / "defaults"
            (defaults / "config").mkdir(parents=True)
            (defaults / "config/test.json").write_text("{}")
            (defaults / "README.md").write_text("not a runtime asset")
            out = root / "dist"
            manifest = build(z, inventory, approvals, notices, sources, defaults,
                             out, "1.0.0", "0.1.0")
            self.assertEqual(sum(x["kind"] == "mod" for x in manifest["files"]), 11)
            self.assertEqual(sum(x["kind"] == "config" for x in manifest["files"]), 1)
            self.assertEqual(sum("correspondingSourceAsset" in x["origin"] for x in manifest["files"]), 2)
            # Two identical source archives intentionally share one content-addressed blob.
            self.assertEqual(len(list((out / "assets").glob("source-*.zip"))), 1)
            failures = []
            verify_notices(out / "assets", manifest, failures)
            self.assertEqual(failures, [])
            for entry in manifest["files"]:
                verify_one(entry, out / "assets", entry["id"], failures)
            self.assertEqual(failures, [])


    def test_reviewed_six_upstream_mods_have_no_TFL_mirror(self):
        lock = load_json(ROOT / "inventory/github-release-lock.mc-1.8.9-ornithe.json")
        inv = load_json(ROOT / "inventory/mc-1.8.9-ornithe-2026-11-07.json")
        by_id = {m["id"]: m for m in inv["mods"]}
        self.assertEqual(len(lock["verified"]), 6)
        self.assertEqual(len(lock["pending"]), 5)
        for upstream in lock["verified"]:
            source = by_id[upstream["id"]]
            self.assertEqual((upstream["sha256"], upstream["bytes"]),
                             (source["sha256"], source["bytes"]))
            self.assertEqual(upstream["download"]["asset"], source["filename"])

    def test_no_approvals_file(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises((ValueError, OSError)):
                load_approvals(Path(td) / "missing.json")


if __name__ == "__main__":
    unittest.main()
