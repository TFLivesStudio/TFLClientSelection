# TFL Client ↔ Selection Distribution contract v2

This is the **target integration contract**, not an existing endpoint. Public distribution repo `TFLivesStudio/TFLSelectionDistribution` has **not** yet been created.

## Discover channels without API server

1. Launcher downloads two static files from the public distribution repository's **pinned branch/path**, e.g. `catalog/current.json` and `catalog/current.json.sig`. HTTPS + response-size bound. Use a canonical GitHub raw URL; allow configured failover to Github Contents only when the same bytes and signature verify.
2. Verify detached Ed25519 signature over **the exact raw catalog bytes** using a public verification key shipped with the launcher. Signature file format: standard Base64 of a raw 64-byte Ed25519 signature. Never reserialize JSON before checking signature. Reject invalid keys, malformed signature, unauthorized target IDs or unknown schema versions.
3. Parse the catalog: `schemaVersion=2`, `distributionRepository=TFLivesStudio/TFLSelectionDistribution`, targets, and `stable|beta|dev` channel pointers. Each pointer contains exact release version, immutable release tag and SHA-256 digest of **raw** release manifest.
4. Construct exact GitHub URL for immutable public Release `https://github.com/<distributionRepository>/releases/download/<tag>/manifest.json` and `manifest.json.sig` **from whitelisted/pinned repository and validated tag fields**. Fetch bytes, verify catalog SHA-256, manifest Ed25519 signature, size and schema.
5. For each mod file in selected release, fetch `https://github.com/<distributionRepository>/releases/download/<tag>/<assetName>`. Asset name is always `sha256-<digest>.bin`, even if local install path is `mods/actual-mod.jar`.
6. Stream downloads to a separate temp path. Verify exact expected byte length and SHA-256 **before promoting to cache/install**. Reject untrusted redirects and unsupported protocols. Use retries, backoff and bounded concurrency.
7. Offline: only launch a previously installed, locally verified signed snapshot. Do not silently accept downgraded untrusted catalog, expired policy, different Minecraft/loader or unexpected files.

Do not use GitHub's `latest` release endpoint as the Selection release selection; it is not pinned per target/channel.

## Canonical files

- `schemas/catalog.v2.schema.json`: catalog (signed static branch file)
- `schemas/manifest.v2.schema.json`: single target's immutable release
- `catalog/catalog.template.json`: **template only**, zero published channels
- `drafts/*.json`: **unpublished design placeholders**
- `releases/<targetId>/<release>.json`: locally versioned published manifest, accompanied by `.json.sig`

Published `manifest.json` bytes must be byte-for-byte identical to the `releases/...json` file. Channel promotions only move signed catalog pointers. One immutable release can be promoted `dev -> beta -> stable` without changing manifest bytes.

## Manifest v2 fields

`packId=tfl-selection`, `selectionMode=locked`, `targetId`, `release`, `minecraft.version`, `minecraft.loader`, `minecraft.loaderVersion`, `minecraft.javaMajor`, `minecraft.bootstrap`, minimum launcher version, file list. Every file gives local relative path, kind, exact bytes, sha256, release asset name, install policy, license/provenance.

- No per-user optional `features`.
- No `mrpack_url`, third-party network delivery modes, Modrinth project ID or mutable upstream latest dependency.
- `installPolicy=managed`: exact official asset, verified before launch.
- `installPolicy=seed-if-absent`: defaults/user-editable config; do not overwrite user changes. **Mods always managed.**
- `noticesAsset`: archive of license/copyright notices, verified and exposed in UI.
- `correspondingSourceAsset`: GPL/LGPL release source snapshot; verified and downloadable but not loaded as a mod.

## Selection specific instance lifecycle

- A Selection profile has a **persistent identity**: `profileKind=tfl-selection`, `targetId`, chosen channel, installed release, lockfile with exact manifest hash, verified file hashes and last-good snapshot.
- Never reinterpret normal existing instances as Selection. Migrate only on explicit, validated conversion.
- Before game start: ensure pinned loader + Java, check pack integrity, reconcile managed mods, quarantine unknown mods, launch. On any failure preserve last good snapshot and visible error.
- Never use current `install_modpack_from_url` / community .mrpack paths for official Selection.
- No background 'latest' dependency resolution in Selection.
- Restrict add/remove/update/duplicate/export/import/open-folder operations for Selection at **backend command/service** level. Do not rely solely on hiding buttons.
- User saves/settings unaffected, no censorship of user choices outside the official Selection profile.
- Revalidation must be efficient: cached SHA-256 and metadata may assist, but security decisions cannot rely solely on timestamps.
- Ensure dynamic injection (e.g. first-party MP Guard JAR) is either pinned and in manifest for supported targets or explicitly excluded from the locked profile; do not introduce unmanaged mods at launch.

## Rust/Tauri client states

`not-installed -> resolving -> downloading -> verifying -> staged -> installed -> launching`.
On error transition to `repair-needed` or `rollback-ready`; never leave partially swapped `mods/`.
Emit progress events (files, bytes, integrity, repair, crash), support cancellation and recovery after crashes.

## Threat model (light protection, not DRM)

- Keep TFL managed assets under application-data directories, outside traditional user-managed `.minecraft/mods`.
- Content-addressed cache and neutral release asset names deter casual identification, without affecting performance.
- No in-memory JAR decryption, compression-on-every-launch, anti-debugging or fragile classloader hacks.
- Root/OS users can read their local JARs and reconstruct the pack. No false claim of unextractability.

## Signature rotation and rollback policy

Launcher ships an active set of trusted Ed25519 public keys (with identifiers in its code). A new signing key is introduced through a signed launcher update before old key retirement. Catalog signature should be verified against only explicitly trusted keys. A rollback release is allowed through a newly signed catalog pointer to an **already signed** immutable release; prevent involuntary replay of older cached catalogs by persisting last-seen catalog generation/sequence once this is added to the schema, while preserving documented offline-launch behavior. v2 does not yet include a monotonic sequence field: **do not advertise replay resistance as implemented**.
