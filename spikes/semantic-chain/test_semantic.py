import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'decision-chain'))
from chain import Chain, digest
from bridge import propose, apply_selection
from protocol import prepare, validate, strict_json, score_checkpoints
from experiment import requests, evaluate, read_responses


def source(actor='human_owner', text='Önceki Q_STORE sorusundaki B, SQLite ile devam.'):
    return dict(synthetic=True,project_id='p',session_id='later',messages=[
        dict(message_id='m',source_revision=1,text=text,actor=dict(type=actor),
             metadata=dict(authenticated=True,permission='decision.approve'))])


def response(request, status='ok'):
    text=request['source']['messages'][0]['text']
    return dict(format='decivora-candidates-1',request_id=request['request_id'],status=status,
       records=[] if status=='abstain' else [dict(message_id='m',kind='AnswerRecord',
       entity_key='answer',start=0,end=len(text),quote=text,attributes=dict(
       question_id='Q_STORE',option_id='B',presentation_revision=1))])


class TestProtocol(unittest.TestCase):
    def setUp(self): self.request=prepare(source());self.output=response(self.request)

    def test_source_only_no_auth_or_oracle(self):
        self.assertNotIn('metadata',self.request['source']['messages'][0])
        for invalid in [dict(source(),items=[]),dict(source(),synthetic=False)]:
            with self.assertRaises(ValueError):prepare(invalid)
        with self.assertRaises(ValueError):prepare(source(),dict(expected='sqlite'))

    def test_request_bounds_and_duplicate_sources(self):
        s=source(text='x'*40000)
        with self.assertRaises(ValueError):prepare(s)
        s=source();s['messages']*=2
        with self.assertRaises(ValueError):prepare(s)

    def test_source_and_prompt_revision_invalidate_cache(self):
        for key in ['source','prompt']:
            r=copy.deepcopy(self.request)
            if key=='source':r[key]['messages'][0]['text']='changed'
            else:r[key]='changed prompt'
            with self.assertRaises(ValueError):validate(r,json.dumps(self.output))

    def test_project_namespace_changes_request(self):
        self.assertNotEqual(prepare(dict(source(),project_id='other'))['request_id'],self.request['request_id'])

    def test_unicode_quote_and_candidate_only(self):
        v=validate(self.request,json.dumps(self.output,ensure_ascii=False))
        self.assertEqual(v['records'][0]['quote'],source()['messages'][0]['text'])
        self.assertEqual(v['canonical_mutations'],0)
        self.assertEqual(v['records'][0]['lifecycle'],'candidate')

    def test_stale_response_and_foreign_message(self):
        for change in [dict(request_id='stale'),dict(format='unknown')]:
            with self.assertRaises(ValueError):validate(self.request,json.dumps(dict(self.output,**change)))
        self.output['records'][0]['message_id']='other'
        with self.assertRaises(ValueError):validate(self.request,json.dumps(self.output))

    def test_invalid_spans_and_nonliteral_quotes(self):
        for change in [dict(start=True),dict(end=9999),dict(quote='SQLite seçildi')]:
            output=copy.deepcopy(self.output);output['records'][0].update(change)
            with self.assertRaises(ValueError):validate(self.request,json.dumps(output))

    def test_no_model_authority_even_nested(self):
        for value in [dict(accepted=True),dict(details=dict(verified=True)),dict(command='answer')]:
            output=copy.deepcopy(self.output);output['records'][0]['attributes']=value
            with self.assertRaises(ValueError):validate(self.request,json.dumps(output))

    def test_duplicate_keys_nonfinite_and_oversize(self):
        for value in ['{"a":1,"a":2}','{"a":NaN}','x'*131073]:
            with self.assertRaises(ValueError):strict_json(value)

    def test_abstention_is_not_noop_completion(self):
        self.assertEqual(validate(self.request,json.dumps(response(self.request,'abstain')))['coverage'],'abstained')
        with self.assertRaises(ValueError):validate(self.request,json.dumps(dict(self.output,status='abstain')))

    def test_duplicate_records_and_cap(self):
        for n in [2,65]:
            with self.assertRaises(ValueError):validate(self.request,json.dumps(dict(self.output,records=self.output['records']*n)))

    def test_answer_revision_types_are_not_coerced(self):
        for change in [dict(presentation_revision=True),dict(presentation_revision=0),dict(question_id=None)]:
            out=copy.deepcopy(self.output);out['records'][0]['attributes'].update(change)
            with self.assertRaises(ValueError):validate(self.request,json.dumps(out))

    def test_evaluator_missing_abstained_foreign(self):
        self.assertEqual(evaluate([])['status'],'incomplete')
        r=requests()[0]
        self.assertTrue(evaluate([dict(format='decivora-candidates-1',request_id=r['request_id'],status='abstain',records=[])])['abstained'])
        with self.assertRaises(ValueError):evaluate([dict(request_id='foreign')])

    def test_pretty_json_array_and_jsonl_response_import(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'responses.json'
            for body in [json.dumps(self.output,indent=2),json.dumps([self.output]),json.dumps(self.output)+'\n'+json.dumps(self.output)]:
                path.write_text(body)
                self.assertEqual(read_responses(path)[0],self.output)
            path.write_text('{"request_id":"x","request_id":"y"}')
            with self.assertRaises(ValueError):read_responses(path)

    def test_checkpoint_missing_failed_and_passed(self):
        expected={'old_target':{'verified':False},'partial':{'verified':False}}
        self.assertEqual(score_checkpoints(expected,{'partial':{'verified':False}})['status'],'incomplete')
        self.assertEqual(score_checkpoints(expected,{'partial':{'verified':False},'old_target':{'verified':True}})['status'],'failed')
        self.assertEqual(score_checkpoints(expected,{k:dict(v) for k,v in expected.items()})['status'],'passed')
        self.assertEqual(score_checkpoints({}, {})['status'],'incomplete')

    def test_imported_draft_runs_chain_but_does_not_claim_model_quality(self):
        here=Path(__file__).parent
        spec=importlib.util.spec_from_file_location('semantic_smoke',here/'run.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        draft=here/'fixtures/assistant-s02-draft.json'
        result=module.run(draft)
        self.assertEqual(result['checkpoint_score']['status'],'passed')
        self.assertEqual(result['semantic_inference'],'not_run')
        evaluated=evaluate([json.loads(draft.read_text())])
        self.assertEqual(evaluated['status'],'incomplete')
        self.assertEqual(evaluated['score']['critical_domain_gate'],'incomplete')


class TestBridge(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.chain=Chain(Path(self.tmp.name)/'events.db');self.addCleanup(self.chain.close)
        self.chain.dispatch('seed',dict(decision='markdown',active=['markdown','security'],tasks={
            'sync':dict(expr='markdown',status='todo'),'export':dict(expr={'any':['markdown','sqlite']},status='todo'),
            'combined':dict(expr={'all':['markdown','security']},status='todo'),'watch':dict(expr=None,status='todo')},
            criteria=['rollback','migration']),'human',0,'seed')
        self.chain.dispatch('ask',dict(question_id='Q_STORE',option_revision=1,options={'A':'markdown','B':'sqlite'}),'human',1,'ask')
        self.request=prepare(source());self.output=response(self.request)
        self.proposal=propose(self.chain,self.request,json.dumps(self.output))

    def receipt(self):
        keys=['project_id','source_sha256','message_id','question_id','option_revision','option','base_revision']
        return dict({k:self.proposal[k] for k in keys},authenticated=True,permission='decision.approve')

    def apply(self,receipt=None):
        return apply_selection(self.chain,self.request,self.proposal,self.receipt() if receipt is None else receipt,'p')

    def test_model_output_is_proposal_only(self):
        self.assertEqual(self.proposal['status'],'pending_trusted_selection')
        self.assertEqual(self.chain.snapshot()['decision'],'markdown')
        self.assertEqual(self.chain.snapshot()['revision'],2)

    def test_trusted_late_selection_and_separate_impact(self):
        self.apply();state=self.chain.snapshot()
        self.assertEqual(state['decision'],'sqlite')
        self.assertEqual({t['status'] for t in state['tasks'].values()},{'todo'})
        self.assertEqual(self.chain.preview()['impact'],dict(sync='obsolete_candidate',combined='obsolete_candidate',export='retained',watch='review_unknown'))

    def test_text_metadata_or_model_claim_is_not_receipt(self):
        with self.assertRaises(PermissionError):self.apply({})
        with self.assertRaises(PermissionError):self.apply(source()['messages'][0]['metadata'])
        self.assertEqual(self.chain.snapshot()['revision'],2)

    def test_wrong_scope_option_source_or_auth(self):
        for change in [dict(project_id='other'),dict(option='A'),dict(source_sha256='old'),dict(authenticated=False)]:
            with self.assertRaises(PermissionError):self.apply(dict(self.receipt(),**change))

    def test_assistant_cannot_approve_with_owner_claim(self):
        request=prepare(source(actor='assistant'));proposal=propose(self.chain,request,json.dumps(response(request)))
        receipt=dict(self.receipt(),source_sha256=proposal['source_sha256'])
        with self.assertRaises(PermissionError):apply_selection(self.chain,request,proposal,receipt,'p')

    def test_mutated_proposal_and_request_are_rejected(self):
        with self.assertRaises(ValueError):apply_selection(self.chain,self.request,dict(self.proposal,option='A'),self.receipt(),'p')
        self.request['source']['messages'][0]['actor_type']='assistant'
        with self.assertRaises(ValueError):self.apply()

    def test_question_context_abstention_and_multiple_answers(self):
        out=copy.deepcopy(self.output);out['records'][0]['attributes']['question_id']='OTHER'
        self.assertEqual(propose(self.chain,self.request,json.dumps(out))['status'],'unmatched_or_stale')
        self.assertEqual(propose(self.chain,self.request,json.dumps(response(self.request,'abstain')))['status'],'needs_context')
        out=copy.deepcopy(self.output);second=copy.deepcopy(out['records'][0]);second['entity_key']='other';out['records'].append(second)
        self.assertEqual(propose(self.chain,self.request,json.dumps(out))['status'],'unmatched_or_ambiguous')

    def test_retries_and_stale_base(self):
        first=self.apply();self.assertEqual(self.apply(),first)
        self.assertEqual(self.chain.snapshot()['revision'],3)
        self.chain.dispatch('add_reason',dict(task='sync',expr='sqlite'),'human',3,'reason')
        # A different command with stale base cannot reuse a prior selection's key.
        self.proposal['message_id']='m';self.proposal['option']='A'
        self.proposal['proposal_digest']=digest({k:v for k,v in self.proposal.items() if k!='proposal_digest'})
        with self.assertRaises(ValueError):self.apply()
