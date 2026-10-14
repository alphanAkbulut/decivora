"""Selected decision hypothesis: scoped, current, durable, no canonical mutation."""
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from packages.storage.workspace import Workspace
from packages.domain.decision_impact import DecisionImpactService
from packages.domain.source_event import ContractError

class DecisionImpactTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.core=Workspace(Path(self.temp.name)/'x.sqlite','w',owner='owner');self.addCleanup(self.core.close)
        a=self.core.authority;a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=1)
        self.scope=a.issue_scope('owner');self.core.create_project(self.scope,'p','Synthetic')
        plan=self.core.plan(self.scope,'p','seed',[dict(op='create',id='d',body=dict(type='Decision',title='Storage decision',description='Synthetic')),dict(op='create',id='t',body=dict(type='Task',title='Affected task',description='Synthetic')),dict(op='link',origin='t',target='d',kind='required_by')])
        self.ids=self.core.apply(self.scope,plan,self.core.approve(self.scope,plan))['temp_ids'];self.service=DecisionImpactService(self.core)
    def preview(self,**changes):
        request=dict(decision=self.ids['d'],decision_version=1,base_revision=self.core.project(self.scope,'p')['knowledge_revision'],key='impact');request.update(changes)
        return self.service.preview(self.scope,'p',**request)
    def test_preview_preserves_task_and_unknown_rationale_and_is_retryable(self):
        before=self.core.projection_digest(self.scope,'p');result=self.preview()
        self.assertEqual(result,self.preview());self.assertEqual(self.core.projection_digest(self.scope,'p'),before)
        row=next(r for r in result['proposals'] if r['record']==self.ids['t'])
        self.assertEqual(row['action'],'review');self.assertTrue(row['requires_approval'])
        self.assertTrue(any(e['kind']=='required_by' for e in row['reason_path']))
        self.assertFalse(self.core.impact_run(self.scope,'p','impact')['stale'])
    def test_stale_trigger_foreign_and_boolean_revisions_denied(self):
        for request in [dict(decision='foreign'),dict(decision_version=2),dict(base_revision=0),dict(decision_version=True)]:
            with self.assertRaises(ContractError):self.preview(**request)
    def test_project_race_rechecked_in_preview_transaction(self):
        original=self.core.impact_preview
        def raced(*args,**kwargs):
            plan=self.core.plan(self.scope,'p','race',[dict(op='create',id='x',body=dict(type='Idea',title='Concurrent idea',description='Synthetic'))])
            self.core.apply(self.scope,plan,self.core.approve(self.scope,plan));return original(*args,**kwargs)
        with patch.object(self.core,'impact_preview',side_effect=raced):
            with self.assertRaises(ContractError) as caught:self.preview()
        self.assertEqual(caught.exception.code,'stale_base')
        self.assertEqual(self.core.db.execute("SELECT count(*) FROM audit WHERE action='impact_preview'").fetchone()[0],0)
    def test_agent_cannot_submit_human_hypothesis(self):
        a=self.core.authority;a.replace_grant(self.scope,'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=a.revision())
        with self.assertRaises(ContractError):self.service.preview(a.issue_scope('agent'),'p',decision=self.ids['d'],decision_version=1,base_revision=self.core.project(a.issue_scope('owner'),'p')['knowledge_revision'],key='agent')

