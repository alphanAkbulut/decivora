import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from membership_batch import FORMAT, derive_batch, prepare_batch, score_batch
from protocol import canonical, prepare
from anchors import prepare_quotes

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'spikes/decision-chain'))
from chain import Chain
from bridge import propose


class TestMembershipBatch(unittest.TestCase):
    def setUp(self):
        self.requests=[prepare(dict(synthetic=True,project_id=p,session_id='s',messages=[dict(
            message_id='m',source_revision=1,actor=dict(type='human_owner'),text='A.')])) for p in ['one','two']]
        self.responses=[];self.rubrics=[]
        for req in self.requests:
            pkt=prepare_quotes(req)
            self.responses.append(dict(format=pkt['format'],request_id=req['request_id'],contract_id=pkt['contract_id'],
                status='ok',records=[dict(message_id='m',kind='AnswerRecord',entity_key='unmatched',quote='A.',attributes={})]))
            # Independent literal expectation; no expected fields inside model packet.
            self.rubrics.append(dict(format='decivora-candidate-rubric-1',request_id=req['request_id'],
                review_status='authored_draft',expected=[dict(message_id='m',kind='AnswerRecord',quote='A.',attributes={})]))

    def raw(self, responses=None):
        return canonical(dict(format=FORMAT,responses=self.responses if responses is None else responses))

    def test_preparation_is_source_only_bound_and_unauthorized(self):
        package=prepare_batch(self.requests)
        self.assertFalse(package['dispatch_authorized'])
        self.assertEqual(package['dispatch'],'not_run')
        self.assertNotIn('expected',package['prompt'])
        self.assertIsNone(package['usage'])
        self.assertFalse(package['hard_token_cap_verified'])
        self.assertEqual(package,prepare_batch(self.requests))

    def test_isolated_requests_score_without_canonical_or_gold_claim(self):
        imported=derive_batch(self.requests,self.raw())
        result=score_batch(self.requests,imported,self.rubrics)
        self.assertEqual([s['score']['true_positive'] for s in result['scores']],[1,1])
        self.assertFalse(result['corpus_gold'])
        self.assertEqual(imported['canonical_mutations'],0)

    def test_missing_and_abstained_not_success(self):
        imported=derive_batch(self.requests,self.raw(self.responses[:1]))
        self.assertEqual(score_batch(self.requests,imported,[])['status'],'incomplete')
        responses=copy.deepcopy(self.responses);responses[0].update(status='abstain',records=[])
        imported=derive_batch(self.requests,self.raw(responses))
        self.assertEqual(score_batch(self.requests,imported,self.rubrics)['status'],'incomplete')

    def test_duplicate_foreign_stale_and_bad_quote_atomic_rejection(self):
        for change in ['duplicate','foreign','contract','quote','authority']:
            responses=copy.deepcopy(self.responses)
            if change=='duplicate':responses[1]=responses[0]
            elif change=='foreign':responses[1]['request_id']='foreign'
            elif change=='contract':responses[1]['contract_id']='old'
            elif change=='quote':responses[1]['records'][0]['quote']='missing'
            else:responses[1]['records'][0]['attributes']['accepted']=True
            with self.subTest(change=change),self.assertRaises(ValueError):derive_batch(self.requests,self.raw(responses))

    def test_limits_and_rubric_binding(self):
        with self.assertRaises(ValueError):prepare_batch(self.requests*2)
        with self.assertRaises(ValueError):prepare_batch([self.requests[0]]*2)
        with self.assertRaises(ValueError):derive_batch(self.requests,self.raw()+' '*65536)
        imported=derive_batch(self.requests,self.raw())
        with self.assertRaises(ValueError):score_batch(self.requests,imported,self.rubrics[:1]*2)

    def test_full_prompt_byte_limit_and_project_identity_swap(self):
        large=prepare(dict(synthetic=True,project_id='p',session_id='s',messages=[dict(
            message_id=str(i),source_revision=1,actor=dict(type='assistant'),text='x'*2000)
            for i in range(5)]))
        with self.assertRaises(ValueError):prepare_batch([large])
        responses=copy.deepcopy(self.responses)
        responses[0]['request_id'],responses[1]['request_id']=responses[1]['request_id'],responses[0]['request_id']
        with self.assertRaises(ValueError):derive_batch(self.requests,self.raw(responses))

    def test_recorded_real_output_source_valid_but_exact_score_incomplete(self):
        folder=ROOT/'examples/membership-smoke'
        requests=json.loads((folder/'requests.json').read_text())
        raw=(ROOT/'docs/quality/model-runs/membership-001-response.txt').read_text()
        self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(),
            'e3f3ae3f0b4d6a71837f6ac073fcd5b68979c26f8214c903d9def11cb8aab953')
        imported=derive_batch(requests,raw)
        self.assertEqual(imported['status'],'source_validated')
        rubric=json.loads((folder/'candidate-rubrics.json').read_text())
        evaluation=score_batch(requests,imported,rubric)
        self.assertEqual(evaluation['status'],'incomplete')
        self.assertEqual([(s['score']['true_positive'],s['score']['false_positive'],s['score']['false_negative'])
            for s in evaluation['scores']],[(0,3,3),(0,0,1)])
        self.assertFalse(evaluation['corpus_gold'])

    def test_recorded_reply_aliases_never_auto_apply_decision_or_repair_raw(self):
        requests=json.loads((ROOT/'examples/membership-smoke/requests.json').read_text())
        raw=(ROOT/'docs/quality/model-runs/membership-001-response.txt').read_text()
        imported=derive_batch(requests,raw)
        with tempfile.TemporaryDirectory() as d:
            chain=Chain(Path(d)/'events.db')
            try:
                chain.dispatch('seed',dict(decision='D_MARKDOWN',active=['D_MARKDOWN'],
                    tasks={},criteria=['rollback','migration']),'human',0,'seed')
                chain.dispatch('ask',dict(question_id='Q_STORE',option_revision=1,
                    options={'A':'D_MARKDOWN','B':'D_SQLITE'}),'human',1,'ask')
                before=chain.snapshot()
                statuses=[]
                for req,derived in zip(requests,imported['derived']):
                    proposal=propose(chain,req,canonical(derived['response']))
                    statuses.append(proposal['status'])
                    self.assertEqual(proposal['canonical_mutations'],0)
                self.assertEqual(statuses,['unmatched_or_stale','needs_context'])
                self.assertEqual(chain.snapshot(),before)
                self.assertEqual(imported['derived'][0]['response']['records'][0]['attributes']['selected_option'],'B')
                self.assertNotIn('option_id',imported['derived'][0]['response']['records'][0]['attributes'])
            finally:chain.close()


if __name__=='__main__':unittest.main()
