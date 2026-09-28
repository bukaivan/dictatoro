"""Prepare pinned Base weights for packaging; never called by the installed app."""
import hashlib
import json
from pathlib import Path
import urllib.request

root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'tools/bundled-base.json').read_text(encoding='utf-8'))
folder=root/'models/base';folder.mkdir(parents=True,exist_ok=True)
for row in manifest['files']:
    name=row['filename']
    if Path(name).name!=name:raise ValueError('Unsafe model filename')
    target=folder/name
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==row['sha256']:
        continue
    with urllib.request.urlopen(row['url'],timeout=120) as response:
        data=response.read()
    if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:
        raise ValueError('Model download failed verification: '+name)
    temporary=target.with_suffix(target.suffix+'.part')
    temporary.write_bytes(data);temporary.replace(target)
print('Bundled Base verified and ready')
