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
# Only canonical definition rows count; repeated references are expected.
subtask_definitions = {}
for line_number, line in enumerate(backlog.splitlines(), 1):
    match = re.match(r'^\| (T\d+[a-z]+) / ', line)
    if match:
        subtask_definitions.setdefault(match.group(1), []).append(line_number)
for subtask_id, line_numbers in subtask_definitions.items():
    if len(line_numbers) > 1:
        errors.append(f'duplicate subtask definition {subtask_id}: lines {line_numbers}')

task_ids = re.findall(r'^## (T\d+) —', backlog, re.M)
if len(task_ids) != 30 or len(set(task_ids)) != 30:
    errors.append('expected 30 distinct tasks')
for ac in range(1, 15):
    if f'AC-{ac:02}' not in (ROOT / 'docs/product/mvp.md').read_text():
        errors.append(f'missing AC-{ac:02}')

# Phase view mirrors canonical main-task metadata; it is not a second backlog.
phase_text = (ROOT / 'docs/delivery/phase-tracker.md').read_text()
phase_rows = re.findall(
    r'^\| (T\d+) \| (P\d[ab]?) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$',
    phase_text, re.M)
phase_rows = [tuple(value.strip() for value in row) for row in phase_rows]
canonical_rows = []
task_headers = list(re.finditer(r'^## (T\d+) — ([^\n]+)\n', backlog, re.M))
for index, header in enumerate(task_headers):
    end = task_headers[index + 1].start() if index + 1 < len(task_headers) else len(backlog)
    section = backlog[header.end():end]
    metadata = re.search(
        r'- \*\*Durum / faz:\*\* ([^/.\n]+) / ([^.]+)\. \*\*Bağımlılık:\*\* ([^.]+)\.',
        section)
    if metadata is None:
        errors.append(f'missing canonical task metadata: {header.group(1)}')
        continue
    state, phase, dependency = (value.strip() for value in metadata.groups())
    canonical_rows.append((header.group(1), phase, state, header.group(2), dependency))
if phase_rows != canonical_rows:
    errors.append('phase tracker differs from canonical task IDs/phase/status/title/dependencies')

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

# Current focus and target-observation contracts; documentation references only.
gap_doc = (ROOT / 'docs/product/intent-to-reality-gap.md').read_text()
gap_ids = set(re.findall(r'^\| (GAP-\d+) \|', gap_doc, re.M))
if gap_ids != {f'GAP-{i:02}' for i in range(1, 11)}:
    errors.append('expected GAP-01–10 planned contracts')
for path in markdown:
    refs = set(re.findall(r'\bGAP-\d+\b', path.read_text()))
    if refs - gap_ids:
        errors.append(f'{path.relative_to(ROOT)}: unknown GAP refs {sorted(refs-gap_ids)}')
gap_fixture = json.loads((ROOT / 'examples/intent-reality-scenario.json').read_text())
if gap_fixture.get('synthetic') is not True or gap_fixture.get('implemented') is not False:
    errors.append('GAP fixture must be synthetic and unimplemented')
if gap_fixture.get('result_status') != 'not_run':
    errors.append('GAP oracle is not a runtime result')
fixture_ids = [row['id'] for row in gap_fixture['scenarios']]
if len(fixture_ids) != 10 or set(fixture_ids) != gap_ids:
    errors.append('GAP fixture scenario coverage mismatch')

# Inventory must cover every Mermaid-bearing document once.
diagram_counts = {
    path.relative_to(ROOT).as_posix(): sum(line == '```mermaid' for line in path.read_text().splitlines())
    for path in markdown
}
diagram_counts = {path: count for path, count in diagram_counts.items() if count}
inventory_doc = (ROOT / 'docs/quality/diagram-review.md').read_text()
inventory = inventory_doc.split('<!-- diagram-inventory:start -->')[1].split('<!-- diagram-inventory:end -->')[0]
inventory_counts = {}
for target, count in re.findall(r'^\| \[.*?\]\(([^)]+)\) \| (\d+) \|$', inventory, re.M):
    resolved = ((ROOT / 'docs/quality') / target).resolve().relative_to(ROOT.resolve()).as_posix()
    if resolved in inventory_counts:
        errors.append(f'duplicate diagram inventory: {resolved}')
    inventory_counts[resolved] = int(count)
if inventory_counts != diagram_counts:
    errors.append('diagram inventory differs from Mermaid source counts')

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
print(f'Phase tracker: {len(phase_rows)} main-task rows matched canonical backlog metadata.')
print(f'Traceability: {len(source_stages)} source stages, {len(features)} features, '
      f'{len(engines)} engines, {len(scenarios)} planned verification scenarios.')
print(f'Collaboration/data: {len(collaboration_scenarios)} additional planned scenarios; not runtime tested.')
print(f'Connection/token/graph/context: {contract_count} additional planned contract scenarios.')
print(f'Target application: {len(gap_ids)} planned GAP scenarios; oracle is not_run.')
print(f'Diagrams: {sum(diagram_counts.values())} source blocks in {len(diagram_counts)} documents; inventory matched.')
print('Not tested: application runtime, adapters, model quality, Mermaid rendering.')
