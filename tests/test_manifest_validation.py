"""Regression tests: closed Selection, GitHub assets, licenses and paths."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_manifests import (load_json, safe_https, safe_install_path,  # noqa: E402
                                validate_manifest, validate_catalog, expected_tag)

SCHEMA = load_json(ROOT / "schemas" / "manifest.v2.schema.json")
CATALOG = load_json(ROOT / "schemas" / "catalog.v2.schema.json")
DRAFT = load_json(ROOT / "drafts" / "mc-1.8.9-ornithe.json")


def artifact(license_id="MIT", basis="open-source-license"):
    digest = "a" * 64
    return {
        "id": "test-mod", "kind": "mod", "path": "mods/test-mod.jar",
        "sha256": digest, "bytes": 111, "assetName": f"sha256-{digest}.bin",
        "installPolicy": "managed",
        "origin": {
            "project": "Example", "projectVersion": "1.0.0",
            "sourceRepository": "https://github.com/example/mod",
            "sourceRevision": "deadbeef",
            "licenseSpdx": license_id,
            "licenseEvidenceUrl": "https://github.com/example/mod/blob/deadbeef/LICENSE",
            "redistributionBasis": basis,
        }
    }


class Contracts(unittest.TestCase):
    def test_drafts(self):
        for path in (ROOT / "drafts").glob("*.json"):
            self.assertEqual(validate_manifest(load_json(path), SCHEMA, "drafts/" + path.name), [])

    def test_empty_catalog_is_not_a_release(self):
        self.assertEqual(validate_catalog(load_json(ROOT / "catalog" / "catalog.template.json"), CATALOG), [])

    def test_owned_or_oss_mod(self):
        x = copy.deepcopy(DRAFT)
        x["files"] = [artifact()]
        self.assertEqual(validate_manifest(x, SCHEMA), [])

    def test_no_upstream_or_optional_features(self):
        x = copy.deepcopy(DRAFT)
        x["features"] = [{"id": "personal-mods"}]
        self.assertTrue(validate_manifest(x, SCHEMA))
        x.pop("features")
        entry = artifact()
        entry["delivery"] = {"mode": "upstream", "url": "https://modrinth.com"}
        x["files"] = [entry]
        self.assertTrue(validate_manifest(x, SCHEMA))

    def test_release_assets_tied_to_hash(self):
        x = copy.deepcopy(DRAFT)
        x["files"] = [artifact()]
        x["files"][0]["assetName"] = "sodium.jar"
        self.assertTrue(any("assetName" in e for e in validate_manifest(x, SCHEMA)))

    def test_unreviewed_license_fails_closed(self):
        x = copy.deepcopy(DRAFT)
        x["files"] = [artifact("LicenseRef-Unknown")]
        self.assertTrue(any("not yet reviewed" in e for e in validate_manifest(x, SCHEMA)))

    def test_gpl_requires_source_snapshot(self):
        x = copy.deepcopy(DRAFT)
        x["files"] = [artifact("GPL-3.0-only")]
        self.assertTrue(any("corresponding source" in e for e in validate_manifest(x, SCHEMA)))

    def test_license_with_source_archive(self):
        x = copy.deepcopy(DRAFT)
        a = artifact("GPL-3.0-only")
        digest = "b" * 64
        a["origin"]["correspondingSourceAsset"] = {
            "assetName": f"source-{digest}.zip", "sha256": digest, "bytes": 333
        }
        x["files"] = [a]
        self.assertEqual(validate_manifest(x, SCHEMA), [])

    def test_permission_needs_evidence(self):
        x = copy.deepcopy(DRAFT)
        x["files"] = [artifact("LicenseRef-TFL-Permission", "explicit-permission")]
        self.assertTrue(any("permission" in e for e in validate_manifest(x, SCHEMA)))

    def test_duplicate_casefold_paths(self):
        x = copy.deepcopy(DRAFT)
        a = artifact()
        b = artifact()
        b["id"] = "second"
        b["path"] = "mods/Test-Mod.jar"
        x["files"] = [a, b]
        self.assertTrue(any("duplicate" in e for e in validate_manifest(x, SCHEMA)))

    def test_path_traversal_and_windows_paths(self):
        for path in ["mods/../t.jar", "mods\\t.jar", "mods/CON.jar",
                     "mods/com1.jar", "/mods/t.jar", "mods//t.jar",
                     "mods/t.jar:stream", "mods/t.jar.", "config/x.jar"]:
            self.assertFalse(safe_install_path(path, "mod"), path)
        self.assertTrue(safe_install_path("mods/t.jar", "mod"))
        self.assertTrue(safe_install_path("config/settings.json", "config"))

    def test_mod_must_be_managed(self):
        x = copy.deepcopy(DRAFT)
        a = artifact()
        a["installPolicy"] = "seed-if-absent"
        x["files"] = [a]
        self.assertTrue(any("mods must be managed" in e for e in validate_manifest(x, SCHEMA)))

    def test_url_security(self):
        for url in ["http://github.com/abc", "https://localhost/abc",
                    "https://192.168.0.1/", "https://u:p@github.com/a"]:
            self.assertFalse(safe_https(url))
        self.assertTrue(safe_https("https://github.com/a/b"))

    def test_tag_format(self):
        self.assertEqual(expected_tag("mc-1.8.9-ornithe", "1.0.0"),
                         "selection-mc-1.8.9-ornithe-v1.0.0")

    def test_cannot_publish_empty_release(self):
        x = copy.deepcopy(DRAFT)
        x["status"] = "published"
        self.assertTrue(validate_manifest(x, SCHEMA))


if __name__ == "__main__":
    unittest.main()
