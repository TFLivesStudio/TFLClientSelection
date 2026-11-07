#!/usr/bin/env python3
"""Safe Prism ZIP review importer. NEVER publishes releases or personal files."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
from zipfile import ZipFile, BadZipFile

MAX_ENTRIES = 40000
MAX_UNCOMPRESSED = 4 * 1024**3
MAX_JAR_BYTES = 512 * 1024**2


class InvalidPrismArchive(ValueError):
    pass


def digest_file(fp):
    h = hashlib.sha256()
    while chunk := fp.read(1024 * 1024):
        h.update(chunk)
    return h.hexdigest()


def _inspect_member(info):
    name = info.filename
    if ('\\' in name or name.startswith('/') or '\x00' in name
            or any(part in ('.', '..', '') for part in name.rstrip('/').split('/'))):
        raise InvalidPrismArchive('Unsafe ZIP member')
    if info.create_system == 3 and stat.S_ISLNK(info.external_attr >> 16):
        raise InvalidPrismArchive('ZIP symlink refused')


def _components(z):
    try:
        data = json.loads(z.read('mmc-pack.json'))
    except (KeyError, ValueError) as err:
        raise InvalidPrismArchive('Missing/invalid Prism mmc-pack.json') from err
    components = {str(x['uid']): str(x.get('version') or x.get('cachedVersion') or '')
                  for x in data.get('components', [])
                  if isinstance(x, dict) and x.get('uid')}
    if components.get('net.minecraft') != '1.8.9':
        raise InvalidPrismArchive('Prism export is not Minecraft 1.8.9')
    if 'net.fabricmc.fabric-loader' not in components:
        raise InvalidPrismArchive('Ornithe Gen2 export lacks Fabric Loader component')
    return components


def inspect_prism_zip(zip_path: Path, staging_dir: Path | None = None):
    """Return a privacy-safe inventory. Redistribution rights are never inferred."""
    with ZipFile(zip_path) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_ENTRIES or sum(i.file_size for i in infos) > MAX_UNCOMPRESSED:
            raise InvalidPrismArchive('Archive exceeds safety limits')
        names = set()
        for info in infos:
            _inspect_member(info)
            if info.filename in names:
                raise InvalidPrismArchive('Duplicate ZIP entry')
            names.add(info.filename)
        components = _components(archive)
        active = sorted((info for info in infos
                         if re.fullmatch(r'minecraft/mods/[^/]+\.jar', info.filename, re.I)),
                        key=lambda info: info.filename.casefold())
        if not active:
            raise InvalidPrismArchive('No active JARs in minecraft/mods')
        mods = []
        mod_ids, installed_names = set(), set()
        for info in active:
            if info.file_size > MAX_JAR_BYTES or info.file_size == 0:
                raise InvalidPrismArchive('JAR exceeds size limits')
            path = PurePosixPath(info.filename)
            if path.name.casefold() in installed_names:
                raise InvalidPrismArchive('Case-insensitive JAR filename collision')
            installed_names.add(path.name.casefold())
            with archive.open(info) as fp:
                sha = digest_file(fp)
            try:
                with ZipFile(io.BytesIO(archive.read(info))) as jar:
                    mod = json.loads(jar.read('fabric.mod.json'))
                    if not isinstance(mod, dict):
                        raise ValueError('Invalid mod metadata')
                    mod_id, version = mod['id'], mod['version']
                    if not isinstance(mod_id, str) or not isinstance(version, str) or not mod_id or not version:
                        raise ValueError('Missing ID/version')
                    natives = [item.filename for item in jar.infolist()
                               if item.filename.lower().endswith(('.dll', '.so', '.dylib'))]
            except (BadZipFile, KeyError, ValueError, TypeError, UnicodeDecodeError) as err:
                raise InvalidPrismArchive('Invalid Fabric mod JAR') from err
            if mod_id.casefold() in mod_ids:
                raise InvalidPrismArchive('Duplicate mod ID')
            mod_ids.add(mod_id.casefold())
            mods.append({'id': mod_id, 'version': version, 'name': mod.get('name') or mod_id,
                         'filename': path.name, 'path': f'mods/{path.name}', 'sha256': sha,
                         'bytes': info.file_size, 'assetName': f'sha256-{sha}.bin',
                         'declaredLicense': mod.get('license'), 'licenseReview': 'pending',
                         'depends': mod.get('depends', {}), 'breaks': mod.get('breaks', {}),
                         'nativeFilesEmbedded': natives})
            if staging_dir:
                dst = staging_dir / 'assets' / f'sha256-{sha}.bin'
                dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists():
                    with archive.open(info) as src, dst.open('wb') as out:
                        shutil.copyfileobj(src, out, 1024 * 1024)
                with dst.open('rb') as fp:
                    if digest_file(fp) != sha:
                        raise InvalidPrismArchive('Staging hash mismatch')
        shaders = [info for info in infos
                   if re.fullmatch(r'minecraft/shaderpacks/[^/]+\.zip', info.filename, re.I)]
        result = {
            'status': 'unpublished-review-only', 'targetId': 'mc-1.8.9-ornithe',
            'minecraft': {'version': '1.8.9', 'loader': 'ornithe-gen2',
                          'loaderVersion': components['net.fabricmc.fabric-loader'], 'javaMajor': 25},
            'mods': mods, 'shaderpacksPendingRightsReview': len(shaders),
            'excluded': ['tfl-maps', 'tfl-far-terrain', 'mod-remapping-api',
                         'player configs/options', 'servers.dat', 'usercache.json',
                         'crash logs', 'shaderpacks'],
            'releaseReady': False,
            'reason': 'No public release until redistribution rights, corresponding source and launcher boot tests are verified.',
        }
    if staging_dir:
        (staging_dir / 'PRIVATE-STAGING-NOT-PUBLIC-RELEASE.txt').write_text(
            result['reason'] + '\n', encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prism_zip', type=Path)
    parser.add_argument('--inventory-out', type=Path, required=True)
    parser.add_argument('--staging-dir', type=Path)
    args = parser.parse_args()
    inventory = inspect_prism_zip(args.prism_zip, args.staging_dir)
    args.inventory_out.parent.mkdir(parents=True, exist_ok=True)
    args.inventory_out.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n',
                                  encoding='utf-8')
    print(f"Audited {len(inventory['mods'])} active JARs; publication blocked pending approvals")


if __name__ == '__main__':
    main()
