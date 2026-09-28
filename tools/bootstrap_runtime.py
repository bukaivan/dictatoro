"""Build the embedded distribution from pinned official archives, never an old installation.

Run with Windows x64 Python 3.11 with pip available. Downloaded wheels are installed
without resolving dependencies; all inputs are explicitly listed in bootstrap-lock.json.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request
import zipfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from build_runtime import build

def fetch(record,cache):
    name=record['filename']
    if Path(name).name!=name or not record['url'].startswith('https://'):
        raise ValueError('Unsafe locked download')
    target=cache/name
    if not target.exists():
        with urllib.request.urlopen(record['url'],timeout=60) as response:
            data=response.read()
        if hashlib.sha256(data).hexdigest()!=record['sha256']:
            raise ValueError('Download hash mismatch: '+name)
        target.write_bytes(data)
    if hashlib.sha256(target.read_bytes()).hexdigest()!=record['sha256']:
        raise ValueError('Cached hash mismatch: '+name)
    return target

def main():
    if sys.platform!='win32' or sys.version_info[:2]!=(3,11):
        raise RuntimeError('Use Windows x64 Python 3.11 with pip to prepare this pinned runtime')
    parser=argparse.ArgumentParser()
    parser.add_argument('--cache',type=Path,required=True)
    parser.add_argument('--input',type=Path,required=True,help='New temporary input-runtime directory')
    parser.add_argument('--destination',type=Path,default=HERE.parent.parent/'Dictatoro-0.3-runtime-qt6112-final')
    args=parser.parse_args()
    if args.input.exists() or args.destination.exists():
        raise FileExistsError('Input and destination must both be new directories')
    if args.input.resolve()==args.destination.resolve():
        raise ValueError('Input and destination must be different')
    lock=json.loads((HERE/'bootstrap-lock.json').read_text(encoding='utf-8'))
    args.cache.mkdir(parents=True,exist_ok=True)
    embed=fetch(lock['python'],args.cache)
    wheels=[fetch(r,args.cache) for r in lock['wheels']]
    args.input.mkdir(parents=True)
    with zipfile.ZipFile(embed) as archive:
        for entry in archive.infolist():
            target=(args.input/entry.filename).resolve()
            if not target.is_relative_to(args.input.resolve()):raise ValueError('Unsafe archive member')
        archive.extractall(args.input)
    (args.input/'python311._pth').write_text('python311.zip\n.\nLib\\site-packages\n..\nimport site\n',encoding='utf-8')
    subprocess.run([sys.executable,'-m','pip','install','--disable-pip-version-check','--no-deps','--no-index','--no-compile',
                    '--target',str(args.input/'Lib/site-packages'),*[str(p) for p in wheels]],check=True)
    build(args.input,args.destination)
    print('Built pinned runtime:',args.destination)

if __name__=='__main__':main()
