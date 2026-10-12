import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from receiver_smoke import prepare,check_request,validate_response,evaluate,FORMAT,ROOT
from protocol import canonical,digest

PACKET=ROOT/'examples/receiver-smoke'


class TestReceiverSmoke(unittest.TestCase):
    def setUp(self):
        self.request=json.loads((PACKET/'request.json').read_text())
        self.oracle=json.loads((PACKET/'expected.json').read_text())
        # Scripted evaluator positive, NEVER a model-run output or model quality claim.
        self.output=dict(format=FORMAT,request_id=self.request['request_id'],responses=copy.deepcopy(self.oracle['responses']))

    def score(self,output=None,oracle=None):
        return evaluate(self.request,canonical(self.output if output is None else output),self.oracle if oracle is None else oracle)

    def test_frozen_prepare_matches_prompt_sources_and_no_expected_input(self):
        request=prepare();self.assertEqual(request,self.request)
        self.assertEqual(request['prompt'],(PACKET/'prompt.txt').read_text())
        self.assertLessEqual(request['prompt_bytes'],8192)
        self.assertFalse(request['dispatch_authorized'])
        self.assertNotIn('next_actions": [{"message_id": "N01-m01',request['prompt'])
        self.assertNotIn('review_status',request['prompt'])
        self.assertFalse(request['paid_api_allowed'])

    def test_scripted_positive_is_draft_unverified_not_model_evidence(self):
        score=self.score();self.assertEqual(score['status'],'passed_draft')
        self.assertEqual(score['action_score'],dict(true_positive=6,false_positive=0,false_negative=0))
        self.assertFalse(score['human_gold']);self.assertEqual(score['model_dispatches'],0)
        self.assertEqual(score['response_origin'],'caller_imported_unverified')

    def test_stale_question_or_not_run_promoted_to_passed_fails_domain_score(self):
        for which in ('question','test'):
            out=copy.deepcopy(self.output)
            if which=='question':out['responses'][0]['readback']['question_revision']=1
            else:out['responses'][1]['readback']['reported_test_results'][0]['result']='passed'
            score=self.score(out);self.assertEqual(score['status'],'failed_draft')
            if which=='test':self.assertTrue(score['critical_errors'])

    def test_false_approval_false_done_and_false_upload_are_critical(self):
        for field,value in [('approved_real_decision',True),('task_verified',True),('upload_verification','observed_verified')]:
            out=copy.deepcopy(self.output);out['responses'][1]['readback'][field]=value
            score=self.score(out);self.assertEqual(score['status'],'failed_draft')
            self.assertEqual(score['critical_errors'][0]['field'],field)

    def test_guessed_ambiguous_question_fails_actions_and_is_critical(self):
        out=copy.deepcopy(self.output);out['responses'][1]['next_actions'][1]['question_id']='Q_UI'
        score=self.score(out);self.assertEqual(score['status'],'failed_draft')
        self.assertTrue(score['critical_errors']);self.assertEqual(score['action_score']['false_positive'],1)

    def test_missing_project_or_abstention_is_incomplete_not_pass(self):
        for rows in [[],self.output['responses'][:1],[dict(self.output['responses'][0],status='abstain',readback=None,next_actions=[]),self.output['responses'][1]]]:
            self.assertEqual(self.score(dict(self.output,responses=rows))['status'],'incomplete')
        out=copy.deepcopy(self.output);out['responses'][0]['readback']['answer_states']=[]
        self.assertEqual(self.score(out)['status'],'failed_draft')

    def test_foreign_project_package_message_or_duplicate_is_rejected(self):
        for which in ('project','package','message','duplicate'):
            out=copy.deepcopy(self.output)
            if which=='project':out['responses'][0]['project_id']='other'
            elif which=='package':out['responses'][0]['package_digest']='stale'
            elif which=='message':out['responses'][0]['next_actions'][0]['message_id']='N02-m01'
            else:out['responses'][1]=copy.deepcopy(out['responses'][0])
            with self.assertRaises(ValueError):self.score(out)

    def test_no_coercion_alias_or_execution_action_and_duplicates_rejected(self):
        for which in ('bool','revision','alias','execute','dup_action','dup_answer','dup_test'):
            out=copy.deepcopy(self.output);row=out['responses'][1]
            if which=='bool':row['readback']['task_verified']='false'
            elif which=='revision':row['readback']['question_revision']=True
            elif which=='alias':row['authenticated']=True
            elif which=='execute':row['next_actions'][0]['type']='apply_decision'
            elif which=='dup_action':row['next_actions'].append(copy.deepcopy(row['next_actions'][0]))
            elif which=='dup_answer':row['readback']['answer_states'].append(copy.deepcopy(row['readback']['answer_states'][0]))
            else:row['readback']['reported_test_results']*=2
            with self.assertRaises(ValueError):self.score(out)

    def test_response_json_bounds_and_no_silent_fence_repair(self):
        for raw in ['x'*32769,'{"format":"a","format":"b"}','{"a":NaN}','```json\n'+canonical(self.output)+'\n```']:
            with self.assertRaises(ValueError):evaluate(self.request,raw,self.oracle)

    def test_changed_request_prompt_or_source_is_not_rebound(self):
        for which in ('prompt','view'):
            r=copy.deepcopy(self.request)
            if which=='prompt':r['prompt']+='extra'
            else:r['views'][0]['fixture_state']['verified']=True
            with self.assertRaises(ValueError):check_request(r)
        out=copy.deepcopy(self.output);out['request_id']='old'
        with self.assertRaises(ValueError):self.score(out)

    def test_oracle_missing_duplicate_stale_and_gold_promotion_rejected(self):
        for change in ('missing','duplicate','stale','gold'):
            oracle=copy.deepcopy(self.oracle)
            if change=='missing':oracle['responses']=oracle['responses'][:1]
            elif change=='duplicate':oracle['responses'][1]=copy.deepcopy(oracle['responses'][0])
            elif change=='stale':oracle['request_id']='old'
            else:oracle['review_status']='human_gold'
            with self.assertRaises(ValueError):self.score(oracle=oracle)

    def test_order_independent_lists_and_extra_action_not_extra_success(self):
        out=copy.deepcopy(self.output);out['responses'].reverse()
        for row in out['responses']:
            row['next_actions'].reverse();row['readback']['answer_states'].reverse()
        self.assertEqual(self.score(out)['status'],'passed_draft')
        out=copy.deepcopy(self.output);out['responses'][0]['next_actions'].append(
            dict(type='request_selection_confirmation',message_id='N01-m01',question_id='Q_STORE'))
        self.assertEqual(self.score(out)['status'],'failed_draft')
        self.assertTrue(self.score(out)['critical_errors'])

    def test_cli_no_expected_input_during_prepare_and_no_overwrite(self):
        script=ROOT/'spikes/semantic-chain/receiver_smoke.py'
        result=subprocess.run([sys.executable,'-B',str(script),'prepare','--expected',str(PACKET/'expected.json')],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'keep';path.write_text('keep')
            result=subprocess.run([sys.executable,'-B',str(script),'prepare','--out',str(path)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0);self.assertEqual(path.read_text(),'keep')


if __name__=='__main__':unittest.main()
