# Security and third-party redistribution policy

## Legal baseline

User preference is to host **all selected mod binaries ourselves** in GitHub Releases and never fetch Selection mods from Modrinth. This is feasible only after verification that every chosen JAR may legally be redistributed. A source repository's existence or public visibility does **not** automatically grant redistribution rights.

Each binary must record exact project, version, upstream source repository, immutable commit/tag, **version-appropriate license evidence**, SHA-256, exact bytes and release asset name. Before publication, manually verify that the downloadable JAR and its bundled assets/dependencies fall within the applicable license.

- MIT/BSD/ISC: typically permit redistribution but preserve license and copyright notices.
- Apache-2.0: ensure license and applicable NOTICE conditions.
- GPLv3/LGPLv3: redistribute under appropriate terms, provide license notices and **complete corresponding source at no extra cost** with convenient access equivalent to our mirrored binary. Preserve source build scripts and modifications, not merely a possibly disappearing upstream GitHub link. This repo's contract requires a content-addressed source archive in **our distribution Release** for GPL/LGPL binaries.
- MPL-2.0 and other copyleft: review file-level/source obligations for the specific artifact, do not assume GPL rules are identical.
- Other/ambiguous/commercial/no-license: hold for review, seek explicit permission or **exclude and select another mod**. No Modrinth fallback is allowed for official Selection.

License notices available to players (verified \`notices-<sha>.zip\`) remain public alongside the binaries. GPL source archives are public and readable. You cannot make GPL sources secretly proprietary by renaming the assets.

### Special case: TFL Core provenance

TFL Core must be reviewed for inherited licenses from any forked upstream code or assets (e.g. TRS-derived components), plus its dependencies; do **not** mark the whole Core as proprietary merely because TFLives maintains its current repository.

## Security controls

1. Ed25519 signatures of the exact raw published catalog and manifest bytes. Trusted public key embedded in launcher, private key only in a protected release workflow.
2. Manifest hash checked against signed catalog, downloaded asset bytes and SHA-256 checked against signed manifest.
3. Content-addressed binaries with immutable release tags, no \`latest\` mod or bootstrap.
4. Path safety: reject absolute/relative traversal, symlinks, Unicode/OS case-folding collisions, reserved DOS names, source mismatch, suspicious GitHub redirects.
5. Download timeouts, retries, rate limiting, bounded size and concurrency, safe file permissions, atomic swaps, journaling and old-known-good restore.
6. Enforce locked selection in Rust backend commands too; the frontend can be modified by an advanced user.
7. Quarantine extra mod JARs with recovery metadata; never silently destroy personal data.
8. Rollback, offline cache and signature rotation tested before release.
9. No reusable GitHub token in the open-source client. GitHub Actions PR jobs have only read-only permissions and no access to publisher secrets.

## Compliance automation is not enough

The Python validator rejects absent required source archives, missing license review basis, unsafe paths, unknown SPDXs and SHA naming mismatches. It cannot independently prove actual IP rights, source completeness, mod compatibility or integrity of remote Release assets. Those are **pre-publication release gates**.

## Verified external references

- MIT license: https://choosealicense.com/licenses/mit/
- GPLv3 §6 source obligations: https://www.gnu.org/licenses/gpl-3.0.en.html
- GitHub licensing overview: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository
