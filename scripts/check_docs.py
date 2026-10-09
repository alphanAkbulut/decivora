#!/usr/bin/env python3
"""Documentation integrity only; does not test the planned product."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
markdown = sorted(ROOT.rglob('*.md'))
links = 0
for path in markdown:
    text = path.read_text(encoding='utf-8')
    if text.count('```') % 2:
        errors.append(f'{path.relative_to(ROOT)}: unbalanced code fence')
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' in target or target.startswith(('#', 'mailto:')):
            continue
        target = target.split('#')[0]
        links += 1
        if target and not (path.parent / target).exists():
            errors.append(f'{path.relative_to(ROOT)}: missing link {target}')

scope = (ROOT / 'docs/product/full-scope.md').read_text()
backlog = (ROOT / 'docs/delivery/backlog.md').read_text()
scope_ids = set(re.findall(r'^\| ([A-Z]+-\d+) \|', scope, re.M))
for scope_id in scope_ids:
    if scope_id not in backlog:
        errors.append(f'scope without task mapping: {scope_id}')
task_ids = re.findall(r'^## (T\d+) —', backlog, re.M)
if len(task_ids) != 30 or len(set(task_ids)) != 30:
    errors.append('expected 30 distinct tasks')
for ac in range(1, 15):
    if f'AC-{ac:02}' not in (ROOT / 'docs/product/mvp.md').read_text():
        errors.append(f'missing AC-{ac:02}')
for path in ROOT.rglob('*.json'):
    json.loads(path.read_text())
fixture = json.loads((ROOT / 'examples/impact-scenario.json').read_text())
if not fixture['synthetic'] or fixture['implemented']:
    errors.append('fixture must be clearly synthetic and unimplemented')
for path in ROOT.rglob('*'):
    if path.is_file() and '.git' not in path.parts:
        if path.suffix in {'.db', '.sqlite'} or path.name.startswith('.env'):
            errors.append(f'runtime data in deliverable: {path}')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'PASS: {len(markdown)} Markdown files, {links} local links, '
      f'{len(scope_ids)} scope IDs, {len(task_ids)} tasks, 14 MVP criteria; JSON valid.')
print('Not tested: application runtime, adapters, model quality, Mermaid rendering.')
