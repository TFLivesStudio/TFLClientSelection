# AGENTS.md — TFL Selection

## Scope
This is the **private modpack manifest and release metadata** repository, not TFL Core source code, not the launcher, and not a place for live API secrets.

## Non-negotiable constraints
- Do not commit JARs, complete modpacks, GitHub tokens, storage credentials, signing private keys or any personal data.
- A GitHub private repo is **not** a private direct-download API for a public launcher.
- Do not claim that a modpack cannot be extracted after installing it.
- Never mark a third-party artifact as authorized to redistribute without recording verifiable license evidence and checking the exact version.
- Do not publish a new channel entry until all its blobs exist and hashes/sizes are verified.
- Never overwrite existing immutable `releases/<target>/<release>/<channel>.json` or its detached signature.
- Only edit `drafts/` to iterate on planned mod selections. Keep drafts outside the release catalog.
- Preserve user-owned mods and modified configs on update; never delete arbitrary unmanaged files.
- The final installer must treat all manifest paths as untrusted and reject traversal, symlinks and collisions.

## Implementation conventions
- Manifest and catalog contract: `schemas/`; docs: `docs/`.
- Prefer stdlib Python for tools; schema validation uses the pinned `jsonschema` dependency.
- Run `python scripts/validate_manifests.py` and `python -m unittest discover -s tests -v`.
- New targets require a draft, catalog target declaration, tests and launcher compatibility review.
- Review releases through pull requests; no automatic publishing on every push.
