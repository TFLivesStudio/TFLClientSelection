# TFL Selection 1.8.9 — Prism ZIP import (2026-11-07)

**Inventory imported, public release blocked pending rights and boot QA.** This metadata is derived from a native Prism Launcher ZIP supplied by the project owner; the original ZIP and personal data were NOT uploaded to GitHub.

- Minecraft **1.8.9**, **Ornithe Gen2** using Fabric Loader **0.20.1**, Intermediary 1.8.9, Flap 0.0.8, and **Java 25**.
- Exactly **11 active mods**, **177609802 bytes** of JARs. Actual filenames, sizes, and SHA-256 are in [inventory](inventory/mc-1.8.9-ornithe-2026-11-07.json).
- TFL Core **0.5.0-visual-preview.1** and Lucerna **0.1.5-tfl.2**, from the supplied binaries. Do not silently replace with older historical versions.
- Six shaderpack ZIPs found (Butter, Complementary Reimagined, Mellow, OpenShad, Sildur, TrueLightFX); **not approved for redistribution** and not part of active mods.
- Over 14,000 unrelated files include generated map/far-terrain caches, user waypoints/server data and game crash logs. The remapping cache includes **Mojang Minecraft client JAR copies** and e4mc/WindowsPriorityBoost cache entries; none of these are active mods to distribute.

## Publication blocks

1. **Argentum, Argentum Extras, Cera:** the monorepo `QuicksilverMC/Argentum` `README.md` explicitly states **All Rights Reserved** for Argentum, except the included **Celeritas** binary that remains LGPLv3. The `/extras` and `/cera` subprojects have no separate grant established; their lack of a root LICENSE does not override the parent's restriction. It is based on **Celeritas**, not a direct automatic permission derived from current Sodium licensing. GitHub permits viewing/forking a public repo under its ToS but **not independent redistribution** without an applicable license. Author permission or independently implemented replacement is required for the exact current JARs. Source: https://github.com/QuicksilverMC/argentum/blob/main/README.md
2. **Amplio:** uploaded JAR **already embeds** `natives/windows-x86_64/nvngx_dlss.dll` (58,956,912 bytes); `Natives.extract()` copies bundled files into `minecraft/amplio/natives/...` at start. There is **no runtime network download** for that DLL in the inspected code. NVIDIA's SDK license permits certain distribution **incorporated in an application** under specific conditions; check exact runtime (release, not dev), license/notice/notification requirements rather than assuming it is prohibited outright. Source: https://github.com/jonathanthxd/amplio/blob/main/src/main/java/us/z1x/amplio/upscale/Natives.java and https://github.com/NVIDIA/DLSS/blob/main/LICENSE.txt .
3. **Copyleft sources:** Legacy LWJGL3 (LGPL-2.1-only), Lucerna (LGPL-3.0-only), Pulse (GPL-3.0-only), Sarcio (LGPL-3.0-or-later), SoundFix (LGPL-3.0 metadata), TFL Core (GPL-3.0-only). Archive corresponding source and copyright notices and verify exact source revisions.
4. **QA:** no actual TFL Client/Ornithe Gen2 bootstrap test, Zulu Java-25 boot or offline-update rollback validation. The Prism archive is not proof our launcher can boot it.
5. **Config/privacy:** official game and TFL Core defaults need a separate curated baseline. Do not blindly ship `client.json`, personal options, maps, domains, server history, shaderpacks or remap caches.

## Next steps

1. Obtain licenses or written permissions for blockers, verify bundled native components and source archives.
2. Finish official mod/config/shader selection **without removing or replacing requested mods** unless explicitly approved.
3. Map/verify TFL Core artifact against the corresponding repository commit, TFL-specific licenses and source.
4. Implement pinned Ornithe Gen2 Fabric-based bootstrap and Java 25 manifest override in the launcher. Current launcher already has Azul Zulu primary and Adoptium fallback through `JreProviderChain`, but infers Java from MC version on the normal launch path.
5. Complete signed release manifest v2, notices/source bundles, real boot tests, content-addressed GitHub Release assets, signed catalog publication. Normal pack changes will be discovered dynamically without rebuilding the launcher.

**Do not publish the 11 binary assets while these gates remain unresolved.**
