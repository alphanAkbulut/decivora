"""Run the source/response/approval/target pipeline with a named contract fixture."""
import hashlib
import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'decision-chain'))
from chain import Chain, digest
from bridge import propose, apply_selection
from protocol import validate, score_checkpoints
from experiment import requests
from anchors import prepare_quotes, anchor
from local_observer import observe


def run(response_path=None):
    prepared = requests()
    request = next(r for r in prepared if r['source']['session_id'] == 'S02')
    message = request['source']['messages'][0]
    # Scripted external-output contract fixture, deliberately not called model inference.
    packet = prepare_quotes(request)
    quote_output = dict(format=packet['format'],request_id=request['request_id'],
      contract_id=packet['contract_id'],status='ok',
      records=[dict(message_id=message['message_id'],kind='AnswerRecord',entity_key='answer-storage',
      quote=message['text'],attributes=dict(
      question_id='Q_STORE',option_id='B',presentation_revision=1))])
    anchored = anchor(request, json.dumps(quote_output,ensure_ascii=False))
    response = anchored['response']
    if response_path is not None:
        response=json.loads(Path(response_path).read_text())
    checkpoints = {}
    local_reads = []
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);chain=Chain(root/'events.db')
        def send(cmd,payload,actor='human'):
            rev=chain.snapshot()['revision']
            return chain.dispatch(cmd,payload,actor,rev,str(rev)+'-'+cmd)
        try:
            send('seed',dict(decision='markdown',active=['markdown','security'],tasks={
              'sync':dict(expr='markdown',status='todo'),
              'export':dict(expr={'any':['markdown','sqlite']},status='todo'),
              'combined':dict(expr={'all':['markdown','security']},status='todo'),
              'watch':dict(expr=None,status='todo')},criteria=['rollback','migration']))
            send('ask',dict(question_id='Q_STORE',option_revision=1,options={'A':'markdown','B':'sqlite'}))
            proposal=propose(chain,request,json.dumps(response,ensure_ascii=False))
            state=chain.snapshot();checkpoints['proposal']=dict(decision=state['decision'],revision=state['revision'],canonical_mutations=proposal['canonical_mutations'])
            receipt={k:proposal[k] for k in ['project_id','source_sha256','message_id','question_id','option_revision','option','base_revision']}
            receipt.update(authenticated=True,permission='decision.approve')
            apply_selection(chain,request,proposal,receipt,request['source']['project_id'])
            state=chain.snapshot();preview=chain.preview()
            checkpoints['decision']=dict(decision=state['decision'],task_statuses=sorted({v['status'] for v in state['tasks'].values()}),**preview['impact'])
            bad=json.loads(json.dumps(response));bad['records'][0]['attributes']['accepted']=True
            before=chain.snapshot()['revision'];rejected=False
            try:validate(request,json.dumps(bad))
            except ValueError:rejected=True
            checkpoints['model_authority']=dict(rejected=rejected,canonical_mutations=chain.snapshot()['revision']-before)
            send('impact',dict(preview_digest=preview['preview_digest'],actions={'sync':'obsolete','export':'retained','combined':'review','watch':'review'}))
            content=b'SQLite migration contract fixture';(root/'bundle.md').write_bytes(content)
            send('expect',dict(artifact_revision=2,ref='fixture-ref-2',path='bundle.md',sha256=hashlib.sha256(content).hexdigest()))
            def collect(ref):
                observation=observe(root,'bundle.md',hashlib.sha256(content).hexdigest())
                if observation['status'] != 'observed_match':
                    raise ValueError('controlled local artifact failed observation')
                local_reads.append(dict(status=observation['status'],
                    task_verified=observation['task_verified'],
                    remote_upload_verified=observation['remote_upload_verified']))
                # Revision/ref are explicitly scripted fixture metadata, not inferred Git proof.
                return dict(availability='read',sha256=observation['observed_sha256'],
                            artifact_revision=2,ref=ref,path='bundle.md')
            send('observe',collect('old-ref'),'observer')
            state=chain.snapshot();checkpoints['old_target']=dict(status=state['observation']['status'],verified=state['verified'])
            send('observe',collect('fixture-ref-2'),'observer')
            send('verify',dict(artifact_revision=2,criteria={'rollback':'passed'}),'verifier')
            checkpoints['partial']=dict(verified=chain.snapshot()['verified'])
            send('verify',dict(artifact_revision=2,criteria={'migration':'passed'}),'verifier')
            checkpoints['complete']=dict(verified=chain.snapshot()['verified'])
            backup=chain.backup(root/'backup.db')
            checkpoints['restore']=dict(same_projection=backup==digest(chain.snapshot()),external_dispatches=0)
        finally:chain.close()
    # Authored expected assertions are independent of current code projections and loaded last.
    expected_path=Path(__file__).with_name('expected-checkpoints.json')
    expected=json.loads(expected_path.read_text())
    return dict(kind='source_response_chain_contract_smoke',
      response_origin='imported_candidate_draft_not_blind_inference' if response_path else 'scripted_contract_fixture_not_inference',source_session='S02',
      request_count=len(prepared),request_ids=[r['request_id'] for r in prepared],
      checkpoints=checkpoints,checkpoint_score=score_checkpoints(expected,checkpoints),
      expected_sha256=hashlib.sha256(expected_path.read_bytes()).hexdigest(),
      prompt_version=request['prompt_version'],prompt_sha256=request['prompt_sha256'],
      model_dispatches=0,semantic_inference='not_run',human_gold_review='pending',
      real_host=False,real_target=False,production_runtime=False,usage=None,
      source_binding='quote_only_scripted' if not response_path else 'imported_legacy_candidate',
      bounded_local_reads=local_reads,
      limitations=['explicit synthetic trusted receipt is not production authentication',
                   'contract fixture is not model output quality',
                   'fixture AC outcomes are controlled inputs',
                   'partial checkpoint scorer does not cover every release invariant'])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--response',type=Path);args=parser.parse_args()
    print(json.dumps(run(args.response),ensure_ascii=False,indent=2))
