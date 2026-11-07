"""The exact-file gate cannot be defeated with later versions or a fake .bin."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_uploaded_189 import validate, INV, LOCK, PINS

class UploadIntegrity(unittest.TestCase):
    def test_missing_six_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertTrue(any("Missing required pinned binary" in x for x in validate(Path(td))))
    def test_forged_tfl_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            data = json.loads(INV.read_text())
            lock = json.loads(LOCK.read_text())
            pin = json.loads(PINS.read_text())
            for row in lock["pending"]:
                mod = next(x for x in data["mods"] if x["id"] == row["id"])
                (folder / mod["assetName"]).write_bytes(b"not really a JAR")
            failures = validate(folder, data, lock, pin)
            self.assertTrue(any("size mismatch" in f for f in failures))
    def test_private_tflcore_is_not_an_upstream_download(self):
        lock = json.loads(LOCK.read_text())
        self.assertNotIn("tflcore", [x["id"] for x in lock["verified"]])
        self.assertIn("tflcore", [x["id"] for x in lock["pending"]])

if __name__ == "__main__":
    unittest.main()
