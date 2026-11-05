#!/usr/bin/env python3
"""Prepare reviewed Audit 5 draft assets; never install, sign or publish a pack."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('core', 'upstream', 'sources', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    manifest_path = ROOT / 'drafts/mc-1.8.9-ornithe.json'
    manifest = json.loads(manifest_path.read_text())
    locks = json.loads((args.core / 'tools/integrations/optimizer-sources.lock.json').read_text())
    sources = json.loads((args.sources / 'source-assets.json').read_text())
    if manifest['status'] != 'draft' or {f['id'] for f in manifest['files']} != {'zirconium', 'starlight'}:
        raise ValueError('This staging command only handles the reviewed two-optimizer draft')
    args.output.mkdir(parents=True, exist_ok=False)
    notices = args.output / manifest['noticesAsset']['assetName']
    with zipfile.ZipFile(notices, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, lock in zip(('zirconium', 'starlight'), locks):
            row = next(f for f in manifest['files'] if f['id'] == name)
            if row['sha256'] != lock['builtSha256'] or row['origin']['sourceRevision'] != lock['revision']:
                raise ValueError(f'{name}: reviewed manifest and build lock differ')
            folder = args.upstream / name
            shutil.copy2(folder / 'build/libs' / lock['jar'], args.output / row['assetName'])
            shutil.copy2(args.sources / sources[name]['assetName'], args.output / row['origin']['correspondingSourceAsset']['assetName'])
            text = (f"{lock['repo']}\nRevision: {lock['revision']}\nLicense: {lock['license']}\n"
                    'TFL adaptation and build provenance: corresponding source archive.\n\n'
                    + (folder / 'LICENSE').read_text()).encode()
            info = zipfile.ZipInfo(f'licenses/{name}.txt', (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, text)
        info = zipfile.ZipInfo('COPYING-GPL-3.0.txt', (1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, (args.core / 'vendor/trs-client/LICENSE').read_bytes())
    subprocess.run([sys.executable, str(ROOT / 'scripts/verify_release_assets.py'), '--draft',
                    '--manifest', str(manifest_path), '--assets', str(args.output)], check=True)
    shutil.copy2(manifest_path, args.output / manifest_path.name)
    sums = ''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n'
                   for p in sorted(args.output.iterdir()) if p.is_file())
    (args.output / 'SHA256SUMS.txt').write_text(sums)


if __name__ == '__main__':
    main()
