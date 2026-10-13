import unittest,tempfile,threading
from pathlib import Path
import test_questions
from packages.domain.question_decisions import QuestionDecisionService
from packages.domain.questions import QuestionService
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace

class QuestionDecisionTests(unittest.TestCase):
    setUp=test_questions.QuestionTests.setUp
    present=test_questions.QuestionTests.present
    answer=test_questions.QuestionTests.answer
    def prepare(self,key='proposal'):
        self.present();self.answer();self.d=QuestionDecisionService(self.core);return self.d.prepare(self.owner,'p',key=key,answer_id='a1',reason='Local persistence is needed.')
    def test_prepare_approve_apply_are_separate_and_retry_single_effect(self):
        p=self.prepare();self.assertEqual(self.core.records(self.owner,'p')['records'],[])
        a=self.d.approve(self.owner,'p',p['id']);self.assertEqual(self.core.records(self.owner,'p')['records'],[])
        r=self.d.apply(self.owner,'p',p['id'],a);self.assertEqual(r,self.d.apply(self.owner,'p',p['id'],a));records=self.core.records(self.owner,'p')['records'];self.assertEqual(len(records),1);self.assertEqual(records[0]['body']['type'],'Decision');self.assertIn('Local persistence',records[0]['body']['description'])
    def test_no_approval_cannot_apply(self):
        p=self.prepare()
        with self.assertRaises(ContractError):self.d.apply(self.owner,'p',p['id'],'forged')
    def test_changed_question_invalidates_approved_proposal(self):
        p=self.prepare();a=self.d.approve(self.owner,'p',p['id']);self.present(1)
        with self.assertRaises(ContractError):self.d.apply(self.owner,'p',p['id'],a)
        self.assertEqual(self.core.records(self.owner,'p')['records'],[])
    def test_generic_apply_cannot_bypass_question_guard(self):
        p=self.prepare();a=self.d.approve(self.owner,'p',p['id'])
        with self.assertRaises(ContractError) as caught:self.core.apply(self.owner,p['plan'],a)
        self.assertEqual(caught.exception.code,'question_approval_required')
    def test_project_change_requires_new_proposal(self):
        p=self.prepare();a=self.d.approve(self.owner,'p',p['id']);plan=self.core.plan(self.owner,'p','other',[dict(op='create',id='task',body=dict(type='Task',title='Task',description='Scope'))]);self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))
        with self.assertRaises(ContractError):self.d.apply(self.owner,'p',p['id'],a)
        self.assertEqual(self.d.view(self.owner,'p')[0]['state'],'Stale')
    def test_two_proposals_cannot_resolve_same_question_twice(self):
        p=self.prepare();p2=self.d.prepare(self.owner,'p',key='other',answer_id='a1',reason='Different proposal');a=self.d.approve(self.owner,'p',p['id']);b=self.d.approve(self.owner,'p',p2['id']);self.d.apply(self.owner,'p',p['id'],a)
        with self.assertRaises(ContractError):self.d.apply(self.owner,'p',p2['id'],b)
    def test_audit_failure_rolls_back_decision_and_receipt(self):
        p=self.prepare();a=self.d.approve(self.owner,'p',p['id']);self.core.db.execute("CREATE TRIGGER fail_resolution BEFORE INSERT ON audit WHEN NEW.action='question_decision_applied' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(ContractError):self.d.apply(self.owner,'p',p['id'],a)
        self.assertEqual(self.core.records(self.owner,'p')['records'],[]);self.assertEqual(self.core.db.execute('SELECT COUNT(*) FROM commands').fetchone()[0],0)
    def test_restart_restore_and_replay_keep_binding(self):
        p=self.prepare();a=self.d.approve(self.owner,'p',p['id']);r=self.d.apply(self.owner,'p',p['id'],a);self.core.replay(self.owner,'p');b=Path(self.temp.name)/'backup.sqlite';m=self.core.backup(self.owner,b)
        with Workspace.restore(b,Path(self.temp.name)/'restore.sqlite',m) as c:
            service=QuestionDecisionService(c);owner=c.authority.issue_scope('owner');self.assertEqual(service.view(owner,'p')[0]['state'],'Applied');self.assertEqual(service.apply(owner,'p',p['id'],a),r)
    def test_agent_denied_and_authority_change_invalidates_old_approval(self):
        p=self.prepare();a=self.d.approve(self.owner,'p',p['id']);authority=self.core.authority;authority.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=authority.revision());agent=authority.issue_scope('agent')
        with self.assertRaises(ContractError):self.d.approve(agent,'p',p['id'])
        fresh=authority.issue_scope('owner')
        with self.assertRaises(ContractError):self.d.apply(fresh,'p',p['id'],a)
    def test_two_connections_apply_once(self):
        p=self.prepare();a=self.d.approve(self.owner,'p',p['id']);barrier=threading.Barrier(2);results=[];errors=[]
        def run():
            try:
                with Workspace(self.path,'w') as c:
                    scope=c.authority.issue_scope('owner');barrier.wait(timeout=5);results.append(QuestionDecisionService(c).apply(scope,'p',p['id'],a))
            except Exception as e:errors.append(e)
        threads=[threading.Thread(target=run) for _ in range(2)]
        for t in threads:t.start()
        for t in threads:t.join(timeout=10)
        self.assertEqual(errors,[]);self.assertEqual(len(results),2);self.assertEqual(results[0],results[1]);self.assertEqual(len(self.core.records(self.owner,'p')['records']),1)
