# Optional signed launcher metadata

The manifest v2 contract accepts optional `iconAsset` and `capabilities`. Existing
published manifests, catalogs, signatures and game artifacts remain unchanged.

`iconAsset` has `assetName: "icon-<sha256>.png"`, lowercase `sha256`, and `bytes`
between 1 and 1048576. It belongs to the same immutable GitHub release as its
signed manifest. The launcher additionally requires a valid PNG header and
dimensions from 1 to 512 pixels per side, verifies size and digest, and uses the
packaged TFL logo if metadata is absent or retrieval fails. Local instance state
cannot supply an arbitrary icon URL. Release preflight verifies an optional icon
alongside other assets.

`capabilities: { "shaders": true }` explicitly declares shader compatibility.
It is not inferred from Fabric, Ornithe or the Minecraft version. The launcher
recognizes shader support in the exact historical 1.8.9 manifest separately;
unrecognized releases without this capability do not advertise it.

Future releases using these fields must set `minimumLauncherVersion` to
`0.15.4-beta.2` or a newer compatible launcher and follow the existing candidate,
validation, approval and signing process. This launcher checks that signed
minimum before parsing extension fields; older launchers reject unknown fields. This change does not add an icon to any
published client, authorize a new game release, or publish signed content.

Validation: `python scripts/validate_manifests.py` and
`python -m unittest discover -s tests -v`; CI also checks repository policy.
