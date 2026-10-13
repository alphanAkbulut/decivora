"""Six-case existing impact oracle through a real isolated Workspace preview."""
import json
from pathlib import Path
import tempfile
from packages.storage.workspace import Workspace


def run_demo():
    source=json.loads((Path(__file__).resolve().parents[2]/'examples/impact-scenario.json').read_text())
    with tempfile.TemporaryDirectory(prefix='decivora-impact-demo-') as directory:
        with Workspace(Path(directory)/'impact.sqlite','workspace',owner='owner') as core:
            a=core.authority;a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'project'}),writable=frozenset({'project'}),active=True,base_revision=1)
            owner=a.issue_scope('owner');core.create_project(owner,'project','Synthetic storage change')
            names=list(source['facts_after'])+[r['id'] for r in source['records']]
            operations=[dict(op='create',id=name,body=dict(type='Task' if name.startswith('T') else 'Decision' if name.startswith('DEC') else 'Requirement',title=name,description='Explicit synthetic fixture')) for name in names]
            plan=core.plan(owner,'project','seed',operations)
            ids=core.apply(owner,plan,core.approve(owner,plan))['temp_ids']
            def expression(value):
                if type(value) is str:return dict(ref=ids[value],revision=1)
                if type(value) is dict:return {k:[expression(v) for v in rows] for k,rows in value.items()}
                return None
            notes={ids[r['id']]:dict(version=1,required_when=expression(r['required_when']),historically_completed=r.get('verification')=='passed',replacement=ids['DEC_DB'] if r['id']=='T2' else None) for r in source['records']}
            before={ids[k]:dict(revision=1,valid=True) for k in source['facts_after']}
            after={ids[k]:dict(revision=1,valid=v) for k,v in source['facts_after'].items()}
            previous=core.projection_digest(owner,'project')
            result=core.impact_preview(owner,'project','impact_storage',dict(record=ids['DEC_MD'],version=1,kind='decision_superseded'),notes,before,after)
            reverse={v:k for k,v in ids.items()};cases={reverse[r['record']]:r['action'] for r in result['proposals'] if reverse[r['record']].startswith('T')}
            expected=dict(T1='review',T2='update',T3='obsolete_candidate',T4='keep',T5='update',T6='review')
            unchanged=core.projection_digest(owner,'project')==previous
            if cases!=expected or not unchanged:raise RuntimeError('Impact oracle or mutation guard failed.')
            backup=Path(directory)/'backup.sqlite';manifest=core.backup(owner,backup)
            with Workspace.restore(backup,Path(directory)/'restore.sqlite',manifest) as restored:
                retained=restored.impact_run(restored.authority.issue_scope('owner'),'project','impact_storage')['result']==result
            return dict(status='passed_manual_impact_preview',cases=cases,coverage=result['coverage'],frontier=result['frontier'],domain_unchanged=unchanged,restore_matches=retained,canonical_mutations_from_preview=0,model_dispatches=0,real_semantic_extraction=False,task_completion_verified_by_demo=False,input_method='explicit_synthetic_manual_metadata',task_changes_applied=False)
