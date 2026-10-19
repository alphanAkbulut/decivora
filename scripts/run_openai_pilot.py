#!/usr/bin/env python3
"""Prepare/run the owner-approved synthetic pilot; never auto-accept model proposals.

Prepare is offline. --run requires a prepared exact manifest, private credential,
source/context-specific grants, shared durable budget, and unexpired approval.
This command uses separate pilot databases, never LOCAL or TEST user data.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from packages.capture.conversations import ConversationService
from packages.capture.dialogue_review import DialogueReviewService
from packages.capture.openai_transport import PilotTransport, PRICE_REVISION, fingerprint, read_key
from packages.capture.responses_extractor import ResponsesExtractor, request_payload
from packages.domain.questions import QuestionService
from packages.storage.project_store import canonical
from packages.storage.workspace import Workspace

DEFAULT = ROOT.parent / 'decivora-local-data' / 'openai-pilot-001'
KEY = ROOT.parent / 'decivora-local-data' / 'secrets' / 'openai-api-key'
CASES = [
    ('task', 'Please add a backup test.', 'new_Task_candidate'),
    ('decision', 'We chose SQLite as the primary store.', 'new_Decision_candidate'),
    ('status', 'I started the task EXISTING_TASK.', 'existing_task_In_Progress_proposal'),
    ('claim', 'The task EXISTING_TASK is done, but I have not run any tests.', 'completion_claim_without_verification'),
    ('answer', 'For Q_STORE revision 1, my answer is SQLite, option sqlite.', 'source_bound_Q_STORE_answer_proposal'),
]


def private_json(path, value):
    encoded = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())


def prepare(folder=DEFAULT, *, cases=None, manifest_overrides=None):
    folder = Path(folder)
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    packet = folder / 'prepared.json'
    if packet.exists():
        # An existing manifest/expiry is immutable; no fresh budget on restart.
        return json.loads(packet.read_text())
    jobs = []
    for case_id, text, expectation in (CASES if cases is None else cases):
        for model in ('gpt-6-luna', 'gpt-6.1-sol'):
            job_id = case_id + '-' + model
            db = folder / (job_id + '.sqlite')
            if db.exists():
                raise ValueError('Partial pilot preparation exists; review before reuse.')
            with Workspace(db, 'pilot', owner='pilot_owner') as core:
                a = core.authority
                a.replace_grant(a.issue_scope('pilot_owner'), 'pilot_owner', kind='human',
                                readable=frozenset({'synthetic'}), writable=frozenset({'synthetic'}),
                                active=True, base_revision=1)
                owner = a.issue_scope('pilot_owner')
                core.create_project(owner, 'synthetic', 'Explicit synthetic pilot')
                plan = core.plan(owner, 'synthetic', 'seed', [dict(op='create', id='task',
                                 body=dict(type='Task', title='Backup integrity test', description='Synthetic existing task'))])
                task = core.apply(owner, plan, core.approve(owner, plan))['temp_ids']['task']
                QuestionService(core).present(owner, 'synthetic', question='Q_STORE', base_revision=0,
                    text='Storage?', options=[dict(id='sqlite', label='SQLite'), dict(id='files', label='Files')], reason='')
                sources = ConversationService(core)
                source = sources.ingest(owner, 'synthetic', text=text.replace('EXISTING_TASK', task))
                prepared = DialogueReviewService(core).prepare(owner, 'synthetic', source_id=source['id'])
                payload = request_payload(source, model=model, max_output_tokens=2000,
                                          dialogue_request=prepared['request'])
                jobs.append(dict(id=job_id, database=db.name, model=model, source_id=source['id'],
                                 task_id=task, payload_sha256=fingerprint(payload),
                                 context_sha256=prepared['context_sha256'],
                                 authored_expectation=expectation, expectation_status='AI_authored_not_human_gold'))
    manifest = dict(approval_ref='owner-chat-2026-10-19-synthetic-20-http-usd1',
                    price_revision=PRICE_REVISION, expires_at=int(time.time()) + 86400,
                    max_http_attempts=20, max_cost_microusd=1000000,
                    max_input_tokens=10000, max_output_tokens=2000,
                    payloads=[job['payload_sha256'] for job in jobs])
    if manifest_overrides is not None:
        if 'payloads' in manifest_overrides:
            raise ValueError('Caller cannot replace exact prepared payload identities.')
        manifest.update(manifest_overrides)
    result = dict(format='decivora-openai-pilot-1', manifest=manifest, jobs=jobs,
                  scope='synthetic_only_no_user_transcripts', model_dispatches=0,
                  max_generation_calls=len(jobs), max_token_count_calls=len(jobs),
                  automatic_retry=False, auto_accept=False)
    private_json(packet, result)
    return result


def run(folder=DEFAULT, key_file=KEY, post=None, *, ledger_path=None):
    folder = Path(folder)
    packet = json.loads((folder / 'prepared.json').read_text())
    read_key(key_file)  # Fail locally before creating a grant or recording an analysis attempt.
    manifest = packet['manifest']
    transport = PilotTransport(folder / 'shared-budget.sqlite' if ledger_path is None else ledger_path, manifest=manifest,
                               key_file=key_file, post=post)
    if transport.snapshot()['frozen']:
        return dict(outcomes=[], shared_budget=transport.snapshot(),
                    native_capture='not_tested', mvp_acceptance=False,
                    stopped='previous_uncertain_or_overrun_dispatch_requires_review')
    outcomes = []
    for job in packet['jobs']:
        # Completed reports are read, never regenerated. Unknown/crash jobs freeze in the ledger.
        receipt = folder / (job['id'] + '.result.json')
        if receipt.exists():
            existing = json.loads(receipt.read_text())
            outcomes.append(existing)
            if existing['result']['status'] != 'Ready for review':
                break
            continue
        with Workspace(folder / job['database'], 'pilot') as core:
            owner = core.authority.issue_scope('pilot_owner')
            sources = ConversationService(core)
            source = sources._source('synthetic', job['source_id'])
            fresh = DialogueReviewService(core).prepare(owner, 'synthetic', source_id=source['id'])
            payload = request_payload(source, model=job['model'], max_output_tokens=2000,
                                      dialogue_request=fresh['request'])
            if fingerprint(payload) != job['payload_sha256']:
                raise ValueError('Prepared source/context changed; no automatic reauthorization.')
            core.create_budget(owner, 'synthetic', 'pilot_run', 12000) if not core.db.execute(
                "SELECT 1 FROM run_budgets WHERE run='pilot_run'").fetchone() else None
            extractor = ResponsesExtractor(transport, model=job['model'], max_output_tokens=2000,
                                           authorized=True, grant_id='approved_source', dialogue_review=True)
            sources.authorize_analysis(owner, 'synthetic', source_id=source['id'], key='approved_source',
                root_run='pilot_run', reserved_tokens=12000, provider=extractor.provider,
                model=job['model'], max_output_tokens=2000, expires_at=manifest['expires_at'],
                context_sha256=fresh['context_sha256'],
                reason='Owner-approved synthetic-only pilot; exact payload and shared USD/call ceiling.')
            result = sources.analyze(owner, 'synthetic', source['id'], extractor)
            # Workspace persistence retains raw model output after credential guards; result is private.
            outcome = dict(job=job['id'], model=job['model'], result=result,
                           review_required=True, canonical_proposals_applied=False,
                           semantic_accuracy='not_independently_scored',
                           shared_budget=transport.snapshot())
            private_json(receipt, outcome)
            outcomes.append(outcome)
            if result.get('status') != 'Ready for review' or transport.snapshot()['frozen']:
                break
    return dict(outcomes=outcomes, shared_budget=transport.snapshot(),
                native_capture='not_tested', mvp_acceptance=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--folder', type=Path, default=DEFAULT)
    args = parser.parse_args()
    if args.prepare == args.run:
        parser.error('Select exactly one of --prepare or --run.')
    if args.prepare:
        value = prepare(args.folder)
        print(json.dumps(dict(prepared_jobs=len(value['jobs']), network_calls=0,
                              private_folder=str(args.folder), expires_at=value['manifest']['expires_at'])))
    else:
        value = run(args.folder)
        print(json.dumps(dict(completed_jobs=len(value['outcomes']), shared_budget=value['shared_budget'],
                              semantic_accuracy='requires_independent_review', mvp_acceptance=False)))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        # Neither exception text nor HTTP response can disclose a key/source.
        print('Pilot stopped. Inspect the private local receipts; no automatic retry.', file=sys.stderr)
        raise SystemExit(1)
