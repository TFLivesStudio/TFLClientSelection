# Stable project boundaries — TFL Selection ecosystem

| Responsibility | TFLClientSelection (private) | TFLSelectionDistribution (public, planned) | TFLClient (public) | TFLClientMOD (separate) |
| --- | --- | --- | --- | --- |
| Choose mods and exact versions | **Owns** | No | Reads | No |
| Maintain GPL source/legal evidence | **Owns** | Hosts approved source/notices | Shows notices | Own provenance |
| Binary distribution | Prepares release metadata | **Hosts Release assets** | **Downloads/verifies** | Supplies Core build |
| Signed release manifest | Generates/reviews | **Serves** | **Verifies** | No |
| Installer/repair/rollback | Specifies protocol/tests | No | **Implements** | No |
| Ornithe Gen2 & Fabric setup | Pins target versions | Hosts permitted bootstrap assets | **Bootstraps** | Produces compatible jar |
| User data, Minecraft worlds, settings | Never stores | Never stores | **Owns local storage** | No |
| TFL Core visual/HUD/features | No | No | Launches | **Owns** |
| Prohibit user mod customization inside Selection | Defines policy | No | **Enforces** | Can display official status |

**Do not mix** TFL Selection (curation/delivery) with TFL Core (game mod functionality), TFL Client (launcher) or generic community modpack discovery.

## GitHub inventory policy

GitHub Releases are a binary distribution channel, not a Git source history. Every selected redistributable mod must be stored under a TFLives-controlled immutable tag, with source evidence and SHA. No third-party mod-host CDN or 'latest' link in the launcher.

License obligations and player extractability cannot be hidden by private repository status, neutral names or closed install UI.
