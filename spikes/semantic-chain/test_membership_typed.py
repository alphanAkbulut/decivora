import copy
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


if __name__=='__main__':unittest.main()
