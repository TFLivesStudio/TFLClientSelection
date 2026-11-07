# TFL Selection 1.8.9 — clean configuration defaults

The included defaults are derived from **non-personal settings** in the owner's Prism 1.8.9 export. They are **seeds**, never enforced immutable files. The launcher will install these only if absent, preserving any player changes.

- Amplio starts on **FSR1**, not DLSS, with quality BALANCED; bundled proprietary DLL issue remains independently under rights review.
- Lucerna shaders start **disabled** because none of the six exported shaderpack ZIPs have been approved for TFL-hosted redistribution yet. We do not force a missing Butter shaderpack on every installation.
- Argentum, Cera and Sarcio settings reflect owner-selected graphics/stability options.
- Pulse starts without the background profiler to avoid always-on overhead and without shipping a player-specific activity record.
- The full TFL Core 57 KB client JSON from the export contains user-specific application state. It is **not** published. A sanitized local-only test configuration is available in the owner's development package; official TFL Core defaults still need smoke tests.

Never commit a Prism `instance.cfg` containing a Windows Java path, player world cache, `servers.dat`, `usercache.json`, world map, private waypoints, or shaderpacks without redistribution approval.

These defaults will be included in actual releases by the gated `scripts/build_release_bundle.py` builder and each will be individually content-addressed in the v2 manifest.
