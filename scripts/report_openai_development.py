#!/usr/bin/env python3
"""Read-only shared development accounting; never reads keys or sends requests."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from packages.capture.openai_transport import micro_cost


def build(folder):
    folder = Path(folder)
    policy = json.loads((folder / 'approved-root-policy.json').read_text())
    records = []
    for name in ('claims-002', 'original-claim-003'):
        packet = json.loads((folder / name / 'prepared.json').read_text())
        for job in packet['jobs']:
            path = folder / name / (job['id'] + '.result.json')
            receipt = json.loads(path.read_text())
            result = receipt['result']
            raw = json.loads(result['raw_output'])
            usage = result['usage']
            details = usage['input_tokens_details']
            cost = micro_cost(job['model'], usage['input_tokens'], usage['output_tokens'],
                              cached_tokens=details['cached_tokens'], cache_write_tokens=details['cache_write_tokens'])
            if raw['source_id'] != job['source_id'] or raw['context_sha256'] != job['context_sha256']:
                raise ValueError('Receipt/source/context mismatch.')
            with sqlite3.connect((folder / name / job['database']).resolve().as_uri() + '?mode=ro', uri=True) as db:
                seed_unchanged = db.execute('SELECT id,version FROM records').fetchall() == [(job['task_id'], 1)]
            records.append(dict(batch=name, job=job['id'], model=job['model'], status=result['status'],
                                stages=[s['stage'] for s in raw['status_changes']],
                                candidate_count=len(raw['candidates']), coverage=raw['coverage'],
                                source_id=raw['source_id'], context_sha256=raw['context_sha256'],
                                request_payload_sha256=job['payload_sha256'],
                                usage=usage, estimated_cost_microusd=cost,
                                seed_unchanged=seed_unchanged,
                                raw_output_sha256=hashlib.sha256(result['raw_output'].encode()).hexdigest(),
                                private_receipt_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    with sqlite3.connect((folder / 'shared-budget.sqlite').resolve().as_uri() + '?mode=ro', uri=True) as db:
        rows = db.execute('SELECT state,attempts,actual FROM dispatch').fetchall()
    if len(rows) != len(records) or any(r[0] != 'settled' or type(r[2]) is not int for r in rows):
        raise ValueError('Incomplete/unknown ledger; no zero-cost fallback.')
    batch_cost = sum(r['estimated_cost_microusd'] for r in records)
    if batch_cost != sum(r[2] for r in rows):
        raise ValueError('Saved provider usage and shared monetary ledger disagree.')
    total_cost = policy['prior_usage']['cost_microusd'] + batch_cost
    paired = []
    history = folder.parent / 'openai-pilot-001'
    if (history / 'prepared.json').exists():
        original = json.loads((history / 'prepared.json').read_text())
        for record in records:
            if record['batch'] != 'original-claim-003':
                continue
            old = next(j for j in original['jobs'] if j['id'] == 'claim-' + record['model'])
            receipt = json.loads((history / (old['id'] + '.result.json')).read_text())
            before = json.loads(receipt['result']['raw_output'])
            paired.append(dict(model=record['model'], same_source=old['source_id'] == record['source_id'],
                               same_context=old['context_sha256'] == record['context_sha256'],
                               different_payload=old['payload_sha256'] != record['request_payload_sha256'],
                               before_stages=[s['stage'] for s in before['status_changes']],
                               after_stages=record['stages']))
    return dict(format='decivora-openai-development-result-1',
                scope=policy['budget_scope'], approval_ref=policy['approval_ref'],
                first_pilot_included=True, prior_usage=policy['prior_usage'],
                batch_model_calls=len(records), batch_http_attempts=sum(r[1] for r in rows),
                total_model_calls=policy['prior_usage']['dispatches'] + len(records),
                total_http_attempts=policy['prior_usage']['http_attempts'] + sum(r[1] for r in rows),
                estimated_total_microusd=total_cost, max_cost_microusd=policy['max_cost_microusd'],
                remaining_cost_microusd=policy['max_cost_microusd'] - total_cost,
                max_model_calls=100, max_http_attempts=policy['max_http_attempts'],
                frozen=False, final_invoice_verified=False, independent_gold=False,
                canonical_auto_apply=False, native_capture_verified=False, mvp_acceptance=False,
                paired_original_comparisons=paired, records=records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.folder), ensure_ascii=False, indent=2))
