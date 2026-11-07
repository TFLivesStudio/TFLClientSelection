# TFL Selection 1.8.9 — reproducible GitHub-only mixed delivery (2026-11-07)

## Decision

**Selection is TFLives' closed choice of mods, not a user-customizable modpack.** No Modrinth dependency in the runtime. TFLives maintains the signed mod/version list and all SHA-256 hashes, even when the author hosts an original JAR in their own GitHub Release.

This is a **mixed delivery mode**, fully within GitHub:
- **Pinned official author's Release**: TFL does *not* republish or modify the binary. The launcher downloads the exact author's GitHub Release asset by repository/tag/name and verifies SHA-256 and bytes from **our signed** manifest.
- **Pinned TFL Selection Release**: for redistributable JARs where there is no exact upstream GitHub Release. These need notices/corresponding source and actual publication by TFL before a stable release may be announced.
- **No fallback to Modrinth or "latest"**. If the author's asset disappears, the launcher can use an already verified local cache/last-good snapshot but cannot invent a replacement binary. A new signed manifest and rights review are required to change source or version.

## Verified with GitHub Releases API

All six assets were verified against **exact sizes and GitHub's reported SHA-256**, equal to the original Prism ZIP. See [machine-readable lock](../inventory/github-release-lock.mc-1.8.9-ornithe.json).

| Installed JAR | Official GitHub Release | Delivery |
| --- | --- | --- |
| argentum-1.0.2.jar | [QuicksilverMC/Argentum v1.0.2](https://github.com/QuicksilverMC/Argentum/releases/tag/v1.0.2) | Author-only, All Rights Reserved |
| argentum-extras-1.0.2.jar | same | Author-only, All Rights Reserved |
| cera-1.0.2.jar | same | Author-only, All Rights Reserved |
| ornithe-standard-libraries-0.22.2.jar | [OrnitheMC OSL v0.22.2](https://github.com/OrnitheMC/ornithe-standard-libraries/releases/tag/v0.22.2) | Original release |
| Sarcio-1.1.1.jar | [QuicksilverMC/Sarcio v1.1.1](https://github.com/QuicksilverMC/Sarcio/releases/tag/v1.1.1) | Original release |
| tflcore-1.8.9-0.5.0-visual-preview.1.jar | [TFL Core v0.5.0-visual-preview.1](https://github.com/TFLivesStudio/TFLClientMOD/releases/tag/v0.5.0-visual-preview.1) | First-party separate repo |

The matching signed manifest still defines **local installed names** such as `mods/argentum-1.0.2.jar`. An optional `files[].download` field provides `kind=github-release`, `repository`, `tag`, and `asset`. If `download` is absent, the asset is expected under **this** TFL Selection Release, named `sha256-<hash>.bin`.

## Exactly five original JARs do NOT have matching verified GitHub Release assets

| JAR from Prism | Resolution required |
| --- | --- |
| amplio-0.1.1+1.8.9.jar | Author `Z1xus/amplio` releases `v0.1.0`, `v0.1.2`, `v0.1.3`, **not 0.1.1**. Do not silently swap; to host original 0.1.1 yourself, confirm NVIDIA SDK distribution obligations and retain its terms |
| legacy-lwjgl3-1.4.10.jar | No exact GitHub Release; original source uses AxolotlClient Maven, which might be another permitted upstream if **exact** checksum/length are verified, but this contract currently allows pinned GitHub Release only |
| lucerna-0.1.5-tfl.2.jar | Customized Lucerna build with **no** matching GitHub Release from `Z1xus/lucerna` or TFL fork |
| pulse-1.0.0.jar | `QuicksilverMC/Pulse` source exists; no public GitHub Release carrying this exact JAR |
| soundfix-1.1.0+mc1.8.9.jar | `moehreag/soundfix` source exists; no public GitHub Release carrying this exact JAR |

**No false "fully ready" claim**: these 5 remain pending and `drafts/mc-1.8.9-ornithe.json` is **not** a downloadable manifest. As of verification `TFLClientSelection` has **zero** GitHub Releases and no signed `catalog/current.json`.

## Consumer algorithm for TFL Client (required)

1. Read signed catalog, then signed immutable manifest, verify Ed25519 and the SHA from the signed channel pointer.
2. Each file has a content-addressed cache key (SHA-256) independent of host or filename.
3. If `files[].download.kind == "github-release"`: construct HTTPS GitHub Release URL from the **four validated fields**. Do not accept arbitrary user-supplied URLs, tokens, redirects to other protocols, branch refs or "latest". HTTPS redirect chains to GitHub's asset CDN can be legitimate; verify final *downloaded bytes*, size and hash before cache promotion.
4. Otherwise: fetch `https://github.com/TFLivesStudio/TFLClientSelection/releases/download/<SelectionTag>/sha256-<hash>.bin`.
5. Atomic staging, fail closed on missing assets, rollback to verified snapshot. Do not mutate game saves or player-specific options. No extra mods.
6. Never rewrite a published manifest to "repair" a missing author's asset; an updated signed TFL Selection Release changes source pin with user-visible update.

## Why this is safer in practical use (with limitations)

- An unrelated Modrinth project suspension does not affect assets at pinned GitHub Releases.
- We avoid hosting rights-restricted binaries when the **author already offers official downloads**.
- The source being in GitHub does **not** guarantee its retention. Original authors can remove assets; GitHub can also remove content for valid reasons.
- Signed metadata + SHA-256 protects the client from undetected changes. It does **not** make the upstream publisher permanent or grant redistribution rights.

## Tools and readiness

```powershell
python scripts/check_upstream_lock.py         # static/offline: 11 mods, 6 verified URLs, 5 pending
python scripts/check_upstream_lock.py --online # GitHub API: exact upstream asset bytes/hash
python -m unittest discover -s tests -v
```

The local candidate builder `scripts/build_release_bundle.py` accepts `--upstream-lock` (defaults to the reviewed six-asset file), **skips redistributing the six source-hosted JARs**, and requires license/source/native approval for every remaining TFL-hosted binary. The existing manual publisher only publishes after a complete passing candidate plus signed QA record. A client/Java25/Ornithe Gen2 launch still requires actual integration tests.

**Next goal:** provide authenticated publication of the five remaining redistributable assets, build/source notices, sign first complete Release, and only then promote a catalog channel. Never promote the current partial draft.
