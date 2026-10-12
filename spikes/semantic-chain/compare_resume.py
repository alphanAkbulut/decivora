"""Offline resume versus equal-information simple-file serialization; no receiving model."""
import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'decision-chain'))
from chain import Chain
from collect_membership import ROOT, QUESTIONS, RAW_SHA
from membership_typed import derive_typed
from protocol import canonical, strict_json, score_checkpoints
from resume_package import serialize_arms

HERE = Path(__file__).resolve().parent


def inspect_core(core):
    state = core['fixture_state']
    question = state['question']
    records = core['preserved_records']
    result = dict(question_id=question['question_id'], question_revision=question['option_revision'],
                  question_state=question['state'],
                  answer_statuses={e['candidate']['message_id']: e['status']
                                   for e in core['answer_candidates']},
                  source_message_count=len(core['source_messages']), record_count=len(records),
                  verified=state['verified'], approved_decision_from_source=question['state'] == 'resolved')
    evidence = [r for r in records if r['kind'] == 'Evidence']
    if evidence:
        result['reported_criterion_result'] = evidence[0]['attributes']['result']
        result['upload_claims'] = sum(r['kind'] == 'ImplementationClaim' for r in records)
    return result


def compare():
    requests_path = ROOT / 'examples/adversarial-smoke/requests.json'
    raw_path = ROOT / 'docs/quality/model-runs/membership-003-response.txt'
    raw = raw_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != RAW_SHA:
        raise ValueError('saved model output changed')
    requests = strict_json(requests_path.read_text())
    imported = derive_typed(requests, raw.decode())
    if imported['status'] != 'source_validated':
        raise ValueError('incomplete saved output')
    bundles, resume_actual, file_actual = {}, {}, {}
    with tempfile.TemporaryDirectory() as tmp:
        for i, (request, derived) in enumerate(zip(requests, imported['derived'])):
            chain = Chain(Path(tmp) / f'{i}.db')
            try:
                chain.dispatch('seed', dict(decision='fixture_initial', active=['fixture_initial'],
                    tasks={}, criteria=['rollback', 'migration']), 'human', 0, 'seed')
                qid, revision, options = QUESTIONS[i]
                chain.dispatch('ask', dict(question_id=qid, option_revision=revision,
                    options=options), 'human', 1, 'ask')
                access = dict(can_read=True, project_id=request['source']['project_id'],
                              source_sha256=request['source_sha256'], authz_revision=1)
                before = chain.snapshot()
                arms = serialize_arms(chain, request, canonical(derived['response']), access)
                if chain.snapshot() != before or arms['status'] != 'prepared':
                    raise AssertionError('export mutated state or incomplete')
                sid = request['source']['session_id']
                # Read back the exact exported serialization, not the in-memory renderer result.
                resume_actual[sid] = inspect_core(strict_json(arms['texts']['resume'])['core'])
                file_actual[sid] = inspect_core(strict_json(arms['texts']['simple_file']))
                bundles[sid] = arms
            finally:
                chain.close()
    # The authored independent checklist is only read after both arm outputs are produced.
    expectation_path = HERE / 'fixtures/resume-checkpoints.json'
    expected = strict_json(expectation_path.read_text())
    paths = [requests_path, raw_path, expectation_path, HERE/'resume_package.py',
             HERE/'compare_resume.py', HERE/'bridge.py', HERE/'protocol.py',
             ROOT/'spikes/decision-chain/chain.py']
    report = dict(experiment_id='RESUME-FILE-001', origin_run='MEMBERSHIP-003',
                  status='offline_serialization_and_guards_only', human_gold=False,
                  receiver_model_test='not_run', native_host_test='not_run',
                  package_score=score_checkpoints(expected, resume_actual),
                  simple_file_score=score_checkpoints(expected, file_actual),
                  same_core_information=all(b['same_core_information'] for b in bundles.values()),
                  bytes={sid:b['bytes'] for sid,b in bundles.items()},
                  actual=dict(resume=resume_actual, simple_file=file_actual),
                  token_counts=None, cost=None, human_correction_time=None,
                  new_model_dispatches=0, selection_dispatches=0, paid_api_calls=0,
                  canonical_mutations=0, production_runtime=False,
                  fixture_only_access=True,
                  conclusions=['Equal facts survive both representations; no superiority shown',
                    'Resume adds a checked snapshot envelope; simple files can implement the same guards',
                    'Byte size is measured, token/cost/receiving-model behavior is not'],
                  hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    return report, bundles


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--export-dir', type=Path, help='new directory for inspectable synthetic arms')
    args = parser.parse_args()
    for path in (args.out, args.export_dir):
        if path is not None and (path.exists() or path.is_symlink()):
            parser.error('output target already exists; nothing exported')
    result, bundles = compare()
    if args.export_dir:
        args.export_dir.mkdir()  # Fail before overwriting an existing directory.
        for sid, bundle in bundles.items():
            for arm, extension in [('resume','json'),('simple_file','json'),('source_only','md')]:
                name = {'resume':'resume', 'simple_file':'state', 'source_only':'source'}[arm]
                with (args.export_dir / f'{sid}-{name}.{extension}').open('x') as stream:
                    stream.write(bundle['texts'][arm])
    body = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    if args.out:
        with args.out.open('x') as stream: stream.write(body)
    else:
        print(body, end='')
    if any(result[k]['status'] != 'passed' for k in ('package_score','simple_file_score')):
        raise SystemExit(1)
