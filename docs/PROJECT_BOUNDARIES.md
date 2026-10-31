# Stable project boundaries — one TFL Selection repository

| Responsibility | TFLClientSelection (public; source + Releases) | TFLClient (public) | TFLClientMOD (independent) |
| --- | --- | --- | --- |
| Choose all mod versions | **Owns** manifests/inventory | Reads/installs only curated ones | No |
| Copyright/license review | **Owns** evidence, notices and GPL corresponding-source Release assets | Displays notices | Supplies TFL Core license/provenance |
| Host approved mod JAR binaries | **Own GitHub Release assets** | Downloads/verifies hashes | Supplies Core JAR |
| Release signature/catalog | **Signs and publishes** after approval | **Verifies** against pinned public key | No |
| Install/repair/rollback | Defines contract | **Implements** | No |
| Ornithe Gen2/Fabric bootstrap | Pins loader/runtime requirements | **Bootstraps** | Compiles compatible mods |
| Player saves/settings | Never stores | **Owns** local data | No |
| No user mod customization for Selection | Defines locked product policy | **Enforces UI and Rust backend** | No |
| TFL Core features/HUD | No | Launches | **Owns** |

The same public repo contains source-of-truth metadata, CI and GitHub Releases. It is not a secret store. Downloads of these Release assets need no user GitHub account or VPS.

Do not confuse official TFL Selection (closed, curated) with TFL Core (in-game mod features), generic community modpacks or the launcher itself.
