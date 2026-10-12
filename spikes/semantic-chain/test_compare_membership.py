import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from compare_membership import compare, ROOT
from membership_typed import prepare_typed
from anchors import anchor, prepare_quotes
from protocol import canonical


class TestSameSourceComparison(unittest.TestCase):
    def test_saved_model_and_lexical_use_same_source_and_shared_fields_only(self):
        r = compare()
        self.assertEqual(r['source_messages'],4)
        self.assertEqual(r['methods']['saved_model']['score']['strict_span']['tp'],4)
        self.assertEqual(r['methods']['lexical']['score']['strict_span']['fp'],1)
        self.assertEqual(r['methods']['lexical']['score']['strict_span']['fn'],4)
        self.assertEqual(r['predictions']['lexical'][0]['kind'],'Decision')
        self.assertEqual({p['project_id'] for p in r['predictions']['saved_model']}, {'prj_memory','prj_release'})
        self.assertFalse(r['capability_differences']['semantic_attributes_scored'])
        self.assertEqual(r['capability_differences']['lexical_missing_candidate_kinds'],['AnswerRecord','Evidence'])
        self.assertFalse(r['human_gold'])
        self.assertEqual(r['native_comparison'],'not_run')
        self.assertEqual(r['cost_comparison'],'unknown')
        self.assertEqual(r['new_model_dispatches'],0)
        self.assertEqual(r['canonical_mutations'],0)

    def test_foreign_duplicate_or_fewer_rubrics_cannot_silently_change_denominator(self):
        rubrics=json.loads((ROOT/'examples/membership-smoke/candidate-rubrics.json').read_text())
        for mode in ('foreign','duplicate','missing'):
            bad=copy.deepcopy(rubrics)
            if mode=='foreign':bad[0]['request_id']='foreign'
            elif mode=='duplicate':bad[1]=copy.deepcopy(bad[0])
            else:bad.pop()
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                p=Path(tmp)/'rubrics.json';p.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):compare(rubrics_path=p)

    def test_abstained_import_is_incomplete_and_not_promoted_to_original_real_run(self):
        raw=json.loads((ROOT/'docs/quality/model-runs/membership-002-response.txt').read_text())
        raw['responses'][0].update(status='abstain',records=[])
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'abstained.json';p.write_text(json.dumps(raw))
            r=compare(response_path=p)
            self.assertEqual(r['methods']['saved_model']['status'],'incomplete_abstained')
            self.assertIsNone(r['origin_run'])
            self.assertEqual(r['response_origin'],'caller_imported_unverified')
            self.assertEqual(r['methods']['saved_model']['score']['critical_domain_gate'],'incomplete')


class TestNewDevelopmentFamilies(unittest.TestCase):
    def setUp(self):
        self.folder=ROOT/'examples/adversarial-smoke'
        self.requests=json.loads((self.folder/'requests.json').read_text())

    def test_frozen_source_only_packet_reproduces_and_remains_unauthorized(self):
        package=prepare_typed(self.requests)
        plan=json.loads((self.folder/'plan.json').read_text())
        manifest=json.loads((self.folder/'manifest.json').read_text())
        self.assertEqual(package['prompt'],(self.folder/'prompt.txt').read_text())
        self.assertEqual(hashlib.sha256(package['prompt'].encode()).hexdigest(),plan['prompt_sha256'])
        self.assertEqual(sum(len(r['source']['messages']) for r in self.requests),8)
        self.assertLessEqual(package['prompt_bytes'],8192)
        self.assertFalse(plan['dispatch_authorized'])
        self.assertEqual(plan['actual_submissions'],0)
        self.assertFalse(plan['paid_api_allowed'])
        self.assertNotIn('expected_candidates',package['prompt'])
        self.assertEqual(manifest['review_status'],'authored_draft')
        self.assertIn('not_sealed',manifest['holdout_status'])
        old=json.loads((ROOT/'examples/membership-smoke/requests.json').read_text())
        self.assertFalse(set(r['request_id'] for r in old)&set(r['request_id'] for r in self.requests))

    def test_authored_quotes_and_old_current_versions_are_independently_bound(self):
        rubrics=json.loads((self.folder/'candidate-rubrics.json').read_text())
        counts=[]
        for request,rubric in zip(self.requests,rubrics):
            packet=prepare_quotes(request)
            fixture=dict(format=packet['format'],contract_id=packet['contract_id'],request_id=request['request_id'],status='ok',
                records=[dict(row,entity_key='fixture-'+str(i)) for i,row in enumerate(rubric['expected'])])
            counts.append(len(anchor(request,canonical(fixture))['response']['records']))
        self.assertEqual(counts,[2,4])  # Schema/source validation of authored fixtures, not inference accuracy.
        old,current=self.requests[0]['source']['context']['question_presentations']
        self.assertNotEqual(old['options']['B'],current['options']['B'])
        quoted_future={m['message_id'] for m in self.requests[0]['source']['messages'][-2:]}
        self.assertFalse(quoted_future & {c['message_id'] for c in rubrics[0]['expected']})


if __name__=='__main__':unittest.main()
