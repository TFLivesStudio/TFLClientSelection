# TFL Client Launcher — code audit and concrete integration plan (2026-10-31)

## Source reviewed

Public repository: https://github.com/TFLivesStudio/TFLClient, current `main` at audit time. This is an **inspection**, not a change to TFL Client itself. File references are exact paths and observed functions, not assumptions about private branches.

| Observed code | Actual behavior / gap | Selection integration |
| --- | --- | --- |
| `src-tauri/src/commands/tfl_selection.rs` | `get_tfl_selection()` searches public org repos tagged `tfl-modpack`, reads `tfl-modpack.json` through GitHub API and expects `mrpack_url`. Only Vanilla/Fabric/Forge/NeoForge/Quilt in list. | Replace **official Selection** discovery with hardcoded/trusted signed catalog endpoint + fixed target IDs. No Github topic search, no .mrpack, no community contributions to official catalog. |
| `src-tauri/src/commands/modpacks.rs` | `install_modpack_from_url` uses `cubrinth::mrpack::install_mrpack`. `update_community_modpack` compares .mrpack URLs; integrity function primarily checks files exist. | Keep for normal modpacks only. Build new **Selection-specific** release installer: signed manifests, binary-by-binary SHA, snapshot/rollback, repair. |
| `src-tauri/src/services/instance_manager.rs` | `LoaderKind` enum lacks Ornithe; `resolve_loader` resolves latest Fabric loader, stores regular instances; `InstanceData` lacks official profile identity. | Add `profile_kind: Normal | TflSelection`, `target_id`, `channel`, `installed_release`, `manifest_digest`, `last_known_good`. Add OrnitheGen2 bootstrap path; never resolve latest loader for Selection. |
| `src-tauri/src/services/launcher.rs` | `ensure_downloaded` handles vanilla/Fabric/Forge/NeoForge/Quilt; Java selected by `aqua::infer_java_version(&data.mc_version)`. Launch uses regular instance directory. | Before launch, perform manifest integrity/repair; respect pinned `minecraft.javaMajor` and `loaderVersion` for official Selection; add Ornithe bootstrap, isolated runtime path. |
| `src-tauri/src/services/launcher.rs` | `inject_mp_guard` copies an additional first-party JAR into `mods` for cracked/offline accounts and fails soft if unavailable. | For locked Selection, either include **exact** guard artifact with version-specific hash in signed manifest, or explicitly avoid injection for that profile. No untracked mods at launch. |
| `src-tauri/src/commands/content.rs` | Offers `install_mod`, `remove_mod`, `set_mod_enabled`, `update_all_mods`, `add_local_mod_files`, `remove_duplicate_mods`. | Add backend authorization guard for every operation that mutates a Selection profile; leave normal launcher instances unchanged. |
| `src-tauri/src/commands/instance.rs` | Offers duplicate, open instance folder, rename and delete commands. | Limit open-folder/export/duplicate for Selection; optionally allow delete after normal user confirmation (must not erase saves silently). Rename display label only, do not alter trusted profile identity. |
| `src/lib/components/library/TflSelection.svelte` | Allows selecting a compatible **normal instance** or creating one; then calls `installModpackFromUrl`. | Redesign to a fixed official Selection **version selector** (1.8.9, 26.3, future); channel opt-in gated; install/repair/update/launch states. No user mod selection. |
| `src/lib/types/types.ts` + `src/lib/api/modpacks.ts` | TFL Selection types depend on `mrpack_url`; API exposes `get_tfl_selection`. | Introduce strict typed v2 catalog/manifest status and new invoke commands. Remove .mrpack linkage only from official Selection path. |
| `src-tauri/src/lib.rs` | Registers Tauri commands for normal instance/content and existing modpacks. | Register new Selection commands and ensure old mutation paths cannot target official Selection profiles. |
| `crates/aqua/src/downloaders/fabric.rs` | Fabric batch resolution/download already exists. | Reuse underlying downloader where appropriate but **pin** exact loader version for Selection instead of resolving latest. |
| `crates/launchwerk/src/launchwerk.rs` + `crates/zellkern` | General Java launch pipeline exists. | Integrate Ornithe Gen2 launch manifest/classpath/libraries/natives after verifying Ornithe + legacy LWJGL3 requirements. Do not assume Fabric internals apply. |

## Proposed new Rust module boundaries

```text
src-tauri/src/services/selection/
  mod.rs                # entrypoint, states and trusted target IDs
  catalog.rs            # signed public catalog, pinned repo, channel resolution
  manifest.rs           # strict v2 schema / source hashes / no arbitrary paths
  signatures.rs         # Ed25519 verification, trusted key IDs, future key rotation
  downloads.rs          # GitHub Release asset URLs, bounded concurrency, hash cache
  store.rs              # verified immutable blobs by sha256
  installer.rs          # transactional staging, journal, atomic swap, rollback
  integrity.rs          # only curated JARs, quarantine extras, repair
  profile.rs            # identity, lockfile, isolated player-data and runtime dirs
  bootstrap/ornithe.rs  # exact loader and native LWJGL3+Argentum integration
  bootstrap/fabric.rs   # pinned Fabric loader through existing aqua infrastructure

src-tauri/src/commands/selection.rs
  get_selection_catalog
  install_selection
  update_selection
  verify_selection
  repair_selection
  rollback_selection
  launch_selection
  select_selection_channel  # opt-in beta/dev if official policy allows
```

Names are **proposals**, not existing files. Avoid duplicating existing HTTP/aqua/launchwerk implementations; add adapters for their safe reusable primitives.

## Sequential implementation roadmap

### Phase L0 — compatibility evidence

1. Record exact TFL Client commit, Rust/Tauri versions and existing test baseline.
2. Boot vanilla 1.8.9 and 26.3 through existing launcher. Confirm actual support for Minecraft 26.3 metadata.
3. Prototype Ornithe Gen2 in isolation: exact loader revision, profile JSON, classpath, natives, Java 25, OSL, Argentum, legacy LWJGL3. If Java 25 incompatible for a specific mod, **change pinned runtime based on evidence**, not assumptions.
4. For modern Fabric, test pinned loader (not latest) and TFL Core jar with exact Minecraft target.
5. Do not issue a stable release before both targets boot.

### Phase L1 — trust and catalog

1. New Rust v2 types with size limits and strict field rejection.
2. Fetch static signed GitHub public catalog from trusted pinned repo/path.
3. Verify Ed25519 signature before accepting target/channel or generating asset URLs.
4. Fetch immutable manifest and verify signed digest.
5. Unknown/unavailable release -> error or verified offline snapshot, not an arbitrary fallback.

### Phase L2 — download and lifecycle

1. Download expected sha256-named release assets using existing HTTP stack with streaming, timeouts, concurrency bounds.
2. Reuse verified global content-addressed cache across targets and releases; no full re-download.
3. Stage managed file set outside currently running game directory and verify each file hash, size, extension and path.
4. Atomic install swap with journal/rollback after game closed; persistent world/options preserved.
5. Automatic repair on missing/corrupted/added mods; reversible quarantine of unknown files.
6. CLI/UI progress, explicit cancellation and crash recovery; E2E interruption tests.

### Phase L3 — locked profile controls

1. `profile_kind=TflSelection` under a **separate application-data directory** and lockfile; legacy instances stay Normal.
2. Hide normal mod manager, adding mods, update mod, remove mod, .mrpack import/export, open managed folder and arbitrary loader chooser in Selection UI.
3. Block corresponding Rust commands from modifying Selection profiles; do not rely on UI visibility.
4. If `TFL MP Guard` is required, make it a verified curated artifact with target compatibility; never copy uncontrolled mods into the locked folder.
5. Preserve personal `options.txt`, saves, logs, screenshots and legally required license notices; these are not protected "mods".
6. Run integrity verification prior to launch; offline launch only verified installed snapshot.

### Phase L4 — release and operations

1. Implement separate signing/publishing pipeline with protected approval and a scoped GitHub App on future distro repo.
2. Build release asset and source-bundle validation and mirror compliance copies.
3. Introduce channel pinning, beta/dev policy, rollback catalog pointers, key rotation, minimum client version.
4. Validate full Windows/Linux/macOS installs and nightly cold start/download failure recovery.

## Acceptance matrix

| Scenario | Expected |
| --- | --- |
| Player opens Selection for the first time | Exactly the TFL-published targets and supported versions are shown, not org-topic community packs |
| Install 1.8.9 | Correct Ornithe Gen2 bootstrap and exact approved JAR set; no Fabric or .mrpack |
| Install modern 26.3 | Correct pinned Fabric loader, exact approved JAR set; no dynamic latest |
| Player adds a `mods/hack.jar` | Prelaunch integrity fails/extra mod quarantined with recovery, **not launched as official Selection** |
| Player clicks install mod on Selection (or calls Rust invoke directly) | Backend rejects mutation, even with UI modified |
| Two versions share same binary hash | Asset downloaded once, reused from verified cache |
| Officially updated one JAR | Only changed blob downloaded, others reused |
| Network fails halfway | Existing snapshot remains runnable/offline verified; no mixed versions |
| GitHub asset modified/corrupt | Hash mismatch -> reject; do not launch |
| Malicious catalog/manifest | Signature failure -> reject |
| User modifies controls/options | Settings preserved; game can still launch |
| User saves a world | Update never erases save |
| Ornithe target with wrong loader/Java | Fail with actionable diagnostic, not silently fall back |
| Cracked account additional guard | Guard either pinned in release or excluded; no untracked auto-injection |
| No Modrinth connectivity | Official Selection installed/updated using our GitHub assets (Minecraft base/Java upstream requirements are separate) |

## Important: scope of this repository

These tasks are tracked **here** as cross-repository requirements, but the actual Rust/Svelte implementation belongs in TFLClient. **No launcher code has been changed by this Selection PR.** Do not say "integrated" until a separate launcher PR and real boot QA are completed.
