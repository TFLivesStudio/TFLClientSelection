# Selection targets and curated inventory — awaiting actual file review

| Target ID | Minecraft | Runtime loader | Java major | Current state |
| --- | --- | --- | --- | --- |
| `mc-1.8.9-ornithe` | 1.8.9 | Ornithe Gen2 | **25 (candidate, test first)** | contract draft; no binaries |
| `mc-26.3-fabric` | 26.3 | Fabric | **25 (candidate, test first)** | contract draft; no binaries |

Java 25 for both targets is a **planning input** from prior client work, not verified here. Official Minecraft 1.8.9 normally uses an older Java runtime, and Ornithe Gen2/Legacy LWJGL3/Argentum setup must be tested in the actual launcher before pinning 25. The published manifest must reflect the Java runtime that truly boots every selected mod.

## Target 1.8.9 — ZIP imported, Release blocked

- **11 verified active JARs** imported from Prism ZIP 2026-11-07; SHA-256 and versions recorded in [inventory](inventory/mc-1.8.9-ornithe-2026-11-07.json).
- Fabric Loader 0.20.1 on **Ornithe Gen2**; Java **25**; TFL Core **0.5.0-visual-preview.1**; Lucerna **0.1.5-tfl.2**.
- These exact mods remain selected. Argentum monorepo's README explicitly says **All Rights Reserved** for its original changes (Celeritas bundled remains LGPLv3); Extras/Cera are same monorepo without a separate redistributable grant. NVIDIA DLSS embedded in Amplio requires SDK-license compliance review.
- **Not a launchable release.** No binary/public catalog/signature published. See [import audit](MC1_8_9_PRISM_IMPORT_REVIEW.md).

## Target 26.3 — candidate inventory registered (not an install manifest)

- User-supplied **56 candidates** inventoried with exact version, JAR filename, source URL, review status, preliminary license gates and technical notes: [readable review](MC26_3_MOD_REVIEW.md) / [CSV inventory](inventory/mc-26.3-fabric-candidates.csv).
- TFL Core Fabric build, version/commit/hash missing; Fabric loader remains to be pinned.
- Sodium, Iris and other stack options remain **candidates only** until actual compatibility, redistribution permissions and source notices are verified.
- Sodium (PolyForm Shield) and EntityCulling (protective no-outside-mirroring rule) are explicitly **blocked for TFL-hosted binary publication** pending authorization/review.
- C2ME/ScalableLux/Vitrail and overlapping patches require isolated benchmark and integration tests.
- No mod has been approved for publication or added to the immutable/managed install list by this inventory update.

### Inventory review for every candidate

Record: project URL, source commit, mod version, exact Minecraft target, loader, Java major, direct dependencies, conflicts, build method, SHA-256, byte size, license evidence, redistribution eligibility, notices and corresponding source archive if required. No unverifiable selection gets uploaded.

### Invariants

- Every required mod is picked by TFLives, not by the end user.
- Never automatically choose newer mod versions at player install time.
- Do not add mods simply because an old planning note named them.
- Separate target folders and release tags; no shared runtime files unless sha256 verified.
- User saves and Minecraft personal settings remain private and unmodified by pack repair.

> Source audit note: `TFLClientMOD`'s current main README still describes 0.3.0-alpha.1 with Fabric Loader 0.19.5+. This is **not** a pinning decision: inspect the exact current build branch/artifacts and run compatibility tests before releasing Selection.

### Delivery source check (2026-11-07)

**Six exact original GitHub Release matches**: Argentum, Argentum Extras, Cera, Sarcio, OSL, TFL Core. **Five pending TFL assets**: Amplio 0.1.1, Legacy LWJGL3 1.4.10, Lucerna 0.1.5-tfl.2, Pulse 1.0.0 and SoundFix 1.1.0. Original JARs remain unchanged. See [mixed delivery](MIXED_GITHUB_RELEASE_DELIVERY.md).
