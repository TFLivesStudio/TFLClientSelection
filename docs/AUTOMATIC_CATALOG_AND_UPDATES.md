# Dynamic catalog: publish new Selection modpacks without rebuilding TFL Client

**Product rule:** `TFL Selection` is the umbrella product name for all official, *locked* Minecraft modpacks, such as 1.8.9/Ornithe Gen2, 26.3/Fabric and later supported versions. TFLives—not end users—chooses every official mod. The launcher must not hardcode a fixed list of supported Minecraft **target IDs**.

## Contract already defined

- Public GitHub source and distribution: `TFLivesStudio/TFLClientSelection`.
- Published `catalog/current.json` plus detached `catalog/current.json.sig` are the **sole** authoritative index; SHA-256 and Ed25519 authenticate the contents.
- Each `targets[]` entry identifies `targetId`, `minecraftVersion`, `loader`, optional `displayName`, `summary`, `sortOrder`, and a `channels` object with `stable`, `beta`, `dev` pointers.
- A pointer contains immutable `release`, `tag`, and `manifestSha256`. The catalog `generation` integer increases **on every publication or channel change**.
- The actual immutable manifest lives both in `releases/<targetId>/<release>.json` and byte-for-byte in `manifest.json` GitHub Release asset. Every JAR is a separate, content-addressed `sha256-<digest>.bin` Release asset. No Modrinth is involved in downloads.
- Drafts do **not** appear in public product UI, even if their files are committed to GitHub.

## Required launcher behavior

1. **Start/open Selection**: fetch signed current catalog using conditional GET (ETag/Last-Modified where useful). Cache the last verified catalog and highest `generation` locally. Provide `Refresh` command.
2. **List**: render all targets *from signed `targets[]`*, filtered by channel availability and launcher compatibility. No hardcoded `1.8.9` and `26.3` entry list. Order by `sortOrder`, then `minecraftVersion` and `targetId`.
3. **New target detection**: a new published supported Fabric target with `stable` pointer automatically appears without a new launcher release. Ornithe targets also appear if the installed launcher already supports the required bootstrap. If loader or runtime requirements exceed built-in capabilities, show **"Actualizar launcher para instalar esta versión"**, not a broken installer.
4. **Check updates**: compare each installed `profileKind=tfl-selection` profile's trusted `targetId`, `channel`, installed `release` and `manifestSha256` with the newest signed channel pointer. If release/hash differs, display `Actualización disponible` and offer/perform a safe update, never full reinstall.
5. **Install/update**: resolve signed manifest by exact tag/hash, download only missing or changed blobs, retain checksum-verified files, stage atomically, preserve user settings/saves and last-known-good snapshot.
6. **Failure/offline**: if GitHub is down, list last verified catalog and allow only previously verified local snapshots; distinguish cached from current state. Never interpret network errors as 'there are no modpacks'. Rate limit/back off on GitHub outages; avoid GitHub unauthenticated REST search API for normal navigation.
7. **Integrity**: reject unsigned catalog, changed immutable Release contents, path collisions, unexpected JARs or a new loader version that is incompatible. Signed catalog generation is monotonically increasing and prevents accepting a stale online response; allow explicit older **signed release rollback** without accepting a stale catalog.

## Required repository/release workflow

A normal source edit, draft change or PR merge is **not yet a public update**. No launcher should react to unpublished work.

- **Curate:** update draft and/or introduce another target manifest. Import actual ZIP/JARs, calculate hashes, verify compatibility and license obligations.
- **CI gate:** validate schema, licensing evidence, binary staging, JAR data, signature process, release format and boot test results. Fail closed on any invalid file.
- **Release:** create a **new, immutable** GitHub Release tag, publish the complete signed manifest and the content-addressed assets. Never overwrite a previously published `manifest.json` or release asset.
- **Catalog auto-promotion:** after *successful* protected release publication, workflow updates the appropriate `targets[]/channels[stable|beta|dev]` pointer, increments `generation`, signs the new catalog and atomically commits `catalog/current.json` + `.sig` (must not expose signing private key to untrusted PR jobs).
- **Visibility:** the next catalog refresh makes the target appear or shows an update in an already installed target, **without updating the launcher binary** when its supported loader/runtime/protocol can handle it.

A securely approved publish action can automate every step after validation; *writing arbitrary JARs to Git or changing a draft cannot safely trigger an immediate public release*.

## Compatibility limits of "never update the launcher"

- **Does not require launcher update:** changing, adding or removing mods to an existing supported target; updating pack config/resources; introducing a new Fabric Minecraft version when existing launcher download/bootstrap/runtime protocol supports it.
- **May require launcher update:** a new mod loader family, new launcher protocol/schema, new Java major/runtime platform, breaking Mojang metadata/API behavior or a new bootstrap strategy absent in launcher.
- The signed manifest `minimumLauncherVersion` and supported loader/runtime capabilities must enforce this gracefully.

## Acceptance tests for launcher integration

- Publish a **new** compatible target in signed catalog: it appears after Refresh, no launcher update.
- Publish a **new release** under 1.8.9: installed 1.8.9 reports update; only changed hashes download.
- Modify unrelated draft or documentation: no production update.
- Corrupt catalog signature or lower signed generation: refuse online update; allow verified offline snapshot.
- HTTP 304 or network outage: use verified local cache with visible stale/offline status.
- An unsupported loader or too-new minimumLauncherVersion: show update-required, do not launch invalid setup.
- User-added JAR: quarantine and repair, do not treat user modifications as a new official Selection release.

## Implementation state

This document is the **design contract**. The current TFL Client implementation (`src-tauri/src/commands/tfl_selection.rs`) still searches community repositories by GitHub topic and consumes `.mrpack` URLs. It must be replaced by a signed, dynamic catalog consumer; no claim of end-to-end integration until a separate launcher PR and tests pass.
