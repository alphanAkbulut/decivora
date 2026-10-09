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

# Referential coverage, not proof that natural-language requirements are complete.
feature_text = (ROOT / 'docs/product/feature-catalog.md').read_text()
engine_text = (ROOT / 'docs/architecture/engines.md').read_text()
evolution = (ROOT / 'docs/discovery/evolution.md').read_text()
verification = (ROOT / 'docs/quality/verification.md').read_text()
traceability = (ROOT / 'docs/quality/traceability.md').read_text()
features = set(re.findall(r'^\| (F\d+) ', feature_text, re.M))
engines = set(re.findall(r'^\| (ENG-\d+) ', engine_text, re.M))
source_stages = set(re.findall(r'^\| (E\d+) \|', evolution, re.M))
scenarios = set(re.findall(r'^\| (V\d+) \|', verification, re.M))
for label, actual, expected in [
    ('features', features, {f'F{i:02}' for i in range(1, 18)}),
    ('engines', engines, {f'ENG-{i:02}' for i in range(1, 11)}),
    ('source stages', source_stages, {f'E{i:02}' for i in range(1, 15)}),
    ('verification scenarios', scenarios, {f'V{i:02}' for i in range(1, 29)}),
]:
    if actual != expected:
        errors.append(f'{label} mismatch: missing {sorted(expected-actual)}, extra {sorted(actual-expected)}')
trace_ids = []
covered_features, covered_engines, covered_stages = set(), set(), set()
for line in traceability.splitlines():
    if not re.match(r'^\| [A-Z]+-\d+ \|', line):
        continue
    fields = [field.strip() for field in line.strip('|').split('|')]
    if len(fields) != 6:
        errors.append(f'invalid traceability row: {line}')
        continue
    scope_id, source, feature, engine, task, check = fields
    trace_ids.append(scope_id)
    for label, cell, pattern, allowed in [
        ('source', source, r'\bE\d+\b', source_stages),
        ('feature', feature, r'\bF\d+\b', features),
        ('engine', engine, r'\bENG-\d+\b', engines),
        ('task', task, r'\bT\d+\b', set(task_ids)),
        ('scenario', check, r'\bV\d+\b', scenarios),
    ]:
        refs = set(re.findall(pattern, cell))
        if refs - allowed:
            errors.append(f'{scope_id}: unknown {label} refs {sorted(refs-allowed)}')
        if label in {'source', 'feature', 'task'} and not refs:
            errors.append(f'{scope_id}: missing {label} mapping')
        if label == 'source': covered_stages.update(refs)
        if label == 'feature': covered_features.update(refs)
        if label == 'engine': covered_engines.update(refs)
    if not check:
        errors.append(f'{scope_id}: missing acceptance evidence plan')
if set(trace_ids) != scope_ids or len(trace_ids) != len(scope_ids):
    errors.append('traceability must map each scope ID exactly once')
for label, covered, defined in [
    ('feature', covered_features, features),
    ('engine', covered_engines, engines),
    ('source stage', covered_stages, source_stages),
]:
    if covered != defined:
        errors.append(f'unmapped {label}: {sorted(defined-covered)}')

# Feature-contract scenario references; no runtime behavior is executed here.
contract_docs = {
    'CON': 'docs/architecture/connection-and-context.md',
    'TOK': 'docs/architecture/routing-token-economy.md',
    'GUX': 'docs/product/graph-experience.md',
    'CTX': 'docs/product/task-context-and-acceptance.md',
}
contract_count = 0
for prefix, relative in contract_docs.items():
    expected_count = 6 if prefix == 'CTX' else 8
    actual = set(re.findall(r'^\| (' + prefix + r'-\d+) \|', (ROOT / relative).read_text(), re.M))
    expected = {f'{prefix}-{i:02}' for i in range(1, expected_count + 1)}
    contract_count += len(actual)
    if actual != expected:
        errors.append(f'{prefix}: invalid contract scenario set')
    for path in markdown:
        refs = set(re.findall(r'\b' + prefix + r'-\d+\b', path.read_text()))
        if refs - actual:
            errors.append(f'{path.relative_to(ROOT)}: unknown contract refs {sorted(refs-actual)}')

for path in ROOT.rglob('*.json'):
    json.loads(path.read_text())
collaboration_plan = (ROOT / 'docs/quality/collaboration-validation.md').read_text()
collaboration_scenarios = set(re.findall(r'^\| (MU\d+) \|', collaboration_plan, re.M))
if collaboration_scenarios != {f'MU{i:02}' for i in range(1, 19)}:
    errors.append('expected MU01-MU18 collaboration/data scenarios')
for path in markdown:
    refs = set(re.findall(r'\bMU\d+\b', path.read_text()))
    if refs - collaboration_scenarios:
        errors.append(f'{path.relative_to(ROOT)}: unknown MU scenario {sorted(refs-collaboration_scenarios)}')
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
print(f'Traceability: {len(source_stages)} source stages, {len(features)} features, '
      f'{len(engines)} engines, {len(scenarios)} planned verification scenarios.')
print(f'Collaboration/data: {len(collaboration_scenarios)} additional planned scenarios; not runtime tested.')
print(f'Connection/token/graph/context: {contract_count} additional planned contract scenarios.')
print('Not tested: application runtime, adapters, model quality, Mermaid rendering.')
