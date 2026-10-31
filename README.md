# TFL Selection — official, locked Minecraft distributions

This is the **public source-of-truth** for TFL Selection, the official Minecraft mod selection installed by the open-source **TFL Client** launcher.

- Minecraft **1.8.9**: **Ornithe Gen2** (independent bootstrap integration required in the launcher).
- Modern Minecraft: **Fabric**, starting with the **26.3** target.
- **Locked Selection**: TFLives chooses the entire mod set. The launcher must not offer user-installed, removed, updated or overridden mods inside Selection.
- **No Modrinth in the Selection install/update path.** Each approved third-party mod binary is mirrored and pinned by SHA-256 in TFL-controlled GitHub Releases.
- **No VPS, API server or R2 required** for the distribution design.
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

This repository currently contains **drafts only**. No mods, source snapshots, signature keys, published catalogs or launchable packs have been uploaded. The release publishing workflow and launcher integration remain to be implemented; public GitHub Release assets will be hosted **right here**.

## Docs

- [Architecture and release design](docs/ARCHITECTURE.md)
- [Exact release contract](docs/LAUNCHER_CONTRACT.md)
- [Launcher code audit and integration plan](docs/LAUNCHER_INTEGRATION.md)
- [File layout and release operations](docs/RELEASE_PROCESS.md)
- [Licensing and security policy](docs/SECURITY_AND_LICENSING.md)
- [Target compatibility / inventory plan](docs/SELECTION_MATRIX.md)

## Static validation

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate_manifests.py
python -m unittest discover -s tests -v
```

The pinned-schema and path validation CI is a **first gate only**, not legal clearance or proof the binaries exist and boot. Release publication will require additional manual and automated checks.
