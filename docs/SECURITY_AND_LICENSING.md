# Security and third-party mod redistribution

## Confidentiality vs source availability

- Repository: **private**, controls who can inspect unpublished release plans.
- Launcher: **open source** by project decision, so it cannot safely embed a reusable secret.
- Installed packs: visible to the users who download them. This system protects the service, integrity and unreleased metadata, not the secrecy of installed JAR files.
- Never promise that a manifest, encryption, compression, renaming or short-lived URLs prevent extraction after installation.

## Security requirements

1. Release JSON and catalog cryptographically signed with Ed25519, public verification keys pinned to launcher. Keep private keys outside Git and isolated from arbitrary pull-request workflows.
2. SHA-256 and exact byte sizes enforced for every asset *after* download and before installation; hashes do **not** authenticate the catalog without a trusted signature.
3. Verify immutable object IDs and scope tickets to authorized asset IDs. Rate-limit and audit without recording bearer tokens.
4. Validate all local paths, path case-collisions, symlinks and file type expectations before any write. No archive extraction into arbitrary locations.
5. Verify upstream redirect targets and block loopback/private/link-local destinations; avoid dangerous protocols. CI's static URL validation is only a **first layer**.
6. Keep per-profile directories, secure caches, rollback snapshots and user-owned configuration changes separate.
7. Test malicious manifest inputs, interrupted downloads, corrupt blobs, replay/rollback policy, compromised mirror and revoked release scenarios before public launch.

## License checklist — required for each third-party artifact

- Record exact project, official URL, version, hash, upstream download location and license.
- Inspect the license and distribution terms for **that artifact/version**; `MIT`, `GPL` etc. are not equivalent to unconditional permission to redistribute everything bundled with a mod.
- If a mod's assets, dependencies or download service forbid mirroring, set `origin.redistribution=upstream-only` and use `delivery.mode=upstream`, or omit it.
- If owned by TFL, use `owned`. If third-party redistribution is affirmatively permitted, use `authorized` and record `evidenceUrl`.
- Comply with required attribution, license files, notices and source-code obligations when distributing binaries; private GitHub visibility does not waive obligations.
- Some commercial mods explicitly prohibit redistribution. Never upload them to private blob storage or ship keys/paid assets without permission.
- Antivirus and supply-chain checks must happen before any binary is accepted as a release.

## Pre-release gating

A green schema validator is **not** a proof of legal redistribution, real artifact existence, mod compatibility or malware safety. Human review is required; the release pipeline must additionally verify uploaded blob digests and signature validity. None of those publication/hosting integrations is active yet.
