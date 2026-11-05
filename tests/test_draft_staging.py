"""Exercise draft staging without weakening the published release contract."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]

class DraftStagingTest(unittest.TestCase):
    def test_explicit_draft_checks_bytes_sources_notices_and_keeps_publication_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            def asset(name,data):
                digest=hashlib.sha256(data).hexdigest();name=name.format(sha=digest);(folder/name).write_bytes(data)
                return dict(assetName=name,sha256=digest,bytes=len(data))
            def archive(name,entries):
                path=folder/name
                with zipfile.ZipFile(path,'w') as z:
                    for entry,data in entries.items():z.writestr(entry,data)
                return path.read_bytes()
            source=asset('source-{sha}.zip',archive('source.zip',{'LICENSE':'test fixture GPL notice','src/Example.java':'// fixture'}))
            binary=asset('sha256-{sha}.bin',archive('example.jar',{'fabric.mod.json':'{"id":"example","version":"1.0.0"}'}))
            notices=asset('notices-{sha}.zip',archive('notices.zip',{'licenses/example.txt':'test fixture GPL notice'}))
            manifest=dict(schemaVersion=2,packId='tfl-selection',targetId='mc-1.8.9-ornithe',release='0.0.0-dev.1',status='draft',selectionMode='locked',minecraft=dict(version='1.8.9',loader='ornithe-gen2',javaMajor=25),noticesAsset=notices,files=[dict(id='example',kind='mod',path='mods/example.jar',installPolicy='managed',**binary,origin=dict(project='Example fixture',projectVersion='1.0.0',sourceRepository='https://github.com/example/example',sourceRevision='1234567',licenseSpdx='GPL-3.0-only',licenseEvidenceUrl='https://github.com/example/example/blob/1234567/LICENSE',redistributionBasis='open-source-license',correspondingSourceAsset=source))])
            path=folder/'draft.json';path.write_text(json.dumps(manifest))
            base=['python',str(ROOT/'scripts/verify_release_assets.py'),'--manifest',str(path),'--assets',str(folder)]
            def run(*args):return subprocess.run(base+list(args),cwd=ROOT,capture_output=True,text=True)
            self.assertNotEqual(0,run().returncode,'A draft must never be certified as published')
            result=run('--draft');self.assertEqual(0,result.returncode,result.stdout+result.stderr);self.assertIn('NOT certified',result.stdout)
            (folder/binary['assetName']).write_bytes(b'wrong bytes')
            self.assertNotEqual(0,run('--draft').returncode,'Draft staging must still enforce binary hashes')
            (folder/binary['assetName']).write_bytes((folder/'example.jar').read_bytes());(folder/source['assetName']).unlink()
            self.assertNotEqual(0,run('--draft').returncode,'Copyleft corresponding sources remain mandatory')

if __name__=='__main__':unittest.main()
