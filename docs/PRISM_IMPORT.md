# Official 1.8.9 Prism Launcher ZIP import — exact upload specification

## Upload request

Please attach **one native Prism Launcher instance export in ZIP format**. Use Prism Launcher -> right click the tested Minecraft 1.8.9 instance -> **Export Instance** -> native ZIP, **not** Modrinth `.mrpack`, not a custom `.minecraft` archive. Preserve the export's original `mmc-pack.json`, `instance.cfg`, and `.minecraft/` (or Prism's equivalent `minecraft/`) directory structure.

### Include

- Instance metadata: `mmc-pack.json` (loader/component stack), `instance.cfg` (profile metadata).
- Every real installed file under `mods/` (actual .jar bytes, not only Modrinth identifiers or URLs).
- `config/` files necessary for the official experience; required `options.txt` may be inspected but should be considered **user-editable**, never immutable pack configuration.
- `resourcepacks/`, `shaderpacks/`, `defaultconfigs/` only when intentionally part of **TFL Selection**.
- Any required patches or custom version metadata bundled by Prism that make **Ornithe Gen2 + Legacy LWJGL3** start.

### Exclude

- `saves/`, `screenshots/`, `logs/`, `crash-reports/`, `backups/`, caches, or temp files.
- Personal accounts, authentication tokens, `accounts.json`, credentials, private server IPs or personal world data.
- Downloaded global Minecraft libraries/assets, extracted native files, or a ZIP of the whole Prism Launcher folder.
- Java/Zulu binaries: target Java **25** is recorded in the Selection manifest; the **TFL Client** launcher provisions its own runtime via `java_manager::ensure_java(25, mc_version)` (subject to real boot tests).

## Do not alter the ZIP manually unless it contains personal data

Keep the working instance files unchanged so we can analyze the *actual tested setup*, its mod metadata, dependencies and shaders/config values. A Prism native ZIP is an **input** for curation, not the **published output**. TFL Selection will publish individually hashed JARs as GitHub Release assets, with exact installer paths in signed manifest v2.

## Import / validation acceptance checklist

1. Inspect ZIP entries and enforce size/path/traversal/symlink constraints before extraction.
2. Detect `mmc-pack.json` components, base Minecraft 1.8.9, Ornithe Gen2, loader revision, Java 25 override, LWJGL3 modifications and necessary libraries. Confirm exact loader identity instead of treating Ornithe as ordinary modern Fabric.
3. Enumerate all JARs from the **uploaded ZIP**, read internal `fabric.mod.json` (where present), IDs/versions/dependencies and filenames; identify duplicates, disabled mods, helper libraries and artifacts that should not be installed.
4. Compute SHA-256 and exact byte counts for every actual JAR and official config/resource file. Ensure all required mods are licensed for independent redistribution.
5. Check TFL Core compatibility/source pin separately against `TFLClientMOD`; never silently substitute an untested Core build.
6. Record licensing evidence/attributions and archive corresponding source for copyleft artifacts. Do not publish binaries missing permissions or source obligations.
7. Construct a complete `drafts/mc-1.8.9-ornithe.json`, validate, and create an immutable Release candidate **only after boot evidence**.
8. Keep the Prism export private as import evidence; **do not** publish the ZIP or transform into a public `.mrpack`.
9. Once verified, publish individual GitHub Release assets and a signed catalog pointer. Test incremental update and offline install in TFL Client.

## Current state

As of this document's creation, the actual Prism ZIP is **not yet attached**, so artifact hashes, actual loader version, mod inventory, signatures and first release do not exist. No successful Java 25/Ornithe runtime test has been verified in this repository yet.
