# TFL Selection — official, locked Minecraft distributions

This is the **public source-of-truth** for TFL Selection, the official Minecraft mod selection installed by the open-source **TFL Client** launcher.

- Minecraft **1.8.9**: **Ornithe Gen2** (independent bootstrap integration required in the launcher).
- Modern Minecraft: **Fabric**, starting with the **26.3** target.
- **Locked Selection**: TFLives chooses the entire mod set. The launcher must not offer user-installed, removed, updated or overridden mods inside Selection.
- **No Modrinth in the Selection install/update path.** Author-hosted, pinned GitHub Releases can serve rights-restricted mods directly; remaining redistributable JARs use TFL-controlled GitHub Releases. Every file is pinned by SHA-256.
- **No VPS, API server or R2 required** for the distribution design.
- **Auto-discovery:** newly published compatible Minecraft versions and updates to any Selection modpack appear through the signed catalog, **without publishing a new launcher build** for routine pack-content changes.
- **No .mrpack** for official Selection. Existing normal launcher instances and their capabilities are a separate product mode.
- Players can alter Minecraft settings and keep worlds/saves, but not the managed mod selection.
- Files delivered to the player remain inspectable; the goal is modest friction against casual copying, not unbreakable DRM.

## Repositories and ownership

| Repository | Visibility | Responsibility |
| --- | --- | --- |
| TFLClientSelection (this repository) | **Public** | Authoring, manifests, curated inventory, licensing evidence, test/verification and release preparation |
| GitHub Releases **in this same repository** | **Public** | Immutable binary assets, detached signatures and signed channel catalog |
| TFLClient | Public | Bootstrapping, downloads, cache, integrity, rollback, locked UI and launch |
| TFLClientMOD | Independent | Building/providing pinned TFL Core artifacts |

This repository and release data are public. Never disguise a public repo to imply protection, and never ship credentials in a client.

## Status

This repository contains drafts and **metadata-only Prism 1.8.9 import inventory**; no active releases. No mods, source snapshots, signature keys, published catalogs or launchable packs have been uploaded. A local gated release builder, Ed25519 signing and manual GitHub CLI publisher are present. **No public binary Release has been published**: permissions, corresponding source, signature keys and end-to-end launcher boot QA remain outstanding. The launcher integration is not yet implemented.

## Docs

- [Architecture and release design](docs/ARCHITECTURE.md)
- [Exact release contract](docs/LAUNCHER_CONTRACT.md)
- [Launcher code audit and integration plan](docs/LAUNCHER_INTEGRATION.md)
- [Prism Launcher ZIP import and cleanup](docs/PRISM_IMPORT.md)
- [Minecraft 1.8.9 real Prism ZIP import audit](docs/MC1_8_9_PRISM_IMPORT_REVIEW.md)
- [Pinned original-author GitHub Releases — 6 verified, 5 pending](docs/MIXED_GITHUB_RELEASE_DELIVERY.md)
- [Rights approval template](licensing/approvals.mc-1.8.9-ornithe.template.json)
- [Guarded release builder](scripts/build_release_bundle.py), [Ed25519 signer](scripts/selection_sign.py), [catalog promotion](scripts/selection_promote.py), [GitHub Release publisher](scripts/publish_approved_release.py)
- [Privacy-safe reviewed defaults for 1.8.9](defaults/mc-1.8.9-ornithe/config)
- [Dynamic catalog discovery and updates](docs/AUTOMATIC_CATALOG_AND_UPDATES.md)
- [File layout and release operations](docs/RELEASE_PROCESS.md)
- [Licensing and security policy](docs/SECURITY_AND_LICENSING.md)
- [Target compatibility / inventory plan](docs/SELECTION_MATRIX.md)
- [Fabric 26.3 — review of 56 proposed mod JARs](docs/MC26_3_MOD_REVIEW.md)
- [Fabric 26.3 — versioned candidate inventory (CSV)](docs/inventory/mc-26.3-fabric-candidates.csv)

## Static validation

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate_manifests.py
python -m unittest discover -s tests -v
```

The pinned-schema and path validation CI is a **first gate only**, not legal clearance or proof the binaries exist and boot. Release publication will require additional manual and automated checks.
