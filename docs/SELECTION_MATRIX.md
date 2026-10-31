# Selection targets and curated inventory — awaiting actual file review

| Target ID | Minecraft | Runtime loader | Java major | Current state |
| --- | --- | --- | --- | --- |
| `mc-1.8.9-ornithe` | 1.8.9 | Ornithe Gen2 | **25 (candidate, test first)** | contract draft; no binaries |
| `mc-26.3-fabric` | 26.3 | Fabric | **25 (candidate, test first)** | contract draft; no binaries |

Java 25 for both targets is a **planning input** from prior client work, not verified here. Official Minecraft 1.8.9 normally uses an older Java runtime, and Ornithe Gen2/Legacy LWJGL3/Argentum setup must be tested in the actual launcher before pinning 25. The published manifest must reflect the Java runtime that truly boots every selected mod.

## Target 1.8.9 — review queue, not a confirmed mod list

- TFL Core (Ornithe Gen2 build), version/commit/hash missing
- Ornithe Gen2 bootstrap support (not implemented in current launcher)
- OSL modules (review exact needed modules and licenses)
- Argentum renderer (review compatibility/rights)
- Legacy LWJGL3 integration (review launcher bootstrap; not necessarily a mod JAR)
- Additional PvP and FPS mods: **not chosen or validated yet**

## Target 26.3 — review queue, not a confirmed mod list

- TFL Core Fabric build, version/commit/hash missing
- Fabric loader, pin exact build instead of resolving latest
- Sodium, Iris: **candidates only**, check exact compatibility and license evidence
- Any dependencies (Fabric API etc): only after exact compatibility review
- Additional QoL/visual mods: **not yet chosen**

### Inventory review for every candidate

Record: project URL, source commit, mod version, exact Minecraft target, loader, Java major, direct dependencies, conflicts, build method, SHA-256, byte size, license evidence, redistribution eligibility, notices and corresponding source archive if required. No unverifiable selection gets uploaded.

### Invariants

- Every required mod is picked by TFLives, not by the end user.
- Never automatically choose newer mod versions at player install time.
- Do not add mods simply because an old planning note named them.
- Separate target folders and release tags; no shared runtime files unless sha256 verified.
- User saves and Minecraft personal settings remain private and unmodified by pack repair.

> Source audit note: `TFLClientMOD`'s current main README still describes 0.3.0-alpha.1 with Fabric Loader 0.19.5+. This is **not** a pinning decision: inspect the exact current build branch/artifacts and run compatibility tests before releasing Selection.
