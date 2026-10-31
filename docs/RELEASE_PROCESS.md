# GitHub-only release process (design + staging)

## Existing state

- Public source-of-truth and distribution repo: **TFLClientSelection**, exists; all manifests, review docs, catalog files, signatures and GitHub Release binaries live here.
- No JAR binaries or source archives uploaded yet.
- No active published channel. Drafts are not a release.
- No signing key, signature service or production release publisher installed yet.

## Target lifecycle

1. **Curate** exactly compatible mod versions per Minecraft/loader target; freeze their Git commit, license, jar bytes, SHA-256 and notices/source obligations.
2. **Import approved JARs** from an upstream build or reproducible local build into temporary protected staging **outside Git history**. Repeatable build preferred. Do not depend on Modrinth at install time.
3. **Build compliance bundle**: include per-artifact full license notices and GPL/LGPL corresponding source archives. Archive each source tree with required build scripts and modifications, not just a GitHub link. Record exact sha/bytes.
4. **Produce release manifest**: copy validated draft to `releases/<targetId>/<release>.json`; set status=published only after real binary evidence, loader boot tests and approval. Pin `loaderVersion` and `javaMajor`. Publish `sha256-<digest>.bin` assets; `manifest.json` and `manifest.json.sig`, `notices-<sha>.zip`, and necessary `source-<sha>.zip`.
5. **Sign** exact UTF-8 manifest and catalog bytes offline or in protected CI using Ed25519. Do not expose keys to untrusted PR workflows. Verify signatures using pinned public key in launcher integration tests.
6. **Upload immutable Release** to this existing public GitHub repository with tag `selection-<targetId>-v<release>`. Verify HTTP-fetched Release assets against recorded hash/length.
7. **Publish channel pointer**: increment the monotonic `generation` and edit `catalog/current.json`; re-sign `catalog/current.json.sig` in a single verified commit in the same repository. This is the only mutable routing entry. Promotion stable/beta/dev points to the same signed immutable release; do not edit old manifest bytes.
8. **Smoke test from TFL Client** on Windows/Linux/macOS where supported; verify launch, unknown-mod quarantine, offline cached launch, interrupted update, rollback, incompatible loader and corrupted blob.
9. **Retain** all signed releases and source archives while supported installs depend on them; do not rewrite or delete historical assets casually.

## Design constraints for publisher

GitHub Actions on pull requests must have **read-only** permissions. A publisher is a separate protected manual workflow in this same public repository, never triggered by an untrusted pull request. A future dedicated publisher triggered by **manual approval** in a protected GitHub Actions Environment may use a short-lived repository-scoped `GITHUB_TOKEN` with `contents: write`; the signing key must remain an environment secret unavailable to PRs. Neither the launcher nor published catalog contains those credentials.

Do not add auto-publish workflow until protected signing keys exist and the first release's legal and loader approvals are complete.

## QA gates

- Static: `python scripts/validate_manifests.py`
- Unit: `python -m unittest discover -s tests -v`
- Release: actual archive hashes/sizes, license archive/source completeness, signature verification and binary scanning
- Launch: correct Java and loader pin, cold install, incremental update, repair, rollback and offline behavior

## GitHub limits

GitHub Releases supports up to **1,000 assets per release** and **2 GiB per asset** (official docs); if we approach limits, bundle items deterministically while preserving per-file hash metadata and incremental behavior. These are future scaling considerations, not a reason to introduce a VPS.

https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
