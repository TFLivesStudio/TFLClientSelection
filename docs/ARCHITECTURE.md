# Architecture — locked Selection, GitHub-only distribution

## Decisions (2026-10-31)

The user-selected behavior is **A: TFLives decides every mod**. Selection is a dedicated first-party Minecraft product, not a generic user-editable modpack. Version families are **1.8.9 / Ornithe Gen2** and **modern / Fabric** (first modern draft 26.3).

**Do not require VPS, Modrinth, R2, GitHub user authentication or private API keys at runtime.**

### Roles

```text
TFLClientSelection (PUBLIC, this ONE repository)
  curated drafts / manifests / license evidence / tests / approval
       |
       | protected/manual publish workflow (same repo, future)
       v
  catalog/current.json + catalog/current.json.sig (static Git main branch)
  GitHub Release: selection-<targetId>-v<version>
     manifest.json + manifest.json.sig
     sha256-<digest>.bin  [each owned/redistributable mod, config, etc.]
     notices-<digest>.zip [third-party license notices]
     source-<digest>.zip  [GPL/LGPL complete corresponding source]
       |
       | ordinary public HTTPS, no account/token
       v
TFLClient (PUBLIC, Rust/Tauri launcher)
  pinned signing key -> catalog verification -> pinned release
  verify manifest signature + digest -> cache -> staged install
  launch exact Minecraft/loader/TFL Core build from manifest
```

Selection is **not** responsible for Minecraft base game assets, Mojang auth or Java runtime distribution; these remain TFLClient responsibilities. The no-Modrinth requirement applies to **Selection's curated mod set**, not a promise of zero external services for a fresh Minecraft install.

### Why GitHub Releases, not JAR files in Git history

Every replaced JAR would inflate repository history and be directly visible. Use **one immutable Release asset per binary**, with content-addressed filenames and SHA-256 digests in manifests. Third-party author deletes/renames a Modrinth version? It does **not** break our already-mirrored approved asset. A TFL GitHub Release being unavailable remains a GitHub platform dependency, accepted for this design.

This public repository's code, release assets and catalog are discoverable. A neutral repo name/asset filenames are **not access control**. The source-of-truth repository is also public; drafts, scripts and release metadata are accessible. Do not treat repository naming as an access control. Users can still inspect the launcher's downloads, filesystem and process.

### Closed versus user data

- **Immutable/managed:** selected mod set, loader bootstrap selection, required generated pack files.
- **Mutable player data:** saves, screenshots, options, keybindings, account data, logs; do not erase or copy into release.
- TFL Client must never show 'install mod', 'add local mods', 'update mod', 'remove mod', 'import .mrpack' or 'export modpack' operations **for a Selection profile**.
- Enforcement must be on Rust command/service boundaries, not only hidden frontend controls.
- Extra `mods/` files are diagnosed and quarantined with a recoverable record (no silent deletion). Official managed files are repaired against signed manifest before launch.
- Player modifications to Minecraft options remain allowed; user saves never overwritten.

### Practical file layout on player PC

TFLClient controls the exact OS-specific application-data root.

```text
<TFL_CLIENT_DATA>/
  cache/selection/blobs/sha256/<digest>   # verified, stable local cache
  selection/profiles/<targetId>/          # instance metadata & player data
    saves/ screenshots/ options.txt/ config-user/
  selection/runtime/<targetId>/           # ephemeral/managed loader-visible files
    mods/*.jar
    config/*                  # managed config; seed-if-absent if user-editable
  selection/snapshots/<targetId>/         # last-known-good release + lockfile
```

Runtime filesystem locations are obscured from **normal instance UI**, but actual JARs remain readable once loaded. This is light organization, not DRM. On supported Fabric versions, custom mods directory may be possible, but must be verified; for Ornithe do **not** assume an equivalent exists. Prefer normal loader-visible paths within a private application-data root to unreliable bytecode/encrypted-memory tricks.

### Dependencies and security boundary

Selection does not support arbitrary mods. That does not mean other **normal** launcher instances lose Modrinth, .mrpack, import/export or user-installed mods. Only the official Selection profile is locked.

Both signed raw catalog and manifest need pinned Ed25519 keys and SHA-256 over exact manifest bytes. Local cache is content-addressed, only verified files can be installed. Download SHA validation without trusted signatures is insufficient.

Bootstrap loader version is **pinned**. For Ornithe Gen2, launcher integration is new work; a `loaderVersion` field in JSON does not make boot support appear.

### No secret client credentials

A public, open-source client must never contain GitHub PAT, release-write token, signing **private** key or GitHub App private key. A protected release workflow in this repository can use GitHub Actions' short-lived `GITHUB_TOKEN` with narrowly scoped `contents: write` for publication; only approved jobs receive signing secrets. PR jobs remain `contents: read`. There is **no** app-level API service required at launch.

### Permanent protocol, evolution allowed

Keep manifest `schemaVersion=2` backwards compatible for this generation. If the protocol ever needs a breaking change, introduce v3 with launcher compatibility gates; do not silently mutate v2 fields or overwrite published releases. "Permanent architecture" means stable responsibilities and invariants, not forbidding future bug fixes/security improvements.
