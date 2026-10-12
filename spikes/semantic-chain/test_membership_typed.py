import copy
import hashlib
import json
from pathlib import Path
import unittest
from membership_typed import FORMAT,prepare_typed,derive_typed
from anchors import prepare_quotes
from protocol import canonical

ROOT=Path(__file__).resolve().parents[2]


class TestTypedMembership(unittest.TestCase):
    def setUp(self):
        self.requests=json.loads((ROOT/'examples/membership-smoke/requests.json').read_text())
        package=prepare_typed(self.requests)
        responses=[]
        for req in self.requests:
            p=prepare_quotes(req)
            responses.append(dict(format=p['format'],contract_id=p['contract_id'],request_id=req['request_id'],status='ok',records=[]))
        responses[0]['records']=[dict(kind='AnswerRecord',message_id='S02-m01',
            quote='Önceki Q_STORE sorusundaki B, SQLite ile devam.',entity_key='answer',
            attributes=dict(question_id='Q_STORE',option_id='B',presentation_revision=1))]
        responses[1]['records']=[dict(kind='AnswerRecord',message_id='S03-m04',quote='A.',entity_key='ambiguous',attributes={})]
        self.batch=dict(format=FORMAT,attribute_contract_id=package['attribute_contract_id'],responses=responses)

    def test_v2_separate_source_only_and_preserves_ambiguous_record(self):
        package=prepare_typed(self.requests)
        self.assertFalse(package['dispatch_authorized'])
        self.assertNotIn('expected_candidates',package['prompt'])
        result=derive_typed(self.requests,canonical(self.batch))
        self.assertEqual(result['status'],'source_validated')
        self.assertEqual(result['derived'][1]['response']['records'][0]['attributes'],{})
        self.assertFalse(result['semantic_fields_repaired'])
        self.assertEqual(result['canonical_mutations'],0)

    def test_alias_extra_authority_boolean_revision_and_wrong_kind_rejected(self):
        for change in ['alias','extra','boolean','kind','authority']:
            b=copy.deepcopy(self.batch);r=b['responses'][0]['records'][0]
            if change=='alias':r['attributes']['selected_option']=r['attributes'].pop('option_id')
            elif change=='extra':r['attributes']['note']='extra'
            elif change=='boolean':r['attributes']['presentation_revision']=True
            elif change=='kind':r['kind']='Execution'
            else:r['attributes']['approved']=True
            with self.subTest(change=change),self.assertRaises(ValueError):derive_typed(self.requests,canonical(b))

    def test_original_v1_raw_and_stale_v2_cannot_be_promoted(self):
        raw=(ROOT/'docs/quality/model-runs/membership-001-response.txt').read_text()
        with self.assertRaises(ValueError):derive_typed(self.requests,raw)
        b=dict(self.batch,attribute_contract_id='stale')
        with self.assertRaises(ValueError):derive_typed(self.requests,canonical(b))

    def test_claim_and_evidence_have_declared_fields_without_verification_authority(self):
        b=copy.deepcopy(self.batch)
        b['responses'][0]['records'] += [dict(kind='ImplementationClaim',message_id='S02-m05',
            quote='Yükledim.',entity_key='claim',attributes={'claim_type':'upload'}),
            dict(kind='Evidence',message_id='S02-m09',entity_key='criterion',
            quote="İzole fixture testinde rollback kriteri geçti; kanıt AC_ROLLBACK revision 1'e bağlı.",
            attributes=dict(criterion_id='AC_ROLLBACK',criterion_revision=1,result='passed'))]
        self.assertEqual(derive_typed(self.requests,canonical(b))['canonical_mutations'],0)
        bad=copy.deepcopy(b);bad['responses'][0]['records'][-1]['attributes']['result']='verified'
        with self.assertRaises(ValueError):derive_typed(self.requests,canonical(bad))
        bad=copy.deepcopy(b);bad['responses'][0]['records'][1]['attributes']['claim_type']='download'
        with self.assertRaises(ValueError):derive_typed(self.requests,canonical(bad))

    def test_saved_single_v2_output_matches_draft_without_gold_or_state_promotion(self):
        from membership_batch import score_batch
        raw=(ROOT/'docs/quality/model-runs/membership-002-response.txt').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
            'e3941c35f39cdf4117bec100e01249a6eb3ec23b82b263e9998d8371ffc862da')
        result=derive_typed(self.requests,raw.decode('utf-8'))
        rubrics=json.loads((ROOT/'examples/membership-smoke/candidate-rubrics.json').read_text())
        score=score_batch(self.requests,result,rubrics)
        self.assertEqual([s['score']['true_positive'] for s in score['scores']],[3,1])
        self.assertTrue(all(s['score']['false_positive']==s['score']['false_negative']==0 for s in score['scores']))
        self.assertFalse(score['corpus_gold'])
        self.assertEqual(score['canonical_domain'],'unscored')
        self.assertFalse(result['semantic_fields_repaired'])
        self.assertEqual(result['canonical_mutations'],0)

    def test_saved_v2_proposals_cannot_apply_selection_or_verify_claims(self):
        import sys
        import tempfile
        sys.path.insert(0,str(ROOT/'spikes/decision-chain'))
        from chain import Chain
        from bridge import propose
        raw=(ROOT/'docs/quality/model-runs/membership-002-response.txt').read_text()
        result=derive_typed(self.requests,raw)
        with tempfile.TemporaryDirectory() as tmp:
            for i,request in enumerate(self.requests):
                chain=Chain(Path(tmp)/f'{i}.db')
                try:
                    chain.dispatch('seed',dict(decision='markdown',active=['markdown'],tasks={},
                        criteria=['rollback','migration']),'human',0,'seed')
                    q='Q_STORE' if i==0 else 'Q_UI'
                    options={'A':'markdown','B':'sqlite'} if i==0 else {'A':'board','B':'timeline'}
                    chain.dispatch('ask',dict(question_id=q,option_revision=1,options=options),'human',1,'ask')
                    before=chain.snapshot()
                    proposal=propose(chain,request,canonical(result['derived'][i]['response']))
                    self.assertEqual(proposal['status'],['pending_trusted_selection','unmatched_or_stale'][i])
                    self.assertEqual(proposal['canonical_mutations'],0)
                    self.assertEqual(chain.snapshot(),before)
                    self.assertFalse(chain.snapshot()['verified'])
                finally:chain.close()


if __name__=='__main__':unittest.main()
