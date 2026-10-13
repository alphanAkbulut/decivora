from pathlib import Path
import tempfile,unittest
from packages.storage.workspace import Workspace
from packages.domain.questions import QuestionService
from packages.domain.source_event import ContractError

class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'core.sqlite';self.core=Workspace(self.path,'w',owner='owner');self.addCleanup(self.core.close)
        a=self.core.authority;a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=1);self.owner=a.issue_scope('owner');self.core.create_project(self.owner,'p','Project');self.s=QuestionService(self.core)
    def present(self,revision=0):return self.s.present(self.owner,'p',question='Q1',base_revision=revision,text='Storage?',options=[dict(id='sqlite',label='SQLite'),dict(id='files',label='Files')])
    def answer(self,request='a1',revision=1,option='sqlite',question='Q1'):return self.s.answer(self.owner,'p',request_id=request,question=question,revision=revision,option=option)
    def test_restart_keeps_pending_question(self):
        self.present()
        with Workspace(self.path,'w') as c:self.assertEqual(QuestionService(c).view(c.authority.issue_scope('owner'),'p')['questions'][0]['status'],'Open')
    def test_explicit_late_answer_records_selection_not_domain_apply(self):
        self.present();result=self.answer();self.assertEqual(result['status'],'Selected');self.assertFalse(result['canonical_apply']);self.assertEqual(self.core.db.execute('SELECT COUNT(*) FROM events').fetchone()[0],0)
    def test_stale_answer_preserved_does_not_select(self):
        self.present();self.present(1);self.assertEqual(self.answer()['status'],'Stale');self.assertEqual(self.s.view(self.owner,'p')['questions'][0]['status'],'Open')
    def test_unknown_question_or_letter_remains_unmatched(self):
        self.present();self.assertEqual(self.answer(option='A')['status'],'Unmatched');self.assertEqual(self.answer(request='a2',question='missing')['status'],'Unmatched')
    def test_retry_duplicate_and_conflicting_answer(self):
        self.present();first=self.answer();self.assertEqual(first,self.answer());self.assertEqual(self.answer('a2')['status'],'Duplicate');self.assertEqual(self.answer('a3',option='files')['status'],'Conflict');self.assertEqual(self.s.view(self.owner,'p')['questions'][0]['selection'],'sqlite')
    def test_request_id_reuse_is_rejected(self):
        self.present();self.answer()
        with self.assertRaises(ContractError):self.answer(option='files')
    def test_agent_cannot_resolve_or_present_and_scope_is_enforced(self):
        a=self.core.authority;a.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=a.revision());agent=a.issue_scope('agent')
        with self.assertRaises(ContractError):self.s.answer(agent,'p',request_id='a',question='Q1',revision=1,option='sqlite')
        with self.assertRaises(ContractError):self.s.view(agent,'other')
    def test_audit_failure_is_atomic(self):
        self.present();self.core.db.execute("CREATE TRIGGER fail_answer BEFORE INSERT ON audit WHEN NEW.action='question_answered' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(ContractError):self.answer()
        self.assertEqual(self.s.view(self.owner,'p')['questions'][0]['status'],'Open')
    def test_backup_restore_keeps_question_and_answer_history(self):
        self.present();self.answer();b=Path(self.temp.name)/'backup.sqlite';m=self.core.backup(self.owner,b)
        with Workspace.restore(b,Path(self.temp.name)/'restore.sqlite',m) as c:self.assertEqual(QuestionService(c).view(c.authority.issue_scope('owner'),'p')['questions'][0]['selection'],'sqlite')

    def test_capacity_rejects_new_work_without_losing_accepted_records(self):
        self.present()
        for i in range(511):self.answer(request='a'+str(i),option='A')
        with self.assertRaises(ContractError) as caught:self.answer(request='over')
        self.assertEqual(caught.exception.code,'question_history_limit');view=self.s.view(self.owner,'p');self.assertEqual(len(view['answers']),511);self.assertEqual(view['questions'][0]['status'],'Open')
    def test_invalid_question_has_no_write(self):
        with self.assertRaises(ContractError):self.s.present(self.owner,'p',question='Q1',base_revision=0,text='?',options=[dict(id='x',label='X'),dict(id='x',label='Again')])
        self.assertEqual(self.s.view(self.owner,'p')['questions'],[])
