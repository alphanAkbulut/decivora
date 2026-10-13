"""Explicit cancellation and compensating reopening, preserving relationships/history."""
from pathlib import Path
import tempfile
from packages.domain.review import ReviewService
from packages.storage.workspace import Workspace

def run_demo():
    with tempfile.TemporaryDirectory(prefix='decivora-lifecycle-') as directory:
        with Workspace(Path(directory)/'core.sqlite','workspace',owner='owner') as core:
            a=core.authority;a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'project'}),writable=frozenset({'project'}),active=True,base_revision=1);owner=a.issue_scope('owner');core.create_project(owner,'project','Synthetic task lifecycle')
            task=dict(type='Task',title='Sync',description='History preserved')
            ops=[dict(op='create',id='d',body=dict(type='Decision',title='Storage',description='Manual')),dict(op='create',id='t',body=task),dict(op='link',origin='t',target='d',kind='required_by')]
            plan=core.plan(owner,'project','seed',ops);ids=core.apply(owner,plan,core.approve(owner,plan))['temp_ids'];d,t=ids['d'],ids['t'];service=ReviewService(core)
            def change(run,state,version):
                core.impact_preview(owner,'project',run,dict(record=d,version=1,kind='decision_superseded'),{t:dict(version=version,required_when=dict(any=[dict(ref=d,revision=1)]),historically_completed=False,replacement=None)},{d:dict(revision=1,valid=state=='cancelled')},{d:dict(revision=1,valid=state=='todo')})
                groups=[dict(id='lifecycle',depends_on=[],records=[t],operations=[dict(op='task_lifecycle',id=t,base_version=version,state=state,reason='Explicit approved synthetic rationale',impact_run=run)])]
                service.create(owner,'project',run+'_review',run,groups);service.select(owner,'project',run+'_review',run+'_selection',['lifecycle']);token=service.approve(owner,'project',run+'_selection');return service.apply(owner,'project',run+'_selection',token)
            change('cancel','cancelled',1);cancelled=core.task_history(owner,'project',t)['execution']
            edge_preserved=core.db.execute('SELECT state FROM edges').fetchone()[0]=='asserted'
            change('reopen','todo',2);history=core.task_history(owner,'project',t);before=core.projection_digest(owner,'project');replay=core.replay(owner,'project')
            result=dict(status='passed_manual_task_lifecycle',cancelled_state=cancelled,current_state=history['execution'],history_states=[row['state'] for row in history['events']],relationship_preserved=edge_preserved,replay_matches=replay['digest']==before,task_deleted=False,task_completion_verified=False,model_dispatches=0,human_login=False)
            if result['history_states']!=['cancelled','todo'] or not edge_preserved or not result['replay_matches']:raise RuntimeError('Lifecycle demonstration failed.')
            return result
