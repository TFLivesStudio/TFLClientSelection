# Launcher ↔ Selection distribution protocol (proposal v1)

This document defines the **target interface**, not an already-running API. No URL, credentials, signing key or binary is deployed yet.

## Trust chain

Launcher ships trusted Ed25519 **public** key(s). Backend/secure release job signs the **exact raw UTF-8 JSON bytes** of both published catalog and immutable manifests. No JSON reserialization before verifying signatures. Key ID is transport metadata; an unknown/unpinned key must be rejected. Signatures do not replace TLS.

## Suggested endpoints

`GET /v1/selection/catalog`

- Response: `catalog/current.json` bytes with headers `X-TFL-Key-Id` and `X-TFL-Signature-Ed25519` (base64 of 64-byte signature over raw response bytes).
- Cache may use ETag, but a response is trusted only after signature verification.
- No draft or internal-only channel is exposed to an unauthorized requester.

`GET /v1/selection/manifests/{targetId}/{release}/{channel}`

- Returns raw bytes of an immutable, published manifest, with the same signature headers.
- Caller checks manifest raw SHA-256 against the signed catalog pointer.
- Rejects revoked release/unknown target/invalid entitlement; never serve arbitrary filesystem paths.

`POST /v1/selection/download-tickets`

Example request:

```json
{
  "targetId": "mc-1.8.9-ornithe",
  "release": "1.0.0",
  "channel": "stable",
  "artifactIds": ["tfl-core"]
}
```

Example response *shape* (illustrative, **not a valid download ticket**):

```json
{
  "tickets": [
    {
      "artifactId": "tfl-core",
      "url": "https://<presigned-object-url>",
      "expiresAt": "2030-01-01T00:05:00Z"
    }
  ]
}
```

- Server authenticates/authorizes access to the **specific published release and asset IDs** before issuing URLs. Must not accept unrestricted object keys from the caller.
- URLs are ephemeral bearer credentials, held in memory only, never logged or saved in lock files.
- Client retries by requesting new tickets if expired, validates redirects/HTTPS and verifies SHA-256 and bytes after download.
- `upstream` files do not require tickets; use `delivery.url` subject to provenance rules.

## Manifest contract

`schemas/manifest.v1.schema.json` is authoritative. Top-level fields:
- `targetId` binds the exact Minecraft version + loader combination; `minecraft.javaMajor` selects the required runtime.
- `release` is immutable and can be promoted among channels only by producing an appropriate signed channel manifest or channel-independent release contract in a subsequent schema revision.
- `features` declares optional mod groups; files may reference `featureId`.
- `files` carries install-relative path, exact sha256, byte size, kind, policy and source rights.
- `installPolicy=managed`: update only after making backups for potential user edits. `seed-if-absent`: write default if path does not exist.
- `delivery.mode=private-object`: request ephemeral URL from server using the approved artifact ID. Object key is content-addressed but not a credential.
- `delivery.mode=upstream`: download only from validated HTTPS, verify exact hash/bytes and respect official source terms.

**Important:** do not infer a loader installer, Java runtime or library set solely from the mod manifest. Loader/bootstrap artifact acquisition is a separate launcher concern and must be pinned/tested per target.

## Errors and behavior

- Invalid catalog signature, malformed manifest, hash mismatch, unsafe path, incompatible Java, revoked asset or unauthorized request: **fail closed** (do not install).
- Interrupted download: resume via HTTP Range only if the source supports it and the final SHA-256 is verified.
- Offline: launch only an already installed, locally verified and permitted snapshot. Do not claim an offline update succeeded.
- Failed update: leave current snapshot untouched; surface an actionable error and retain previous known-good version.

## Integration boundary

Do not modify TFL Core or launcher code in this repository. Their maintainers implement the published `schemaVersion=1` contract once agreed. Incompatible changes increment `schemaVersion` and are tested against real launcher builds.
