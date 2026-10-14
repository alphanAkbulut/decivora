"""Workflow, local-human verification and dependency guards: independent domain tests."""
import json,tempfile,unittest
from pathlib import Path
from packages.storage.workspace import Workspace
from packages.storage.project_store import canonical
from packages.domain.acceptance import AcceptanceService
from packages.domain.task_workflow import TaskWorkflowService
from packages.domain.task_blockers import TaskBlockerService
from packages.domain.source_event import ContractError

class WorkflowTests(unittest.TestCase):
    def test_audit_reuse_is_read_snapshot_only_and_result_cannot_poison_cache(self):
        self.ready_for_verification();self.evidence('AC1')
        with self.core.read_snapshot():
            first=self.s._rows('p',self.task,'criterion_evidence')
            first[0]['status']='failed'
            self.assertEqual(self.s._rows('p',self.task,'criterion_evidence')[0]['status'],'passed')
            self.assertIn(('p','criterion_evidence'),self.core.workflow_audit_read_cache)
        self.assertIsNone(self.core.workflow_audit_read_cache)
        self.evidence('AC1',status='failed')
        with self.core.read_snapshot():
            self.assertEqual(self.s._rows('p',self.task,'criterion_evidence')[-1]['status'],'failed')
        with self.core.transaction():
            self.s._rows('p',self.task,'criterion_evidence')
            self.assertIsNone(self.core.workflow_audit_read_cache)

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'workflow.sqlite'
        self.core=Workspace(self.path,'w',owner='owner');self.addCleanup(self.core.close);a=self.core.authority;a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=1);self.owner=a.issue_scope('owner');self.core.create_project(self.owner,'p','Project')
        self.s=TaskWorkflowService(self.core);self.i=0;self.task=self.create('Task');self.contract(self.task)
    def apply(self,ops):
        self.i+=1;plan=self.core.plan(self.owner,'p','op'+str(self.i),ops);return self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))
    def create(self,title):return self.apply([dict(op='create',id='t',body=dict(type='Task',title=title,description='Scope'))])['temp_ids']['t']
    def contract(self,task,base=0,method='human_review'):
        row=lambda rid:dict(id=rid,statement='Observed review',method=method,required=True,applicable=True,applicability_reason='')
        self.apply([dict(op='acceptance_contract',task=task,task_version=self.s._task('p',task)['version'],base_contract=base,criteria=[row('AC1')],dod=[row('DOD1')],reason='Explicit scope',acknowledged_changes=['AC1','DOD1'] if base else [])])
    def stage(self,stage,task=None,**kw):
        task=task or self.task;view=self.s.view(self.owner,'p',task);self.i+=1
        return self.s.transition(self.owner,'p',task=task,task_version=self.s._task('p',task)['version'],base_revision=view['revision'],stage=stage,reason='Human stage review',key='stage'+str(self.i),**kw)
    def evidence(self,criterion,status='passed',task=None):
        task=task or self.task;v=self.s.view(self.owner,'p',task)['verification'];self.i+=1
        return self.s.evidence(self.owner,'p',task=task,task_version=self.s._task('p',task)['version'],contract_version=v['contract_version'],criterion=criterion,status=status,reference='Human review notes',note='Observed criterion scope',key='evidence'+str(self.i))
    def ready_for_verification(self,task=None):
        for stage in ('In Progress','In Review','Awaiting Verification'):self.stage(stage,task)
    def complete(self,task=None):
        self.ready_for_verification(task);self.evidence('AC1',task=task);self.evidence('DOD1',task=task);return self.stage('Done',task,scope_reviewed=True)
    def test_partial_criteria_never_complete_then_full_explicit_done(self):
        self.ready_for_verification();self.evidence('AC1')
        with self.assertRaises(ContractError):self.stage('Done',scope_reviewed=True)
        self.evidence('DOD1');self.assertEqual(self.stage('Done',scope_reviewed=True)['stage'],'Done')
        self.evidence('AC1','failed');self.assertEqual(self.s.view(self.owner,'p',self.task)['stage'],'Awaiting Verification')
        self.assertEqual(self.s._rows('p',self.task,'task_stage')[-1]['stage'],'Done')
    def test_gate_finish_allows_start_but_prevents_done(self):
        TaskBlockerService(self.core).set(self.owner,'p',task=self.task,task_version=1,base_revision=0,blocked=True,reason='Await external delivery',next_action='Check delivery',gate='finish',waiting_kind='input')
        self.ready_for_verification();self.evidence('AC1');self.evidence('DOD1')
        with self.assertRaises(ContractError):self.stage('Done',scope_reviewed=True)
    def test_dependency_needs_actual_completion_and_blocks_direction(self):
        prerequisite=self.create('Prerequisite');self.contract(prerequisite)
        self.apply([dict(op='link',origin=self.task,target=prerequisite,kind='depends_on')])
        self.ready_for_verification();self.evidence('AC1');self.evidence('DOD1')
        self.assertIn(self.task,self.s.view(self.owner,'p',prerequisite)['assessment']['blocks'])
        with self.assertRaises(ContractError):self.stage('Done',scope_reviewed=True)
        self.complete(prerequisite);self.assertEqual(self.stage('Done',scope_reviewed=True)['stage'],'Done')
        self.stage('In Progress',prerequisite);self.assertEqual(self.s.view(self.owner,'p',self.task)['stage'],'Awaiting Verification')
    def test_new_contract_stales_evidence_and_success(self):
        self.complete();self.contract(self.task,base=1)
        v=self.s.view(self.owner,'p',self.task);self.assertEqual(v['stage'],'Awaiting Verification');self.assertEqual(v['verification']['results'][0]['status'],'stale')
    def test_automatic_verifier_cannot_be_spoofed_by_human_endpoint(self):
        self.contract(self.task,base=1,method='automatic_test');self.ready_for_verification()
        with self.assertRaises(ContractError):self.evidence('AC1')
    def test_stale_revision_retry_and_changed_identity(self):
        kwargs=dict(task=self.task,task_version=1,base_revision=0,stage='In Progress',reason='Explicit',key='stable')
        first=self.s.transition(self.owner,'p',**kwargs);self.assertEqual(self.s.transition(self.owner,'p',**kwargs),first)
        with self.assertRaises(ContractError):self.s.transition(self.owner,'p',**dict(kwargs,stage='Backlog'))
        with self.assertRaises(ContractError):self.s.transition(self.owner,'p',**dict(kwargs,key='other'))
    def test_old_start_does_not_override_lifecycle_reopen(self):
        self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',('w','p','owner','task_work_started',canonical(dict(task=self.task,task_version=1,contract_version=1))))
        self.assertEqual(self.s.view(self.owner,'p',self.task)['stage'],'In Progress')
        # Projector regression fixture: lifecycle guard behavior is separately tested.
        for base,state in ((1,'cancelled'),(2,'todo')):
            op=dict(op='task_lifecycle',id=self.task,base_version=base,state=state,reason='Fixture regression',impact_run='fixture')
            seq=self.core.db.execute('INSERT INTO events(workspace,project,stream,version,kind,payload) VALUES (?,?,?,?,?,?)',('w','p',self.task,base+1,'task_lifecycle',canonical(op))).lastrowid
            self.core._project_event(op,'p',seq)
        self.assertEqual(self.s.view(self.owner,'p',self.task)['stage'],'To Do')
    def test_replay_restore_and_audit_failure_preserve_state(self):
        self.complete();self.core.replay(self.owner,'p');self.assertEqual(self.s.view(self.owner,'p',self.task)['stage'],'Done')
        backup=Path(self.temp.name)/'backup.sqlite';manifest=self.core.backup(self.owner,backup)
        with Workspace.restore(backup,Path(self.temp.name)/'restored.sqlite',manifest) as restored:self.assertEqual(TaskWorkflowService(restored).view(restored.authority.issue_scope('owner'),'p',self.task)['stage'],'Done')
        self.core.db.execute("CREATE TRIGGER stop BEFORE INSERT ON audit WHEN NEW.action='task_stage' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(ContractError):self.stage('In Progress')
        self.assertEqual(self.s.view(self.owner,'p',self.task)['stage'],'Done')
    def test_agent_cannot_transition_or_verify(self):
        a=self.core.authority;a.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=a.revision());agent=a.issue_scope('agent')
        with self.assertRaises(ContractError):self.s.transition(agent,'p',task=self.task,task_version=1,base_revision=0,stage='In Progress',reason='Agent claim',key='agent')
    def test_backlog_selection_and_invalid_direct_done(self):
        self.stage('Backlog');self.assertEqual(self.stage('To Do')['stage'],'To Do')
        with self.assertRaises(ContractError):self.stage('Done',scope_reviewed=True)

    def test_question_answer_is_not_applied_decision_or_task_done(self):
        from packages.domain.questions import QuestionService
        from packages.domain.question_decisions import QuestionDecisionService
        q=QuestionService(self.core);q.present(self.owner,'p',question='q1',base_revision=0,text='Choose scope?',options=[dict(id='a',label='A'),dict(id='b',label='B')],task=self.task)
        self.ready_for_verification();self.evidence('AC1');self.evidence('DOD1')
        with self.assertRaises(ContractError):self.stage('Done',scope_reviewed=True)
        q.answer(self.owner,'p',request_id='answer',question='q1',revision=1,option='a')
        with self.assertRaises(ContractError):self.stage('Done',scope_reviewed=True)
        service=QuestionDecisionService(self.core);service.prepare(self.owner,'p',key='qdecision',answer_id='answer',reason='Human decision rationale');token=service.approve(self.owner,'p','qdecision');service.apply(self.owner,'p','qdecision',token)
        self.assertEqual(self.stage('Done',scope_reviewed=True)['stage'],'Done')

    def test_published_payload_required_fields_and_statuses_match_real_events(self):
        self.complete()
        root=Path(__file__).resolve().parents[2]
        for action,name in [('task_stage','task-stage-v2'),('criterion_evidence','criterion-evidence')]:
            schema=json.loads((root/'manifests'/f'{name}.schema.json').read_text())
            rows=self.core.db.execute('SELECT ref FROM audit WHERE action=?',(action,)).fetchall()
            self.assertTrue(rows)
            for raw, in rows:
                payload=json.loads(raw)
                self.assertEqual(set(payload),set(schema['required']))
                self.assertEqual(set(payload),set(schema['properties']))
                for key,spec in schema['properties'].items():
                    if 'enum' in spec:self.assertIn(payload[key],spec['enum'])
                    if 'const' in spec:self.assertEqual(payload[key],spec['const'])
            self.assertFalse(schema['additionalProperties'])

    def test_related_decision_change_invalidates_completion_but_unrelated_change_does_not(self):
        decision=self.apply([dict(op='create',id='d',body=dict(type='Decision',title='Storage choice',description='SQLite'))])['temp_ids']['d'];self.apply([dict(op='link',origin=self.task,target=decision,kind='required_by')]);self.complete()
        downstream=self.create('Unrelated task');self.apply([dict(op='link',origin=downstream,target=self.task,kind='depends_on')]);self.assertEqual(self.s.view(self.owner,'p',self.task)['stage'],'Done')
        self.apply([dict(op='update',id=decision,base_version=1,body=dict(type='Decision',title='New storage choice',description='Changed scope'))]);self.assertEqual(self.s.view(self.owner,'p',self.task)['stage'],'Awaiting Verification')

    def test_legacy_done_receipt_survives_upgrade_until_its_reason_changes(self):
        decision=self.apply([dict(op='create',id='d',body=dict(type='Decision',title='Legacy reason',description='SQLite'))])['temp_ids']['d'];self.apply([dict(op='link',origin=self.task,target=decision,kind='required_by')])
        original=self.s._save
        def legacy_save(scope,project,action,value):
            if action=='task_stage' and value['stage']=='Done':value=dict(value);value.pop('basis_version');value['format']='decivora-task-stage-1';value['completion_basis']=self.s._completion_basis(project,self.task,legacy=True)
            return original(scope,project,action,value)
        self.s._save=legacy_save;self.complete();self.s._save=original
        self.assertEqual(self.s.view(self.owner,'p',self.task)['stage'],'Done');downstream=self.create('Downstream');self.apply([dict(op='link',origin=downstream,target=self.task,kind='depends_on')]);self.assertEqual(self.s.view(self.owner,'p',self.task)['stage'],'Done')
        self.apply([dict(op='update',id=decision,base_version=1,body=dict(type='Decision',title='Changed reason',description='Changed architecture'))]);self.assertEqual(self.s.view(self.owner,'p',self.task)['stage'],'Awaiting Verification')
