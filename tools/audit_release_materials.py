"""Offline provenance/notices checks; not a legal opinion or a security clearance."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def audit(source, runtime, cache):
    legal = source / 'legal'
    lock = json.loads((source / 'tools/bootstrap-lock.json').read_text('utf-8'))
    failures = []
    legal_files = [p for p in legal.rglob('*') if p.is_file()]
    legal_hashes = {sha(p.read_bytes()) for p in legal_files}
    checked_legal = 0
    for row in json.loads((legal / 'legal-manifest.json').read_text('utf-8')):
        path = legal / row['file']
        if not path.is_file() or sha(path.read_bytes()) != row['sha256']:
            failures.append('Legal manifest mismatch: ' + row['file'])
        checked_legal += 1

    native_origins = {}
    packages = []
    for record in [lock['python'], *lock['wheels']]:
        archive_path = cache / record['filename']
        if not archive_path.is_file() or sha(archive_path.read_bytes()) != record['sha256']:
            failures.append('Missing or changed locked archive: ' + record['filename'])
            continue
        notices = []
        with zipfile.ZipFile(archive_path) as archive:
            for entry in archive.infolist():
                if entry.is_dir():
                    continue
                name = entry.filename
                native = Path(name).suffix.lower() in {'.dll', '.pyd', '.exe'}
                notice = bool(re.search(r'licen[cs]e|copying|notice|copyright', Path(name).name, re.I))
                if not (native or notice):
                    continue
                digest = sha(archive.read(entry))
                if native:
                    native_origins.setdefault(digest, []).append({
                        'archive': record['filename'], 'member': name,
                        'archive_sha256': record['sha256'], 'url': record['url']})
                if notice:
                    copied = digest in legal_hashes
                    notices.append({'member': name, 'sha256': digest, 'in_legal': copied})
                    if not copied:
                        failures.append('Missing original notice: ' + record['filename'] + ':' + name)
        fallbacks = []
        if not notices:
            fallback_names = {
                'ctranslate2': 'upstream/CTranslate2-MIT.txt',
                'flatbuffers': 'upstream/flatbuffers-Apache.txt',
                'tokenizers': 'upstream/tokenizers-Apache.txt',
                'tqdm': 'components/tqdm',
            }
            package = record['filename'].split('-')[0]
            fallback = fallback_names.get(package)
            if fallback and (legal / fallback).exists():
                fallbacks.append(fallback)
            else:
                failures.append('No packaged or supplemental notice: ' + record['filename'])
        packages.append({'archive': record['filename'], 'hash_verified': True, 'notices': notices,
                         'supplemental_notices': fallbacks})

    native_files = []
    for path in sorted(runtime.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in {'.dll', '.pyd', '.exe'}:
            continue
        if path.name.lower() == 'libiomp5md.dll':
            # Excluded by setup.iss; separately installed from Intel, not delivered here.
            continue
        digest = sha(path.read_bytes())
        origins = native_origins.get(digest, [])
        relative = path.relative_to(runtime).as_posix()
        native_files.append({'file': relative, 'sha256': digest, 'origins': origins})
        if not origins:
            failures.append('No locked origin for native file: ' + relative)

    for provenance in ('download-provenance.json', 'additional-provenance.json'):
        records = json.loads((legal / provenance).read_text('utf-8'))
        if isinstance(records, dict):
            records = records['downloads']
        for row in records:
            if 'file' in row and 'sha256' in row:
                path = legal / row['file']
                if not path.is_file() or sha(path.read_bytes()) != row['sha256']:
                    failures.append('Source/notice provenance mismatch: ' + row['file'])

    model = json.loads((legal / 'bundled-base-provenance.json').read_text('utf-8'))
    model_failures = []
    for row in model['files']:
        path = source / 'models/base' / row['filename']
        if not path.is_file() or sha(path.read_bytes()) != row['sha256']:
            model_failures.append(row['filename'])
    failures.extend('Bundled model missing/changed: ' + name for name in model_failures)
    # Check the newly collected nested component records independently of the
    # aggregate manifest, including the corresponding Rust source archives.
    ct_root = legal / 'components/CTranslate2-4.8.2-dependencies'
    ct = json.loads((ct_root / 'provenance.json').read_text('utf-8'))
    rust_root = legal / 'components/Rust-dependency-notices'
    rust = json.loads((rust_root / 'provenance.json').read_text('utf-8'))
    records = [(ct_root, row) for row in ct['files']]
    records += [(rust_root, row) for package in rust['packages'] for row in package.get('notices', [])]
    records += [(legal, row) for row in rust['source_archives']]
    records += [(legal, row) for row in json.loads((rust_root / 'copyleft-source-provenance.json').read_text('utf-8'))]
    for parent, row in records:
        path = parent / row['file']
        if not path.is_file() or sha(path.read_bytes()) != row['sha256']:
            failures.append('Nested dependency provenance mismatch: ' + row['file'])
    return {
        'scope': 'Pinned binary origin, original notices, legal/source/model hashes only',
        'legal_completeness_certified': False,
        'all_native_transitive_licenses_verified': False,
        'archives_verified': len(packages),
        'legal_manifest_entries_checked': checked_legal,
        'nested_dependency_records_checked': len(records),
        'rust_source_lock_packages': len(rust['packages']),
        'rust_superset_manual_review': [r['name'] + ' ' + r['version'] for r in rust['packages']
                                       if r.get('manual_review') or r.get('error')],
        'packages': packages, 'native_files': native_files,
        'base_files_verified': not model_failures,
        'failures': failures,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.source, args.runtime, args.cache)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), 'utf-8')
    print('Archives:', report['archives_verified'], 'native files:', len(report['native_files']),
          'legal entries:', report['legal_manifest_entries_checked'])
    for failure in report['failures']:
        print(failure)
    raise SystemExit(bool(report['failures']))


if __name__ == '__main__':
    main()
