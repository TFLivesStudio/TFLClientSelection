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
7. **Publish channel pointer and discoverable release**: increment the monotonic `generation` and edit `catalog/current.json`; re-sign `catalog/current.json.sig` in a single verified commit in the same repository. This is the only mutable routing entry. Adding a new Minecraft version also adds a new signed `targets[]` entry with supported loader and presentation metadata; modifying a modpack creates a **new** immutable release, not a mutation of the old release. Both actions are visible to a catalog-driven launcher after refresh. Promotion stable/beta/dev points to the same signed immutable release; do not edit old manifest bytes.
8. **Smoke test from TFL Client** on Windows/Linux/macOS where supported; verify launch, unknown-mod quarantine, offline cached launch, interrupted update, rollback, incompatible loader and corrupted blob.
9. **Retain** all signed releases and source archives while supported installs depend on them; do not rewrite or delete historical assets casually.

## Design constraints for publisher

GitHub Actions on pull requests must have **read-only** permissions. A publisher is a separate protected manual workflow in this same public repository, never triggered by an untrusted pull request. A future dedicated publisher triggered by **manual approval** in a protected GitHub Actions Environment may use a short-lived repository-scoped `GITHUB_TOKEN` with `contents: write`; the signing key must remain an environment secret unavailable to PRs. Neither the launcher nor published catalog contains those credentials.

Release preparation and local signing tooling are now provided as **scripts**, but no signing key is installed, no binaries are published, and there is no unattended public release publisher. Automatic channel discovery happens for already approved **signed** releases; it does **not** imply any arbitrary source commit publishes JARs.

## Repeatable publishing commands (after rights review and boot QA)

The latest native Prism export is used as byte-for-byte input; every JAR is checked against the committed inventory. Unapproved assets cannot be staged by the release builder. First create a private directory containing:

- `approvals.json`: a completed copy of `licensing/approvals.mc-1.8.9-ornithe.template.json`, with **documented authorization** for every mod and bundled native library. `status=approved` is an attestation from a reviewer, never a substitute for real permission.
- `notices/<mod-id>.txt`: full license/copyright notices for each mod.
- `sources/<mod-id>.zip`: corresponding source with build scripts at the precise revision, for LGPL/GPL artifacts.
- Original Prism ZIP, already SHA-256 pinned by inventory.

```powershell
python -m pip install -r requirements-dev.txt
python scripts/build_release_bundle.py --prism 'TFL Client 1.8.9.zip' --approvals approvals.json --notices notices --sources sources --output dist/selection-189 --release 1.0.0 --minimum-launcher-version 0.1.0
python scripts/verify_release_assets.py --manifest dist/selection-189/manifest.json --assets dist/selection-189/assets
```

Both commands **fail closed** if licenses, notices, source or JAR digests are invalid. The output is only a **local candidate**. The publisher must sign the raw manifest, upload all files from `assets/` plus `manifest.json` and its `.sig` into an immutable GitHub Release, verify download hashes, and only then sign and publish a new catalog generation. The signature key is created and managed locally or in a protected publishing environment; see `scripts/selection_sign.py` and `scripts/selection_promote.py`.

**Do not run a public upload of the 11 current JARs** until the ARR and NVIDIA rights review, complete corresponding sources and required boot QA have succeeded.

## QA gates

- Static: `python scripts/validate_manifests.py`
- Unit: `python -m unittest discover -s tests -v`
- Release: actual archive hashes/sizes, license archive/source completeness, signature verification and binary scanning
- Launch: correct Java and loader pin, cold install, incremental update, repair, rollback and offline behavior

## GitHub limits

GitHub Releases supports up to **1,000 assets per release** and **2 GiB per asset** (official docs); if we approach limits, bundle items deterministically while preserving per-file hash metadata and incremental behavior. These are future scaling considerations, not a reason to introduce a VPS.

https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
