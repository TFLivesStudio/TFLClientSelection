# Architecture — TFL Selection distribution

## Scope / ownership

- **TFL Client Launcher**: public application, login/session handling, manifest verification, download engine and isolated installations.
- **TFL Core**: independently built first-party mod and its own source repository/release process.
- **TFL Selection**: this **private** repository, selection manifests, third-party licensing records, compatibility matrix, release review.
- **TFL Distribution Service**: a separate, not-yet-implemented backend controlling manifest delivery and issuing short-lived access to private object storage.
- **Blob storage**: e.g. Cloudflare R2 (private bucket) or a compatible securely operated object store. Binary files must **not** be checked into Git.

A private GitHub repository is an authoring store, not an endpoint the open-source launcher should clone. Never ship reusable GitHub credentials, R2 secrets, or signing private keys with a public executable.

## Initial target matrix

| Target ID | Minecraft | Loader | Runtime (initial working assumption) |
| --- | --- | --- | --- |
| `mc-1.8.9-ornithe` | 1.8.9 | Ornithe Gen2 | Java 25 |
| `mc-26.3-fabric` | 26.3 | Fabric | Java 25 |

Before first publish, test exact Java and loader versions against the **actual** bootable environment. Selection records `javaMajor` in each manifest; it does not claim all mods are compatible.

## Objects and versioning

- Drafts: `drafts/<target>.json` (never deployable).
- Immutable releases: `releases/<target>/<release>/<channel>.json`.
- Detached signature of raw release bytes: `<release-manifest-path>.sig` (Ed25519, base64; key ID conveyed by trusted distribution metadata).
- Channel pointer: `catalog/current.json`, referencing the release manifest *and exact SHA-256 of raw manifest bytes*.
- Published catalog must itself be signed before serving. `catalog/catalog.template.json` has deliberately **no active channels**.
- Binary objects: `sha256/<first-two-hex>/<full-sha256>` in private storage. Content-addressed and immutable.
- `delivery.mode=upstream`: launcher downloads from a specific, trusted HTTPS official endpoint when redistribution is not approved. SHA-256/size are still mandatory.

Release versions identify a snapshot; the channel pointer is mutable. Promote a candidate by changing a channel pointer, **not** by editing a published manifest or overwriting blobs.

## Installation algorithm (must be implemented in Launcher)

1. Request **signed** catalog; verify Ed25519 against a public key pinned by the launcher. Reject unknown keys and invalid signatures.
2. Resolve target + channel to immutable release. Fetch exact manifest bytes, verify digest from catalog, then its detached signature; check schema, launcher minimum version and target/loader/runtime compatibility.
3. Determine enabled features and platform. Validate all relative paths before resolving under the isolated instance directory; reject traversal, symlinks, case-insensitive collisions and Windows reserved names. Do not follow links out of instance.
4. Diff against `installed-manifest.lock` and verified local file hashes; trust neither filenames nor timestamps alone.
5. Reuse hash-verified cache at `cache/blobs/sha256/...`. For missing private objects request ephemeral download tickets; for upstream downloads use only trusted HTTPS sources and inspect redirects against SSRF/local network targets.
6. Download to unique temp files, enforce limits and timeouts, stream SHA-256 and byte count, then promote to content-addressed cache only when verified.
7. Build/stage the new managed snapshot **outside** the live mods directory; copy/hardlink verified artifacts as appropriate. Seed-only config must preserve existing user files.
8. Stop Minecraft and atomically switch the target managed set, using a journal and last-known-good snapshot. A partial failed update must never leave a half-installed pack.
9. Mark install successful only after an integrity pass. Offer repair, rollback, per-channel pinning and offline launch of an already installed verified snapshot.

Store logs without secrets, signed download URLs or bearer tokens. Preserve user-added files: never recursively purge `mods/` or `config/`; only remove paths known to be managed by the previous verified lock after backup/conflict handling. Do not overwrite user edits to an owned managed path silently.

## Distribution strategies

**Preferred:** private object storage with short-lived presigned GETs issued by a backend *after* entitlement/access checks. R2 is a candidate, not a currently configured resource.

**Alternative:** authenticated file gateway on the existing VPS with HTTP Range, throttling and observability. This has server bandwidth and operations trade-offs; it still must not expose static private credentials.

**Third-party assets:** official upstream HTTPS URLs where redistribution is not permitted, respecting project rules and source integrity.

## What privacy means (and does not mean)

The manifest repository, release decisions, source scripts and unpublished builds can remain private. **All files actually delivered to a user's PC are extractable**. Access control, packaging, encrypted transit or opaque paths cannot make them permanently secret from a legitimate user. Do not add DRM-like measures that falsely promise otherwise.
