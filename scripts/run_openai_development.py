#!/usr/bin/env python3
"""Bounded synthetic development batches under the explicit shared USD3 approval.

No source discovery, real transcripts, UI activation, retries, or automatic apply.
First-pilot usage is carried once into the same durable root for all new batches.
"""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT))
from report_openai_pilot import build
from run_openai_pilot import prepare, run, private_json, KEY
from packages.capture.openai_transport import PRICE_REVISION, fingerprint

DATA = ROOT.parent / 'decivora-local-data'
DEVELOPMENT = DATA / 'openai-development-001'
CASES = [
    ('done-en', 'I finished EXISTING_TASK. Tests have not been run yet.', 'completion_claim_Done_not_verified'),
    ('done-tr', 'EXISTING_TASK görevini bitirdim. Testleri henüz çalıştırmadım.', 'completion_claim_Done_not_verified'),
    ('future-en', 'Once EXISTING_TASK is finished, we can discuss deployment. I have not started it.', 'no_status_proposal'),
    ('negation-tr', 'EXISTING_TASK görevini bitirmedim; henüz başlamadım.', 'no_status_proposal'),
]


def root_policy(folder=DEVELOPMENT, history_folder=DATA / 'openai-pilot-001'):
    folder = Path(folder)
    path = folder / 'approved-root-policy.json'
    if path.exists():
        return json.loads(path.read_text())
    # Read-only reconstruction from original private receipts, not an editable zero baseline.
    historical = build(history_folder)
    if (historical['model_generation_calls'] != 10 or historical['allocated_http_attempts'] != 20 or
            not historical['within_approved_cost'] or not historical['seed_records_unchanged']):
        raise ValueError('First-pilot accounting requires review before extending the root budget.')
    policy = dict(approval_ref='owner-chat-2026-10-19-explicit-usd3-100-generation-200-http',
                  price_revision=PRICE_REVISION, expires_at=int(time.time()) + 86400,
                  max_http_attempts=200, max_cost_microusd=3000000,
                  max_input_tokens=10000, max_output_tokens=2000,
                  budget_scope='decivora-development-2026-10-19-usd3',
                  prior_usage=dict(dispatches=10, http_attempts=20,
                                   cost_microusd=historical['corrected_estimated_cost_microusd'],
                                   evidence_sha256=fingerprint(historical)))
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    private_json(path, policy)
    return policy


def prepare_claim_batch(folder=DEVELOPMENT, history_folder=DATA / 'openai-pilot-001'):
    policy = root_policy(folder, history_folder)
    return prepare(Path(folder) / 'claims-002', cases=CASES, manifest_overrides=policy)


def run_claim_batch(folder=DEVELOPMENT, key_file=KEY, post=None):
    folder = Path(folder)
    return run(folder / 'claims-002', key_file, post, ledger_path=folder / 'shared-budget.sqlite')


def prepare_original_claim_batch(folder=DEVELOPMENT, history_folder=DATA / 'openai-pilot-001'):
    policy = root_policy(folder, history_folder)
    cases = [('original-claim', 'The task EXISTING_TASK is done, but I have not run any tests.',
              'original_source_completion_claim_Done_not_verified')]
    return prepare(Path(folder) / 'original-claim-003', cases=cases, manifest_overrides=policy)


def run_original_claim_batch(folder=DEVELOPMENT, key_file=KEY, post=None):
    folder = Path(folder)
    return run(folder / 'original-claim-003', key_file, post, ledger_path=folder / 'shared-budget.sqlite')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare', action='store_true')
    group.add_argument('--run', action='store_true')
    parser.add_argument('--batch', choices=('claims', 'original-claim'), default='claims')
    args = parser.parse_args()
    if args.prepare:
        packet = prepare_claim_batch() if args.batch == 'claims' else prepare_original_claim_batch()
        print(json.dumps(dict(prepared_jobs=len(packet['jobs']), network_calls=0,
                              max_generation_calls_total=100, max_http_attempts_total=200,
                              max_cost_usd_total=3, first_pilot_included=True)))
    else:
        result = run_claim_batch() if args.batch == 'claims' else run_original_claim_batch()
        print(json.dumps(dict(batch_jobs=len(result['outcomes']), shared_budget=result['shared_budget'],
                              canonical_auto_apply=False, mvp_acceptance=False)))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('Development batch stopped; inspect private receipts. No automatic retry.', file=sys.stderr)
        raise SystemExit(1)
