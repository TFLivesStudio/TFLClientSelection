# TFL Selection 1.8.9 — Prism ZIP import (2026-11-07)

**Inventory imported, public release blocked pending rights and boot QA.** This metadata is derived from a native Prism Launcher ZIP supplied by the project owner; the original ZIP and personal data were NOT uploaded to GitHub.

- Minecraft **1.8.9**, **Ornithe Gen2** using Fabric Loader **0.20.1**, Intermediary 1.8.9, Flap 0.0.8, and **Java 25**.
- Exactly **11 active mods**, **177609802 bytes** of JARs. Actual filenames, sizes, and SHA-256 are in [inventory](inventory/mc-1.8.9-ornithe-2026-11-07.json).
- TFL Core **0.5.0-visual-preview.1** and Lucerna **0.1.5-tfl.2**, from the supplied binaries. Do not silently replace with older historical versions.
- Six shaderpack ZIPs found (Butter, Complementary Reimagined, Mellow, OpenShad, Sildur, TrueLightFX); **not approved for redistribution** and not part of active mods.
- Over 14,000 unrelated files include generated map/far-terrain caches, user waypoints/server data and game crash logs. The remapping cache includes **Mojang Minecraft client JAR copies** and e4mc/WindowsPriorityBoost cache entries; none of these are active mods to distribute.

## Publication blocks

1. **Argentum, Argentum Extras, Cera:** no declared license in their JAR metadata, currently listed as **All Rights Reserved** on Modrinth. Argentum's GitHub repository has no root LICENSE verified. Source visibility is not redistribution permission. Seek authorization or exact applicable license.
2. **Amplio:** its JAR embeds `natives/windows-x86_64/nvngx_dlss.dll` of 58,956,912 bytes. MIT mod metadata does **not** automatically license the bundled NVIDIA binary. Rebuild without it or verify redistribution rights.
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
