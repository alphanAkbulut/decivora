"""Replay saved MEMBERSHIP-002 candidates in isolated fixtures; no inference/egress.

Selection, impact and verifier inputs are separate authored test fixtures, not
authentication or verification inferred from model text. No original input rebind.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'decision-chain'))
from chain import Chain
from bridge import propose, apply_selection
from local_observer import observe
from membership_typed import derive_typed
from membership_batch import read
from protocol import canonical, digest, score_checkpoints, strict_json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def apply_fixture_impact(chain, project_id, receipt):
    """Separate synthetic caller boundary; not a production IAM adapter."""
    if (receipt.get('authenticated') is not True or
            receipt.get('permission') != 'impact.approve' or
            receipt.get('project_id') != project_id):
        raise PermissionError('fixture impact receipt denied')
    return chain.dispatch('impact',
        dict(preview_digest=receipt['preview_digest'], actions=receipt['actions']),
        'human', receipt['base_revision'], 'fixture-impact-' + digest(receipt))


def _bound_request(requests, fixture):
    matches = [r for r in requests if r['request_id'] == fixture['request_id']]
    if len(matches) != 1 or matches[0]['source']['project_id'] != fixture['project_id']:
        raise ValueError('fixture request/project binding mismatch')
    request = matches[0]
    question = fixture['question']
    presentations = request['source']['context'].get('question_presentations', [])
    if not any(p['question_id'] == question['question_id'] and
               p['revision'] == question['option_revision'] and
               p['options'] == question['options'] for p in presentations):
        raise ValueError('fixture question differs from frozen source context')
    return request


def replay(*, requests_path=ROOT/'examples/membership-smoke/requests.json',
           response_path=ROOT/'docs/quality/model-runs/membership-002-response.txt',
           scenario_path=HERE/'fixtures/membership-chain-scenario.json',
           expected_path=HERE/'fixtures/membership-chain-checkpoints.json'):
    requests = strict_json(read(requests_path))
    raw = read(response_path)
    scenario = strict_json(read(scenario_path))
    if scenario.get('format') != 'membership-chain-fixture-1' or scenario.get('fixture_trust_only') is not True:
        raise ValueError('explicit controlled fixture required')
    if hashlib.sha256(raw.encode()).hexdigest() != scenario['raw_sha256']:
        raise ValueError('saved first-output bytes changed')
    imported = derive_typed(requests, raw)
    if imported['status'] != 'source_validated':
        raise ValueError('incomplete saved candidate batch')
    request = _bound_request(requests, scenario)
    ambiguous_request = _bound_request(requests, scenario['ambiguity'])
    responses = {x['request_id']: x['response'] for x in imported['derived']}
    response = responses[request['request_id']]
    target = scenario['target']
    if not isinstance(scenario['verifier_results'], list) or len(scenario['verifier_results']) != 2:
        raise ValueError('exactly partial/full authored verifier fixtures required')
    if target['path'] != 'bundle.md' or any(
            not isinstance(target[k], str) or len(target[k].encode()) > 131072
            for k in ('content', 'old_content')):
        raise ValueError('target must be a bounded isolated bundle fixture')
    checkpoints, local_reads = {}, []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        chain = Chain(root/'storage.db')
        ambiguous_chain = Chain(root/'release.db')

        def send(command, payload, actor='human'):
            rev = chain.snapshot()['revision']
            return chain.dispatch(command, payload, actor, rev, str(rev)+'-'+command)

        try:
            send('seed', copy.deepcopy(scenario['seed']))
            send('ask', copy.deepcopy(scenario['question']))
            proposal = propose(chain, request, canonical(response))
            state = chain.snapshot()
            checkpoints['proposal'] = dict(status=proposal['status'], decision=state['decision'],
                revision=state['revision'], canonical_mutations=proposal['canonical_mutations'])
            if proposal['status'] != 'pending_trusted_selection':
                raise ValueError('saved candidate cannot be selected in this fixture')
            # Model claim/Evidence remain records; never dispatch verifier from them.
            checkpoints['reported_evidence'] = dict(
                claims=sum(r['kind'] == 'ImplementationClaim' for r in response['records']),
                evidence_candidates=sum(r['kind'] == 'Evidence' for r in response['records']),
                verified=state['verified'], evidence=state['evidence'], observation=state['observation'])
            receipt = copy.deepcopy(scenario['selection_receipt'])
            denied = dict(receipt, authenticated=False)
            before = chain.snapshot()['revision']
            rejected = False
            try:
                apply_selection(chain, request, proposal, denied, scenario['project_id'])
            except PermissionError:
                rejected = True
            checkpoints['denied_selection'] = dict(rejected=rejected,
                canonical_mutations=chain.snapshot()['revision']-before)
            selected_event = apply_selection(chain, request, proposal, receipt, scenario['project_id'])
            state = chain.snapshot()
            preview = chain.preview()
            checkpoints['decision'] = dict(decision=state['decision'],
                task_statuses=sorted({v['status'] for v in state['tasks'].values()}), impact=preview['impact'])
            before = state['revision']
            retry_event = apply_selection(chain, request, proposal, receipt, scenario['project_id'])
            checkpoints['selection_retry'] = dict(same_event=selected_event == retry_event,
                canonical_mutations=chain.snapshot()['revision']-before)
            apply_fixture_impact(chain, scenario['project_id'], scenario['impact_receipt'])
            checkpoints['impact'] = dict(statuses={k:v['status'] for k,v in chain.snapshot()['tasks'].items()})
            content = target['content'].encode()
            expected_hash = hashlib.sha256(content).hexdigest()
            send('expect', dict(artifact_revision=target['artifact_revision'], ref=target['ref'],
                path=target['path'], sha256=expected_hash))

            def collect(ref):
                observation = observe(root, target['path'], expected_hash)
                if observation['status'] not in ('mismatch', 'observed_match'):
                    raise ValueError('isolated target observation unavailable')
                local_reads.append({k:observation[k] for k in (
                    'status', 'observed_sha256', 'bytes_read', 'task_verified', 'remote_upload_verified')})
                # Explicit fixture metadata; local read does not prove a Git revision.
                return dict(availability='read', sha256=observation['observed_sha256'],
                    artifact_revision=target['artifact_revision'], ref=ref, path=target['path'])

            (root/target['path']).write_text(target['old_content'])
            for point, ref in [('old_target', target['old_ref']), ('wrong_content', target['ref'])]:
                send('observe', collect(ref), 'observer')
                state = chain.snapshot()
                checkpoints[point] = dict(status=state['observation']['status'], verified=state['verified'])
            (root/target['path']).write_bytes(content)
            send('observe', collect(target['ref']), 'observer')
            state = chain.snapshot()
            checkpoints['current_target'] = dict(status=state['observation']['status'], verified=state['verified'])
            for point, criteria in zip(('partial', 'complete'), scenario['verifier_results']):
                send('verify', dict(artifact_revision=target['artifact_revision'], criteria=criteria), 'verifier')
                state = chain.snapshot()
                checkpoints[point] = dict(verified=state['verified'], evidence=state['evidence'])
            # backup() really opens the backup and replays the stored events without IO dispatch.
            before_restore = chain.snapshot()
            restored_digest = chain.backup(root/'backup.db')
            restored = Chain(root/'backup.db')
            try:
                restored_state = restored.snapshot()
                count = lambda c: c.conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
                checkpoints['restore'] = dict(same_projection=restored_digest == digest(before_restore) == digest(restored_state),
                    same_event_count=count(chain) == count(restored), external_dispatches=0)
            finally:
                restored.close()
            ambiguous_chain.dispatch('seed', dict(decision='board', active=['board'], tasks={}, criteria=[]), 'human', 0, 'seed')
            ambiguous_chain.dispatch('ask', scenario['ambiguity']['question'], 'human', 1, 'ask')
            ambiguous_before = ambiguous_chain.snapshot()
            ambiguous_response = responses[ambiguous_request['request_id']]
            ambiguous_proposal = propose(ambiguous_chain, ambiguous_request, canonical(ambiguous_response))
            checkpoints['ambiguous'] = dict(status=ambiguous_proposal['status'],
                answer_candidates=sum(r['kind'] == 'AnswerRecord' for r in ambiguous_response['records']),
                canonical_mutations=ambiguous_chain.snapshot()['revision']-ambiguous_before['revision'],
                question_state=ambiguous_chain.snapshot()['question']['state'])
            event_count = count(chain)
        finally:
            ambiguous_chain.close()
            chain.close()
    expected = strict_json(read(expected_path))
    return dict(kind='saved_membership_output_controlled_chain_replay', origin_run='MEMBERSHIP-002',
        new_model_dispatches=0, external_dispatches=0, paid_api_requests=0, usage=None,
        raw_sha256=imported['typed_raw_sha256'], request_ids=[r['request_id'] for r in requests],
        source_sha256=request['source_sha256'], semantic_fields_repaired=False,
        scenario_sha256=hashlib.sha256(Path(scenario_path).read_bytes()).hexdigest(),
        expected_sha256=hashlib.sha256(Path(expected_path).read_bytes()).hexdigest(),
        checkpoints=checkpoints, checkpoint_score=score_checkpoints(expected, checkpoints),
        storage_event_count=event_count, bounded_local_reads=local_reads,
        production_runtime=False, remote_upload_verified=False, human_gold=False,
        evidence_layers=dict(extraction='saved real model output on synthetic development messages',
            authority='separate authored fixture receipts', graph='deterministic controlled fixture',
            target='real read of temporary authored file; ref/revision metadata fixture',
            acceptance='separate scripted verifier outcomes', restore='SQLite backup/reopen/event projection'),
        limitations=['Not fresh inference, blind holdout or general quality measurement',
            'Single-question fixture per project; no production IAM or concurrent question engine',
            'Chain verification binds artifact revision, not per-criterion revision; production AC binding still required',
            'Fixture event schema does not persist full production source/receipt lineage'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = replay()
    body = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n'
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            stream.write(body)
    else:
        print(body, end='')
    if result['checkpoint_score']['status'] != 'passed':
        raise SystemExit(1)
