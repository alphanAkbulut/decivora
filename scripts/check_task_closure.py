"""Validate planning ownership/closure consistency; not product acceptance tests."""
import json
from pathlib import Path
import re

from project_progress import build

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT, manifest=None):
    manifest = json.loads((root / 'docs/delivery/task-closure.json').read_text()) if manifest is None else manifest
    data = build(root)
    tasks = {t['id']: t for t in data['tasks']}
    rows = {s['id']: s for t in data['tasks'] for s in t['subtasks']}
    for line in (root / 'docs/delivery/team-data-plan.md').read_text().splitlines():
        match = re.match(r'^\| (T\d+[a-z]+) / ([^|]+) \|', line)
        if match and match[1] not in rows:
            rows[match[1]] = dict(status='UNSPECIFIED', dependencies=match[2])
    if manifest['format'] != 'decivora-task-closure-1' or set(manifest['tasks']) != set(tasks) or set(manifest['subtasks']) != set(rows):
        raise ValueError('Closure manifest must cover exact canonical task/subtask inventory.')
    if manifest['mvp_criteria'] != [f'AC-{i:02}' for i in range(1, 15)]:
        raise ValueError('MVP criteria must be preserved.')
    graph = {tid: list(t['dependencies']) for tid, t in tasks.items()}
    for sid, row in manifest['subtasks'].items():
        parent = re.match(r'T\d+', sid)[0]
        classification = row['classification']
        if row['parent'] != parent or row['owner'] not in tasks or row['first_use_gate'] not in tasks or not row['reason'].strip():
            raise ValueError('Missing or invalid subtask owner/gate/reason: ' + sid)
        if classification not in ('task_local', 'integration', 'release', 'future_proposed'):
            raise ValueError('Unknown closure classification: ' + sid)
        if row['required_for_parent_closure'] != (classification == 'task_local'):
            raise ValueError('Parent closure flag disagrees with classification: ' + sid)
        if row['status'] != rows[sid]['status']:
            raise ValueError('Subtask status changed; review manifest: ' + sid)
        if classification == 'future_proposed' and row['status'] != 'PROPOSED':
            raise ValueError('Accepted scope cannot silently become proposed: ' + sid)
        deps = re.findall(r'T\d+[a-z]*', rows[sid]['dependencies'])
        if deps != row['dependencies']:
            raise ValueError('Subtask dependencies changed: ' + sid)
        # Exact parent after slash may denote containment, not a prerequisite.
        graph[sid] = [d for d in deps if d != parent]
        # A later task's child cannot be assumed available before that task's
        # planned start prerequisites. Model those prerequisites conservatively.
        owner_number = int(row['owner'][1:])
        for dep in deps:
            dep_parent = re.match(r'T\d+', dep)[0]
            if int(dep_parent[1:]) > owner_number:
                graph[sid].extend(tasks[dep_parent]['dependencies'])
        if classification == 'task_local':
            graph[parent].append(sid)
        elif classification in ('integration', 'release'):
            graph[row['owner']].append(sid)
    for tid, task in tasks.items():
        record = manifest['tasks'][tid]
        if record['core_acceptance'] != task['details']['Kabul']:
            raise ValueError('Core acceptance changed without manifest review: ' + tid)
        if task['status'] == 'DONE':
            if record['core_verified'] is not True or not record['evidence']:
                raise ValueError('Done needs scoped evidence: ' + tid)
            for name in record['evidence']:
                path = (root / name).resolve()
                if not path.is_relative_to(root.resolve()) or not path.is_file():
                    raise ValueError('Missing/outside evidence path: ' + tid)
            for sid, row in manifest['subtasks'].items():
                required = row['parent'] == tid and row['required_for_parent_closure']
                required |= row['owner'] == tid and row['classification'] in ('integration', 'release')
                if required and row['status'] != 'DONE':
                    raise ValueError('Done has unfinished required work: ' + sid)
    visiting, visited = set(), set()
    def walk(node):
        if node in visiting:
            raise ValueError('Closure dependency cycle: ' + node)
        if node in visited:
            return
        visiting.add(node)
        for dep in graph.get(node, []):
            if dep not in graph:
                raise ValueError('Unresolved task dependency: ' + dep)
            walk(dep)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        walk(node)
    return dict(main_tasks=len(tasks), subtasks=len(rows), dependency_cycles=0,
                scope='planning consistency only; runtime/first-use/release evidence still required')


if __name__ == '__main__':
    print('PASS:', json.dumps(validate(), ensure_ascii=False))
