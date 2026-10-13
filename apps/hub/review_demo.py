"""No-text local selection → separate approval → atomic apply demonstration."""
from pathlib import Path
import tempfile
from packages.domain.review import ReviewService
from packages.storage.workspace import Workspace

def run_demo():
    with tempfile.TemporaryDirectory(prefix='decivora-review-') as directory:
        with Workspace(Path(directory)/'core.sqlite','workspace',owner='owner') as core:
            a=core.authority;a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'project'}),writable=frozenset({'project'}),active=True,base_revision=1);owner=a.issue_scope('owner');core.create_project(owner,'project','Manual review')
            task=dict(type='Task',title='Sync',description='Before')
            plan=core.plan(owner,'project','seed',[dict(op='create',id='d',body=dict(type='Decision',title='Storage',description='Manual')),dict(op='create',id='t',body=task)])
            ids=core.apply(owner,plan,core.approve(owner,plan))['temp_ids'];d,t=ids['d'],ids['t']
            core.impact_preview(owner,'project','impact',dict(record=d,version=1,kind='decision_superseded'),{t:dict(version=1,required_when=dict(any=[dict(ref=d,revision=1)]),historically_completed=False,replacement=None)},{d:dict(revision=1,valid=True)},{d:dict(revision=1,valid=False)})
            service=ReviewService(core)
            groups=[dict(id='scope_update',depends_on=[],records=[t],operations=[dict(op='update',id=t,base_version=1,body=dict(task,description='After explicitly selected scope change'))])]
            service.create(owner,'project','review','impact',groups)
            compared=service.compare(owner,'project','review');before=core.projection_digest(owner,'project')
            selected=service.select(owner,'project','review','selection',['scope_update'])
            token=service.approve(owner,'project','selection')
            no_change_before_apply=before==core.projection_digest(owner,'project')
            applied=service.apply(owner,'project','selection',token)
            retry=service.apply(owner,'project','selection',token)
            after=core.projection_digest(owner,'project')
            replay=core.replay(owner,'project')
            result=dict(status='passed_local_review_kernel',selection_groups=selected['groups'],compare_mutations=compared['canonical_mutations'],unchanged_until_separate_apply=no_change_before_apply,applied_events=len(applied['event_sequences']),retry_same_result=retry==applied,replay_matches=replay['digest']==after,model_dispatches=0,human_login=False,task_cancellation_implemented=False,task_completion_verified=False)
            if not all(result[k] for k in ('unchanged_until_separate_apply','retry_same_result','replay_matches')):raise RuntimeError('Review demo failed.')
            return result
