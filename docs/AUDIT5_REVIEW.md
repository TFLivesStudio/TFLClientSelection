# Audit 5: two independent optimizer candidates

`feat/audit5-optimizer-candidates` adds Zirconium and Legacy Starlight to the **draft** 1.8.9 manifest. It does not change a published release, signed catalog, managed launcher profile, or existing selected mod. The starting manifest had no entries; these two additions are not a complete launchable Selection pack.

Both use Java 25 and Ornithe Gen2. Zirconium is built from `Coccocoahelper/Zirconium-Ornithe@d687019623a153e03a9210e05b3eea0d33059cf7` with the three narrowly scoped TFL patches; Starlight uses `Polyfrost/Legacy-Starlight@ed5214d0f9ff787a43aafd915c31c793620ef280` with its build plugin pinned. The source revision, license evidence, full corresponding source ZIP, per-mod notice, installed filename, content-addressed release asset name, byte count and SHA-256 are in the manifest. Neither optimizer is included inside TFL Core.

Core acceptance evidence and reproduction scripts are in `TFLivesStudio/TFLClientMOD`, branch `feat/audit5-integrations`, `docs/evidence/audit5/` and `tools/integrations/`. Individual and combined native tests cover LWJGL2, Legacy LWJGL3 and Argentum/Extras, map fog and fonts, resource reload, dimensions, lighting and cached terrain. Active Complementary shaders were tested separately with Lucerna. The complete interface/map scenario passed 184 checks. Core baseline/Sodium/Iris acceptance remains separately recorded in that repository.

Measurements use software rendering, not a physical GPU. The controlled 4,096-block lighting test showed shorter update times with Starlight; general FPS improvement was not demonstrated. Zirconium's SPNG decoder was faster on small PNGs and slower on 1,024 px PNGs. The patch therefore keeps full-resolution ImageIO decoding for larger textures; it never downsizes resource packs. RGBA, crop, image lifetime and decoder selection tests passed. Both artifacts reproduced their pinned hashes from pristine sources.

The local staged binaries, notices and sources passed:

```sh
python scripts/validate_manifests.py
python -m unittest discover -s tests -v
python scripts/check_repo_policy.py
python scripts/verify_release_assets.py --draft --manifest drafts/mc-1.8.9-ornithe.json --assets /path/to/staging
```

`--draft` verifies the actual bytes, sources and notices; it cannot certify publication or launcher readiness. Without that flag the staging command still rejects drafts. The regression suite checks that corrupt bytes and missing copyleft sources fail.

Before any official release: approve this candidate and the remaining curated inventory; stage all assets in **this repository's** GitHub Releases, implement/verify the pinned launcher bootstrap, run the complete published-pack matrix on physical hardware, and sign/promote the immutable manifest through the separate catalog process. No signing material, binary files or credentials are committed here. No public release or channel promotion is performed by this change.
