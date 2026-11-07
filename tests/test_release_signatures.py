import base64
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from selection_sign import signature_from_file, verify_bytes

class Signatures(unittest.TestCase):
    def test_sign_verify_and_tamper_detection(self):
        secret = bytes(range(32))
        private = Ed25519PrivateKey.from_private_bytes(secret)
        public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        with tempfile.TemporaryDirectory() as td:
            file = Path(td) / "manifest.json"
            file.write_bytes(b'{"schemaVersion":2}\n')
            with patch.dict(os.environ, {"TFL_SELECTION_SIGNING_SEED_B64": base64.b64encode(secret).decode()}):
                sig = signature_from_file(file)
            verify_bytes(file.read_bytes(), sig, base64.b64encode(public).decode())
            with self.assertRaises(Exception):
                verify_bytes(b'{"schemaVersion":1}\n', sig, base64.b64encode(public).decode())

    def test_no_key_no_signing(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "catalog.json"
            p.write_text("{}")
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ValueError):
                    signature_from_file(p)

if __name__ == "__main__":
    unittest.main()
