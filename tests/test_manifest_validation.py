"""Contract and path-security tests for the distribution validator."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_manifests import (  # noqa: E402
    load_json, safe_https, safe_install_path, validate_manifest, validate_catalog
)

SCHEMA = load_json(ROOT / "schemas" / "manifest.v1.schema.json")
CATALOG_SCHEMA = load_json(ROOT / "schemas" / "catalog.v1.schema.json")
EXAMPLE = load_json(ROOT / "drafts" / "mc-1.8.9-ornithe.json")


def owned_file():
    sha = "a" * 64
    return {
        "id": "tfl-core-test", "kind": "mod", "path": "mods/tfl-core.jar",
        "sha256": sha, "bytes": 123, "installPolicy": "managed",
        "delivery": {"mode": "private-object", "objectKey": f"sha256/aa/{sha}"},
        "origin": {"project": "TFL Core", "homepage": "https://github.com/TFLivesStudio",
                   "license": "proprietary", "redistribution": "owned"},
    }


class ContractTests(unittest.TestCase):
    def test_drafts_validate(self):
        for path in (ROOT / "drafts").glob("*.json"):
            self.assertEqual(validate_manifest(load_json(path), SCHEMA, f"drafts/{path.name}"), [])

    def test_catalog_template_valid(self):
        catalog = load_json(ROOT / "catalog" / "catalog.template.json")
        self.assertEqual(validate_catalog(catalog, CATALOG_SCHEMA, False), [])

    def test_owned_private_object_valid(self):
        manifest = copy.deepcopy(EXAMPLE)
        manifest["files"] = [owned_file()]
        self.assertEqual(validate_manifest(manifest, SCHEMA), [])

    def test_upstream_only_private_object_rejected(self):
        manifest = copy.deepcopy(EXAMPLE)
        item = owned_file()
        item["origin"]["redistribution"] = "upstream-only"
        manifest["files"] = [item]
        self.assertTrue(validate_manifest(manifest, SCHEMA))

    def test_authorized_without_evidence_rejected(self):
        manifest = copy.deepcopy(EXAMPLE)
        item = owned_file()
        item["origin"]["redistribution"] = "authorized"
        manifest["files"] = [item]
        self.assertTrue(any("evidence" in e for e in validate_manifest(manifest, SCHEMA)))

    def test_content_address_must_match(self):
        manifest = copy.deepcopy(EXAMPLE)
        item = owned_file()
        item["delivery"]["objectKey"] = "sha256/ff/" + "f" * 64
        manifest["files"] = [item]
        self.assertTrue(any("objectKey" in e for e in validate_manifest(manifest, SCHEMA)))

    def test_case_insensitive_collision(self):
        manifest = copy.deepcopy(EXAMPLE)
        item = owned_file()
        other = copy.deepcopy(item)
        other["id"] = "different"
        other["path"] = "mods/TFL-Core.jar"
        manifest["files"] = [item, other]
        self.assertTrue(any("duplicate install path" in e for e in validate_manifest(manifest, SCHEMA)))

    def test_feature_must_be_declared(self):
        manifest = copy.deepcopy(EXAMPLE)
        item = owned_file()
        item["featureId"] = "unknown"
        manifest["files"] = [item]
        self.assertTrue(any("unknown feature" in e for e in validate_manifest(manifest, SCHEMA)))

    def test_paths_reject_traversal_and_windows_tricks(self):
        unsafe = [
            "/mods/core.jar", "mods/../core.jar", "mods//core.jar",
            "mods\\core.jar", "mods/CON.jar", "mods/com1.txt",
            "mods/nul.txt", "mods/core.jar.", "mods/core.jar:stream",
            "config/core.jar", "mods/a?b.jar",
        ]
        for path in unsafe:
            self.assertFalse(safe_install_path(path, "mod"), path)
        self.assertTrue(safe_install_path("mods/core.jar", "mod"))

    def test_urls_refuse_local_and_insecure(self):
        for url in ("http://example.com/x.jar", "https://localhost/x.jar",
                    "https://127.0.0.1/x.jar", "https://u:p@example.com/x.jar",
                    "https://local.internal/x.jar"):
            self.assertFalse(safe_https(url), url)
        self.assertTrue(safe_https("https://cdn.modrinth.com/example.jar"))


if __name__ == "__main__":
    unittest.main()
