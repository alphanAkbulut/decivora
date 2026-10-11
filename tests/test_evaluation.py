import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('corpus_eval',Path(__file__).resolve().parents[1]/'scripts/evaluate_corpus.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class TestIndependentScorer(unittest.TestCase):
    def fixture(self):
        source=[dict(project_id='p',messages=[dict(message_id='m',text='SQLite seçildi')])]
        gold=[dict(project_id='p',items=[dict(message_id='m',records=[
            dict(kind='Decision',source_span=dict(start=0,end=6))])])]
        prediction=dict(project_id='p',message_id='m',kind='Decision',start=0,end=6,quote='SQLite')
        return source,gold,prediction

    def test_duplicate_prediction_cannot_inflate(self):
        s,g,p=self.fixture();r=module.score(s,[p,p],g)['strict_span']
        self.assertEqual((r['tp'],r['fp'],r['fn']),(1,1,0))

    def test_wrong_kind_and_missing_denominators(self):
        s,g,p=self.fixture()
        self.assertEqual(module.score(s,[],g)['strict_span']['recall'],0)
        self.assertIsNone(module.score(s,[],g)['strict_span']['precision'])
        self.assertEqual(module.score(s,[dict(p,kind='Task')],g)['strict_span']['tp'],0)

    def test_scope_and_span_errors_are_not_success(self):
        s,g,p=self.fixture()
        for bad in [dict(p,project_id='other'),dict(p,end=999),dict(p,quote='different')]:
            with self.assertRaises(ValueError):module.score(s,[bad],g)

    def test_oracle_cannot_enter_extractor(self):
        with self.assertRaises(ValueError):module.lexical([dict(items=[])])

    def test_coarse_score_is_not_domain_gate(self):
        s,g,p=self.fixture()
        r=module.score(s,[dict(p,end=14,quote='SQLite seçildi')],g)
        self.assertEqual(r['strict_span']['tp'],0)
        self.assertEqual(r['message_kind_only']['tp'],1)
        self.assertEqual(r['critical_domain_gate'],'incomplete')
