import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from import_prism import inspect_prism_zip, InvalidPrismArchive


def jar(mod_id='example', version='1.0.0'):
    data = io.BytesIO()
    with ZipFile(data, 'w', ZIP_DEFLATED) as out:
        out.writestr('fabric.mod.json',
                     json.dumps({'id': mod_id, 'version': version, 'license': 'MIT'}))
    return data.getvalue()


def prism(path, mc='1.8.9', extra=None):
    with ZipFile(path, 'w') as z:
        z.writestr('mmc-pack.json', json.dumps({'components': [
            {'uid': 'net.minecraft', 'version': mc},
            {'uid': 'net.fabricmc.fabric-loader', 'version': '0.20.1'}]}))
        z.writestr('minecraft/mods/a.jar', jar())
        for name, data in (extra or {}).items():
            z.writestr(name, data)


class PrismImport(unittest.TestCase):
    def test_no_personal_files(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'p.zip'
            prism(path, extra={'minecraft/servers.dat': 'SECRET',
                               'minecraft/tfl-maps/user-cache.bin': 'SECRET'})
            obj = inspect_prism_zip(path)
            self.assertEqual(obj['minecraft']['loaderVersion'], '0.20.1')
            self.assertEqual(len(obj['mods']), 1)
            self.assertNotIn('SECRET', json.dumps(obj))
            self.assertFalse(obj['releaseReady'])

    def test_wrong_game_version(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'p.zip'
            prism(path, mc='1.12.2')
            with self.assertRaises(InvalidPrismArchive):
                inspect_prism_zip(path)

    def test_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'p.zip'
            prism(path, extra={'../bad': 'no'})
            with self.assertRaises(InvalidPrismArchive):
                inspect_prism_zip(path)

    def test_staging_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'p.zip'
            prism(path)
            obj = inspect_prism_zip(path, Path(temp) / 'staging')
            blob = Path(temp) / 'staging' / 'assets' / obj['mods'][0]['assetName']
            self.assertTrue(blob.exists())
            self.assertEqual(blob.stat().st_size, obj['mods'][0]['bytes'])

    def test_duplicate_mod_id(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'p.zip'
            prism(path, extra={'minecraft/mods/b.jar': jar(mod_id='example', version='2.0.0')})
            with self.assertRaises(InvalidPrismArchive):
                inspect_prism_zip(path)


if __name__ == '__main__':
    unittest.main()
