#!/usr/bin/env python3
"""Ed25519 detached signatures for immutable Selection manifests and catalogs.

Key generation is local only. Never store the secret seed, PEM or private key in Git.
Use TFL_SELECTION_SIGNING_SEED_B64 only in a trusted protected publishing environment.
"""
from __future__ import annotations
import argparse
import base64
import os
from pathlib import Path
import sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

ENV_SEED = "TFL_SELECTION_SIGNING_SEED_B64"

def private_key_from_env() -> Ed25519PrivateKey:
    value = os.environ.get(ENV_SEED)
    if not value:
        raise ValueError("Missing signing key in protected environment")
    try:
        seed = base64.b64decode(value, validate=True)
    except Exception as exc:
        raise ValueError("Invalid base64 seed") from exc
    if len(seed) != 32:
        raise ValueError("Ed25519 seed must be 32 bytes")
    return Ed25519PrivateKey.from_private_bytes(seed)

def public_key_raw(private: Ed25519PrivateKey) -> bytes:
    return private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)

def signature_from_file(path: Path) -> str:
    signature = private_key_from_env().sign(path.read_bytes())
    return base64.b64encode(signature).decode("ascii") + "\n"

def verify_bytes(data: bytes, sig_b64: str, public_b64: str) -> None:
    signature = base64.b64decode(sig_b64.strip(), validate=True)
    pub = base64.b64decode(public_b64.strip(), validate=True)
    if len(pub) != 32 or len(signature) != 64:
        raise ValueError("Invalid Ed25519 public key or signature length")
    Ed25519PublicKey.from_public_bytes(pub).verify(signature, data)

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="action", required=True)
    key = sub.add_parser("generate", help="Generate a brand-new signing key LOCALLY")
    key.add_argument("--secret-output", type=Path, required=True)
    key.add_argument("--public-output", type=Path, required=True)
    sign = sub.add_parser("sign")
    sign.add_argument("file", type=Path)
    sign.add_argument("--output", type=Path)
    verify = sub.add_parser("verify")
    verify.add_argument("file", type=Path)
    verify.add_argument("--signature", type=Path, required=True)
    verify.add_argument("--public-key", type=Path, required=True)
    args = p.parse_args()
    try:
        if args.action == "generate":
            if args.secret_output.exists() or args.public_output.exists():
                raise ValueError("Refusing to overwrite existing signing keys")
            args.secret_output.parent.mkdir(parents=True, exist_ok=True)
            args.public_output.parent.mkdir(parents=True, exist_ok=True)
            private = Ed25519PrivateKey.generate()
            secret = private.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption())
            # Atomic exclusive creation, least privilege on POSIX.
            fd = os.open(args.secret_output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, "w") as stream:
                stream.write(base64.b64encode(secret).decode("ascii") + "\n")
            args.public_output.write_text(
                base64.b64encode(public_key_raw(private)).decode("ascii") + "\n",
                encoding="ascii")
            print(f"Private key stored locally at {args.secret_output}; do not commit or log it")
        elif args.action == "sign":
            out = args.output or Path(str(args.file) + ".sig")
            if out.exists():
                raise ValueError("Refusing to overwrite existing detached signature")
            out.write_text(signature_from_file(args.file), encoding="ascii")
            print(f"Signed raw bytes: {args.file} -> {out}")
        else:
            verify_bytes(args.file.read_bytes(), args.signature.read_text(encoding="ascii"),
                         args.public_key.read_text(encoding="ascii"))
            print(f"Ed25519 OK: {args.file}")
    except Exception as exc:
        print(f"Signature operation failed: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
