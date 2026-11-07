"""Guard rail tests for the six-asset publication workflow without uploading files."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_manifests import load_json
from assemble_189_release_ci import must, source_version_check
from publish_189_ci import TAG

class FullOriginalSelection(unittest.TestCase):
    def test_six_private_and_five_public(self):
        inv=load_json(ROOT/"inventory/mc-1.8.9-ornithe-2026-11-07.json")
        lock=load_json(ROOT/"inventory/github-release-lock.mc-1.8.9-ornithe.json")
        pins=load_json(ROOT/"inventory/owned-source-pins.mc-1.8.9-ornithe.json")
        self.assertEqual(len(inv["mods"]),11)
        self.assertEqual(len(lock["verified"]),5)
        self.assertEqual(len(lock["pending"]),6)
        self.assertEqual(set(pins["assets"]),{x["id"] for x in lock["pending"]})
        self.assertNotIn("tflcore",{x["id"] for x in lock["verified"]})
        self.assertEqual(pins["tag"],TAG)
        self.assertEqual(pins["assets"]["lucerna"]["version"],"0.1.5-tfl.2")
        self.assertEqual(pins["assets"]["amplio"]["version"],"0.1.1+1.8.9")
    def test_source_revision_not_ever_latest(self):
        pins=load_json(ROOT/"inventory/owned-source-pins.mc-1.8.9-ornithe.json")
        for item in pins["assets"].values():
            self.assertRegex(item["commit"],r"^[0-9a-f]{40}$")
    def test_license_family_matches(self):
        pins=load_json(ROOT/"inventory/owned-source-pins.mc-1.8.9-ornithe.json")
        self.assertEqual(pins["assets"]["soundfix"]["license"],"LGPL-3.0-only")
        self.assertEqual(pins["assets"]["legacy-lwjgl3"]["license"],"LGPL-2.1-only")
        self.assertEqual(pins["assets"]["pulse"]["license"],"GPL-3.0-only")
        self.assertEqual(pins["assets"]["tflcore"]["license"],"GPL-3.0-only")
        self.assertIn("NVIDIA",pins["assets"]["amplio"]["nativeNotice"])
    def test_builder_is_fail_closed(self):
        with self.assertRaises(ValueError):
            must(False,"not approved")

if __name__=="__main__":
    unittest.main()
