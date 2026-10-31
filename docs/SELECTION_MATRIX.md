# Initial modpack targets — pending inventory

The following are **design inputs**, not verified or redistributed binary selections.

| Target | Loader / bootstrap candidate | TFL Core | Other candidate groups | Current state |
| --- | --- | --- | --- | --- |
| mc-1.8.9-ornithe | Ornithe Gen2, OSL, legacy LWJGL3 support and Argentum (exact versions to confirm) | Ornithe build (pin exact JAR) | PvP, performance, HUD/QoL, compatibility | draft only |
| mc-26.3-fabric | Fabric (exact loader and runtime versions to confirm) | Fabric build (pin exact JAR) | Sodium/Iris ecosystem, vanilla-oriented performance and visual/QoL | draft only |

## Pending decisions

1. Where binaries reside: private R2 bucket, VPS gateway or a compatible equivalent.
2. Download entitlement: public access to signed *release* metadata, authenticated access, internal dev/beta access.
3. Inventory and feature groups by target, including exact mods and version-specific compatibility tests.
4. Redistribution review for every third-party JAR; where prohibited, official upstream delivery or exclusion.
5. Launcher integration protocol agreement, trusted signature keys, signing service, rollback behavior.
6. Install-time isolation for per-user settings and extra mods.
7. Target-specific Java major/loader setup must be confirmed with real boot tests.

## Priorities

- First deliver a legal, reproducible, boot-tested minimum set on **each target**.
- Then add optional features and machine-specific quality profiles.
- Add newer Minecraft versions by introducing a new `targetId`, not by mixing incompatible binaries in one profile.

The catalog currently has **zero published channels**.
