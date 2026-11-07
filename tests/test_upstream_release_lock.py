"""Static delivery-lock regressions for hybrid official+upstream GitHub assets."""
from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_upstream_lock import (verify_local, INVENTORY, LOCK, DRAFT)
from validate_manifests import load_json

class LockedGithubReleaseTests(unittest.TestCase):
    def setUp(self):
        self.inventory = load_json(INVENTORY)
        self.lock = load_json(LOCK)
        self.draft = load_json(DRAFT)

    def test_matches_original_11_jar_prism_zip(self):
        self.assertEqual(verify_local(self.inventory, self.lock, self.draft), [])

    def test_forged_upstream_digest_rejected(self):
        lock = copy.deepcopy(self.lock)
        lock["verified"][0]["sha256"] = "0" * 64
        self.assertTrue(verify_local(self.inventory, lock, self.draft))

    def test_missing_mod_blocked(self):
        draft = copy.deepcopy(self.draft)
        draft["files"].pop()
        self.assertTrue(verify_local(self.inventory, self.lock, draft))

    def test_no_unverified_fallback_url(self):
        draft = copy.deepcopy(self.draft)
        item = next(f for f in draft["files"] if f["id"] == "amplio")
        item["download"] = {"kind":"github-release", "repository":"Z1xus/amplio",
                            "tag":"v0.1.3", "asset":"amplio-0.1.3+1.8.9.jar"}
        self.assertTrue(verify_local(self.inventory, self.lock, draft))

if __name__ == "__main__":
    unittest.main()
