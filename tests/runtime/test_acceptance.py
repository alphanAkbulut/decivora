"""Versioned acceptance contracts cannot silently weaken or fabricate completion."""
from pathlib import Path
import tempfile
import unittest
from copy import deepcopy
from packages.storage.workspace import Workspace
from packages.domain.acceptance import AcceptanceService
from packages.domain.source_event import ContractError

class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'core.sqlite';self.core=Workspace(self.path,'workspace',owner='owner');self.addCleanup(self.core.close)
        a=self.core.authority;a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'p1'}),writable=frozenset({'p1'}),active=True,base_revision=1);self.owner=a.issue_scope('owner');self.core.create_project(self.owner,'p1','Project')
        self.body=dict(type='Task',title='Task',description='Initial');plan=self.core.plan(self.owner,'p1','seed',[dict(op='create',id='t',body=self.body)]);self.task=self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))['temp_ids']['t'];self.service=AcceptanceService(self.core)
        criterion=lambda rid:dict(id=rid,statement='Observable result',method='human_review',required=True,applicable=True,applicability_reason='')
        self.op=dict(op='acceptance_contract',task=self.task,task_version=1,base_contract=0,criteria=[criterion('AC1')],dod=[criterion('DOD1')],reason='Initial explicit approval',acknowledged_changes=[])
    def code(self,code,fn):
        with self.assertRaises(ContractError) as caught:fn()
        self.assertEqual(caught.exception.code,code)
    def save(self,op=None,key='contract'):
        plan=self.core.plan(self.owner,'p1',key,[op or self.op]);token=self.core.approve(self.owner,plan);return self.core.apply(self.owner,plan,token)
    def test_contract_approval_version_history_and_not_run_results(self):
        self.save();view=self.service.view(self.owner,'p1',self.task)
        self.assertEqual(view['current']['version'],1);self.assertFalse(view['completed']);self.assertTrue(all(r['status']=='not_run' for r in view['results']))
        self.assertEqual(self.service.start(self.owner,'p1',self.task)['implementation_claim'],'in_progress')
    def test_work_cannot_start_before_approved_criteria(self):self.code('acceptance_required',lambda:self.service.start(self.owner,'p1',self.task))
    def test_required_criterion_change_needs_explicit_diff_ack(self):
        self.save();op=deepcopy(self.op);op['base_contract']=1;op['criteria'][0]['required']=False
        self.code('acceptance_diff_required',lambda:self.save(op,'changed'))
        op['acknowledged_changes']=['AC1'];op['reason']='Owner reviewed the scope change';self.save(op,'explicit')
        self.assertEqual(len(self.service.view(self.owner,'p1',self.task)['history']),2)
    def test_not_applicable_without_reason_is_rejected(self):
        op=deepcopy(self.op);op['criteria'][0]['applicable']=False
        self.code('invalid_acceptance',lambda:self.save(op))
    def test_empty_ac_or_dod_rejected(self):
        for key in ('criteria','dod'):
            op=deepcopy(self.op);op[key]=[];self.code('invalid_acceptance',lambda:self.save(op))
    def test_stale_task_and_stale_contract_are_rejected(self):
        self.save();self.code('stale_acceptance',lambda:self.save(key='duplicate_revision'))
        plan=self.core.plan(self.owner,'p1','task_edit',[dict(op='update',id=self.task,base_version=1,body=dict(self.body,title='New'))]);self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))
        self.assertTrue(self.service.view(self.owner,'p1',self.task)['stale']);self.code('acceptance_required',lambda:self.service.start(self.owner,'p1',self.task))
    def test_replay_backup_restore_and_restart_keep_contract(self):
        self.save();before=self.core.projection_digest(self.owner,'p1');self.assertEqual(self.core.replay(self.owner,'p1')['digest'],before)
        backup=Path(self.temp.name)/'backup.sqlite';manifest=self.core.backup(self.owner,backup)
        with Workspace.restore(backup,Path(self.temp.name)/'restore.sqlite',manifest) as restored:self.assertEqual(AcceptanceService(restored).view(restored.authority.issue_scope('owner'),'p1',self.task)['current']['version'],1)
    def test_agent_cannot_approve_contract_or_start_work(self):
        a=self.core.authority;a.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p1'}),writable=frozenset({'p1'}),active=True,base_revision=a.revision());agent=a.issue_scope('agent')
        plan=self.core.plan(agent,'p1','agent',[self.op]);self.code('human_approval_required',lambda:self.core.approve(agent,plan));self.code('human_approval_required',lambda:self.service.start(agent,'p1',self.task))
    def test_audit_failure_rolls_back_contract_event(self):
        self.core.db.execute("CREATE TRIGGER fail_ac BEFORE INSERT ON audit WHEN NEW.action='apply' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        self.code('storage_failure',self.save);self.assertIsNone(self.service.view(self.owner,'p1',self.task)['current'])
