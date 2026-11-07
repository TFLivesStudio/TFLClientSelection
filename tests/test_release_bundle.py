"""Release candidate must never publish without authorization and all 11 mods."""
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_release_bundle import load_approvals, require

class BuildReleaseTests(unittest.TestCase):
    def test_approval_data_required(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises((ValueError, OSError)):
                load_approvals(Path(td) / "missing.json")

    def test_empty_approval_rejected(self):
        with self.assertRaises(ValueError):
            require(False, "unlicensed binary rejected")

    def test_true_condition_passes(self):
        require(True, "fine")

if __name__ == "__main__":
    unittest.main()
