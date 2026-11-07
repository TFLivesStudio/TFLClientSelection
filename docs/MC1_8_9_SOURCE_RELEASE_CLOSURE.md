# TFL Selection 1.8.9 — source and publication closure

## Exact current ZIP vs candidate source trees

The owner's Prism ZIP contains exactly five mods still missing a public **exact-hash** GitHub Release. These source repositories **do not authorize substituting JARs** with later/older versions.

| JAR | Candidate corresponding source | License checked | Remaining proof |
|---|---|---|---|
| `lucerna-0.1.5-tfl.2.jar` | [jonathanthxd/lucerna, work/tfl-far-terrain-shader-stability](https://github.com/jonathanthxd/lucerna/tree/work/tfl-far-terrain-shader-stability) @ `45f3fcde` | LGPL-3.0-only, `LICENSE` (and GPLv3 `COPYING`) | Branch declares **0.1.5-tfl.2**; identify **exact build commit** matching SHA-256 `7f9d396861998b2ea8562379e22320a4547a2b5cc18567d97d2dd042ed42e451` |
| `amplio-0.1.1+1.8.9.jar` | [jonathanthxd/amplio, main](https://github.com/jonathanthxd/amplio) @ `deadbad272` | MIT (root `LICENSE`) | Branch declares **0.1.1**; identify exact build commit matching SHA-256 `05d18d7760d8c855fc33e32e3c8b3026c8217d5a1c05a768a5769c8c7c83315f`; separately review embedded NVIDIA DLL distribution conditions |
| `pulse-1.0.0.jar` | [QuicksilverMC/Pulse](https://github.com/QuicksilverMC/Pulse) | GPL-3.0-only, root `LICENSE` | Find precise source revision matching original JAR, include license/complete corresponding source |
| `legacy-lwjgl3-1.4.10.jar` | [moehreag/legacy-lwjgl3](https://github.com/moehreag/legacy-lwjgl3) | **LGPL-2.1**, root `LICENSE` | Find precise 1.4.10 source revision; include build scripts, license and source (not `GPL-2.1`) |
| `soundfix-1.1.0+mc1.8.9.jar` | [moehreag/soundfix, ornithe/1.8.9](https://github.com/moehreag/soundfix/tree/ornithe/1.8.9) | **LGPL-3.0** declared in `fabric.mod.json`; root LICENSE absent in inspected branch | Confirm complete license/notice evidence, exact build source revision and source archive |

## Immediate next operation: prepare author-verified artifacts for publication

1. Preserve **all five original JARs** exactly as exported. Available in the owner's chat private staging archive `TFLSelection_189_PENDIENTES_PARA_RELEASE_PRIVADO.zip`, each stored as `assets/sha256-<original-digest>.bin` (name is required by the v2 manifest).
2. Identify the matching source revision for each built JAR, and prepare a ZIP of complete corresponding source + license notices for each GPL/LGPL JAR. Use the user's two forks as candidates; their *branch version strings alone are not sufficient* proof.
3. For Amplio, check NVIDIA DLSS runtime distribution terms and notices for the exact bundled binary. A MIT project license alone does not license embedded third-party binaries.
4. Publish only the **five** approved content-addressed binaries and necessary `source-<digest>.zip`/`notices-<digest>.zip` in an immutable **TFL Selection** GitHub Release. The six author-hosted JARs are already pinned by official GitHub Release tag/name/digest and are **not mirrored**.
5. Use the guarded builder/publisher scripts under `scripts/` to generate/verify the exact signed manifest with Ed25519. Generate/manage the private key via a protected trusted environment, never commit it.
6. Verify all 11 remote URLs, sigs, hashes and byte lengths; then publish the signed catalog channel (initially **beta/preview**, not stable) with incremented `generation`.
7. **Separate launcher integration:** installation cannot be considered end-to-end tested until TFL Client supports Ornithe Gen2 Java 25, both GitHub delivery types, signature validation, offline cache and rollback. The launcher work itself is a separate tracked issue.

**Definition of done (repository/distribution side):** all 11 original mods have reachable exact verified GitHub assets; signed immutable full manifest/catalog exists; notices and corresponding-source obligations fulfilled; CI and remote download verification pass. Reaching this milestone does **not** imply end-to-end launcher boot certification.

## Why source provenance matters

License metadata describes legal rights, but does not certify that a previously built binary matches the current repository head. For Lucerna, `main` currently declares `0.1.4`, while branch `work/tfl-far-terrain-shader-stability` declares `0.1.5-tfl.2`. For Amplio the fork `main` declares `0.1.1`. Pin immutable source commits that actually produced each binary before release.
