# Release lifecycle

## 0. No release is currently live

`drafts/*.json` are **planning documents**, not live manifests. `catalog/catalog.template.json` intentionally points to no release; the launcher must not be directed to it as if stable were available.

## 1. Curate a target

For each Minecraft/loader version, verify actual bootability and Java requirements. Decide required/optional mod groups. Record exact artifact versions, official sources, SHA-256, byte lengths, install paths, platform constraints and licensing evidence. Keep TFL Core version pinned like every other mod; never point at an unversioned nightly asset.

## 2. Build immutable candidate

- Add files to a copied manifest in `releases/<targetId>/<release>/<channel>.json`; set status `published` only after rights and technical review.
- Upload approved private objects by content hash to private storage; verify server-side and client-side size/digest.
- Use `delivery.mode=upstream` for official sources when mirroring is not allowed.
- Verify launcher boot, mod loader compatibility, updates, offline launch and rollback against real machines.

## 3. Sign and publish

- Generate Ed25519 signature of **exact manifest bytes** using a controlled signing step (private key never exposed to untrusted PRs).
- Commit accompanying `.json.sig` and verify signature against pinned public keys in a release pipeline.
- Point `catalog/current.json` to the immutable manifest with its raw-byte SHA-256; sign exact catalog bytes too.
- Publish catalog and manifest via API; backend denies access to unapproved files and issues limited-scope presigned GETs.

The exact signer, trust-key rotation mechanism and backend are **not yet implemented**; no release should be considered production-ready before these are completed.

## 4. Channels and rollback

- `dev`: internal testing with controlled visibility.
- `beta`: external opt-in testing.
- `stable`: boot-tested, licensed and supported release.
- Rollback: repoint a channel to its **previous signed immutable** manifest; never overwrite historical artifacts.
- Preserve old blobs according to a documented retention period, including any snapshot still installed and supported.

## Local validation

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_manifests.py
python -m unittest discover -s tests -v
```

CI validates schemas, basic permission metadata, path safety, expected object keys and catalog cross-references. It does not access production storage.
