#!/usr/bin/env python3
"""Read-only pilot report: no credentials, network, re-dispatch, or source upload."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from packages.capture.openai_transport import micro_cost, PRICE_REVISION


def build(folder):
    folder = Path(folder)
    packet = json.loads((folder / 'prepared.json').read_text())
    records = []
    for job in packet['jobs']:
        path = folder / (job['id'] + '.result.json')
        if not path.exists():
            raise ValueError('Incomplete pilot: not all private receipts exist.')
        receipt = json.loads(path.read_text())
        result = receipt['result']
        usage = result.get('usage')
        if type(usage) is not dict:
            raise ValueError('Usage unavailable; do not publish a zero-cost result.')
        details = usage['input_tokens_details']
        cost = micro_cost(job['model'], usage['input_tokens'], usage['output_tokens'],
                          cached_tokens=details['cached_tokens'], cache_write_tokens=details['cache_write_tokens'])
        raw = json.loads(result['raw_output'])
        if (receipt['job'] != job['id'] or receipt['model'] != job['model'] or
                raw['source_id'] != job['source_id'] or raw['context_sha256'] != job['context_sha256']):
            raise ValueError('Receipt identity does not match prepared job.')
        db_path = folder / job['database']
        with sqlite3.connect(db_path.resolve().as_uri() + '?mode=ro', uri=True) as db:
            canonical = db.execute('SELECT id,version FROM records').fetchall()
        seed_unchanged = canonical == [(job['task_id'], 1)]
        records.append(dict(job=job['id'], model=job['model'], status=result['status'],
            coverage=raw['coverage'], candidate_types=[c['type'] for c in raw['candidates']],
            status_stages=[s['stage'] for s in raw['status_changes']],
            answer_proposals=len(raw['answer_proposals']), relation_proposals=len(raw['relation_proposals']),
            input_tokens=usage['input_tokens'], output_tokens=usage['output_tokens'],
            cached_tokens=details['cached_tokens'], cache_write_tokens=details['cache_write_tokens'],
            reasoning_tokens=usage['output_tokens_details']['reasoning_tokens'],
            corrected_estimated_cost_microusd=cost,
            raw_output_sha256=hashlib.sha256(result['raw_output'].encode()).hexdigest(),
            private_receipt_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            canonical_seed_unchanged=seed_unchanged,
            independent_gold_review=False))
    with sqlite3.connect((folder / 'shared-budget.sqlite').resolve().as_uri() + '?mode=ro', uri=True) as db:
        rows = db.execute('SELECT state,attempts,actual FROM dispatch').fetchall()
    corrected = sum(r['corrected_estimated_cost_microusd'] for r in records)
    return dict(format='decivora-openai-pilot-result-1', date='2026-10-19',
        model_generation_calls=len(records), allocated_http_attempts=sum(r[1] for r in rows),
        approved_max_http_attempts=packet['manifest']['max_http_attempts'],
        approved_max_cost_microusd=packet['manifest']['max_cost_microusd'],
        all_source_schema_contracts_passed=all(r['status'] == 'Ready for review' for r in records),
        real_user_transcripts_sent=False, auto_applied_proposals=False,
        seed_records_unchanged=all(r['canonical_seed_unchanged'] for r in records),
        input_tokens=sum(r['input_tokens'] for r in records),
        output_tokens=sum(r['output_tokens'] for r in records),
        total_tokens=sum(r['input_tokens'] + r['output_tokens'] for r in records),
        cache_write_tokens=sum(r['cache_write_tokens'] for r in records),
        original_ledger_price_revision=packet['manifest']['price_revision'],
        original_ledger_estimate_microusd=sum(r[2] for r in rows),
        corrected_price_revision=PRICE_REVISION,
        corrected_estimated_cost_microusd=corrected,
        within_approved_cost=corrected <= packet['manifest']['max_cost_microusd'],
        final_invoice_verified=False, native_capture_verified=False, mvp_acceptance=False,
        expectation_status='AI_authored_not_independent_gold',
        scope='Five short English synthetic sources; no generalized accuracy or savings claim.',
        records=records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.folder), ensure_ascii=False, indent=2))
