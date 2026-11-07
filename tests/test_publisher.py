import tempfile
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from publish_approved_release import compare_published, validate_local

class PublisherTests(unittest.TestCase):
    def test_remote_bytes_must_match_exactly(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            a = base / "assets"
            b = base / "downloaded"
            a.mkdir()
            b.mkdir()
            (a / "example.bin").write_bytes(b"abc")
            (b / "example.bin").write_bytes(b"abcd")
            with self.assertRaises(ValueError):
                compare_published(a, b)
            (b / "example.bin").write_bytes(b"abc")
            compare_published(a, b)

    def test_empty_staging_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                validate_local(Path(td))

if __name__ == "__main__":
    unittest.main()
