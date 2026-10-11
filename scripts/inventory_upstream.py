#!/usr/bin/env python3
"""Read-only structural inventory of a supplied source snapshot; executes no upstream code."""
import argparse
import collections
import csv
import hashlib
import json
import pathlib
import re

EXTENSIONS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.mts', '.cts', '.py', '.sh', '.ps1', '.rs', '.css', '.html'}
EXCLUDED = {'.git', '.wrongstack', '.project', 'node_modules'}
IMPORT = re.compile(r'(?:\bfrom\s*|\bimport\s*\(|\brequire\s*\(|\bimport\s*)[\"\']([^\"\']+)[\"\']')


def inventory(root, output, revision):
    manifests = [root / 'package.json', *sorted(root.glob('packages/*/package.json')),
                 *sorted(root.glob('apps/*/package.json')), root / 'website/package.json']
    manifests = [p for p in manifests if p.is_file()]
    owners = {p.parent: json.loads(p.read_text()) for p in manifests}
    names = {j['name']: j for j in owners.values()}
    by_owner = collections.defaultdict(list)
    top = collections.defaultdict(collections.Counter)
    digest = hashlib.sha256()
    errors = []
    source_files = []
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.is_symlink():
            continue
        relative = p.relative_to(root)
        if EXCLUDED.intersection(relative.parts):
            continue
        if p.suffix not in EXTENSIONS:
            continue
        try:
            raw = p.read_bytes()
            content = raw.decode('utf-8')
        except (OSError, UnicodeError) as error:
            errors.append({'path': relative.as_posix(), 'error': str(error)})
            continue
        test = any(x in relative.parts for x in ('tests', 'test', 'e2e', 'fixtures')) or bool(re.search(r'\.(test|spec)\.', p.name))
        declaration = p.name.endswith(('.d.ts', '.d.mts', '.d.cts'))
        imports = sorted(set(IMPORT.findall(content)))
        line_count = len(content.splitlines())
        file_hash = hashlib.sha256(raw).hexdigest()
        digest.update(f'{relative.as_posix()}\0{file_hash}\n'.encode())
        owner = next((q for q in sorted(owners, key=lambda x: len(x.parts), reverse=True)
                      if q == p.parent or q in p.parents), root)
        row = {'path': relative.as_posix(), 'sha256': file_hash, 'lines': line_count,
               'kind': 'declaration' if declaration else 'test_or_fixture' if test else 'source',
               'owner': owners[owner]['name'], 'imports': imports}
        source_files.append(row)
        by_owner[owner].append(row)
        area = '/'.join(relative.parts[:2]) if relative.parts[0] in ('apps', 'packages') else relative.parts[0]
        top[area]['files'] += 1
        top[area]['lines'] += line_count

    def closure(name):
        seen = set()
        todo = [name]
        while todo:
            current = todo.pop()
            for field in ('dependencies', 'optionalDependencies'):
                for dependency in names[current].get(field, {}):
                    if dependency in names and dependency not in seen and dependency != name:
                        seen.add(dependency)
                        todo.append(dependency)
        return sorted(seen)

    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for owner, manifest in sorted(owners.items()):
        files = by_owner[owner]
        direct = {**manifest.get('dependencies', {}), **manifest.get('optionalDependencies', {})}
        rows.append({'directory': owner.relative_to(root).as_posix(), 'name': manifest['name'],
                     'declared_version': manifest.get('version', ''), 'declared_license': manifest.get('license', ''),
                     'source_files': sum(f['kind'] == 'source' for f in files),
                     'test_fixture_files': sum(f['kind'] == 'test_or_fixture' for f in files),
                     'declaration_files': sum(f['kind'] == 'declaration' for f in files),
                     'all_lines': sum(f['lines'] for f in files),
                     'internal_dependency_closure': ';'.join(closure(manifest['name'])),
                     'direct_dependencies': ';'.join(f'{k}={v}' for k, v in sorted(direct.items()))})
    with (output / 'upstream-component-inventory.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {'revision': revision, 'method': 'UTF-8 file read, SHA-256 and regex import index; not AST/type/runtime validation',
               'excluded_directory_names': sorted(EXCLUDED), 'extensions': sorted(EXTENSIONS),
               'workspace_manifest_count': len(rows), 'code_file_count': len(source_files),
               'code_lines_including_tests_and_declarations': sum(f['lines'] for f in source_files),
               'kinds': dict(collections.Counter(f['kind'] for f in source_files)),
               'sorted_path_and_file_hash_digest_sha256': digest.hexdigest(),
               'read_errors': errors, 'top_level_areas': dict(sorted(top.items()))}
    (output / 'upstream-inventory-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    # Detailed local index stays outside the product repository: no source text is copied.
    (output / 'upstream-file-index.json').write_text(json.dumps(source_files, indent=2) + '\n')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=pathlib.Path)
    parser.add_argument('output', type=pathlib.Path)
    parser.add_argument('--revision', required=True)
    args = parser.parse_args()
    print(json.dumps(inventory(args.snapshot.resolve(), args.output.resolve(), args.revision), indent=2))
