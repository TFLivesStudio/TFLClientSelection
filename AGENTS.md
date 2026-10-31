# AGENTS.md — TFL Selection

## Product invariant
- Official TFL Selection is **locked**. User may set Minecraft settings and keep worlds/screenshots/saves, but may not modify the curated mods via launcher or add personal ones to the Selection profile.
- 1.8.9 uses **Ornithe Gen2** and target 26.3 uses **Fabric**. Never substitute Fabric for Ornithe or guess launcher bootstrap support.
- Selection is **not** community modpack discovery and is **not** a .mrpack installer.
- All selected third-party mod JARs are hosted in **TFL-managed public GitHub Release assets** only after rights and source checks. No Modrinth fallback.
- No dependency on TFLives VPS, custom API, R2, reusable private GitHub tokens or user GitHub accounts.
- This private repository is authoring/source-of-truth; published binary repository is separate and public.

## Safety and licensing
- **Never** commit JARs, tokens, private keys, paid/commercial assets or unlicensed binaries to Git history.
- No release or redistribution without reviewing the actual version's license. MIT usually requires notice, GPL/LGPL requires corresponding source availability and notices; other licenses need their own review. The *repo being public* does not grant rights.
- Maintain version-accurate source archives for GPL/LGPL as part of **our own release**, not only upstream links.
- No claim that files installed on user machines cannot be extracted.
- Signed catalog and exact bytes of manifest validated against pinned Ed25519 public key in launcher. Hashes alone are not trust authentication.
- Do not auto-publish from pull requests and do not expose signing secrets to untrusted code.
- Installation MUST reject path traversal, collisions, symlinks, out-of-bounds writes, invalid hashes, malicious redirects, and unexpected extra mods.
- Never delete user saves, screenshots, logs or options when repairing a Selection install.

## Responsibility boundary
- Work **here**: release metadata, schemas, source/license evidence, package/asset mapping, CI, compatibility matrix, notices and release review.
- Work **in TFLClient**: loader support, signed catalog client, downloader, cache, transactional install, locked profile protection, automatic repair, offline/rollback and UI.
- Work **in TFLClientMOD**: TFL Core source, build and artifact provenance; Selection pins version/hash of its output.
- Do not change TFLClient or TFLClientMOD automatically while editing this repository; coordinate explicit integration PRs.

## Version/release invariants
- Drafts: \`drafts/*.json\`; never treated as downloadable.
- Published manifest: \`releases/<targetId>/<release>.json\`; immutable forever.
- Release tag: \`selection-<targetId>-v<release>\` in public distribution repo.
- Asset JAR names in release: \`sha256-<64 lowercase hex>.bin\`, installed under exact local \`mods/*.jar\` paths.
- Signed \`catalog/current.json\` points to immutable release; **channel promotion edits catalog only**.
- No user-selectable optional features/variants inside one release manifest.
- Run \`python scripts/validate_manifests.py\` and \`python -m unittest discover -s tests -v\`; verify GitHub Actions.
