"""One executable integrated core flow using only an isolated synthetic workspace."""
import json
from pathlib import Path
import tempfile
from packages.storage.workspace import Workspace
from packages.domain.project_binding import SessionKey
from packages.domain.source_event import validate_source_event
from packages.reconciliation.core import reconcile
from packages.capture.extraction import validate_candidates,lexical_context
from packages.impact.graph import rationale


def run_demo():
    root=Path(__file__).resolve().parents[2]
    with tempfile.TemporaryDirectory(prefix='decivora-core-demo-') as directory:
        path=Path(directory)/'workspace.sqlite'
        with Workspace(path,'workspace_demo',owner='owner_demo') as core:
            a=core.authority
            a.replace_grant(a.issue_scope('owner_demo'),'owner_demo',kind='human',readable=frozenset({'p1','p2'}),writable=frozenset({'p1','p2'}),active=True,base_revision=1)
            owner=a.issue_scope('owner_demo')
            core.create_project(owner,'p1','Aynı isim');core.create_project(owner,'p2','Aynı isim')
            key=SessionKey('manual','account_demo','session_fixture','epoch_demo')
            event=validate_source_event(dict(json.loads((root/'examples/runtime/source-event.json').read_text()),project_id='p1'))
            core.bind(owner,key,'p1',0)
            receipt=core.receive(owner,key,event,1)
            duplicate=core.receive(owner,key,event,1)
            lease=core.lease(owner,'p1',now=0)
            # Explicitly structured/manual proposal: no model inference claimed.
            body=dict(type='Task',title='Yerel kaynak kaydı',description='Kaynak referansını koru')
            other=dict(type='Requirement',title='Kayıpsız alım',description='Alındı denilen veri kalıcı olmalı')
            ops=[dict(op='create',id='task',body=body,source_seq=receipt['seq']),
                 dict(op='create',id='requirement',body=other,source_seq=receipt['seq']),
                 dict(op='link',origin='task',target='requirement',kind='required_by')]
            plan=core.plan(owner,'p1','manual_change',ops);approval=core.approve(owner,plan)
            applied=core.apply(owner,plan,approval)
            core.finish(owner,lease,dict(change=applied,method='manual_structured'),now=1)
            before=core.projection_digest(owner,'p1')
            replay=core.replay(owner,'p1')
            records=core.records(owner,'p1')['records']
            comparison=reconcile(dict(**body,source_ref='receipt_demo',intent='proposed'),records)
            context=lexical_context(records,'kaynak')
            graph=core.graph(owner,'p1')
            preserved=rationale({'any':[dict(ref='old',revision=1),dict(ref='new',revision=1)]},
                {'old':dict(revision=1,valid=False),'new':dict(revision=1,valid=True)})
            manifest=core.backup(owner,Path(directory)/'backup.sqlite')
            with Workspace.restore(Path(directory)/'backup.sqlite',Path(directory)/'restore.sqlite',manifest) as restored:
                restore_matches=restored.projection_digest(restored.authority.issue_scope('owner_demo'),'p1')==before
            result=dict(status='passed_integrated_local_core',profile='synthetic_manual_only',
                durable_receipt=receipt['durable_receipt'],retry_same_receipt=receipt['seq']==duplicate['seq'],
                processing_frontier=core.frontier(owner,key,'p1'),atomic_records=len(records),events=replay['events'],
                replay_matches=before==replay['digest'],restore_matches=restore_matches,
                reconciliation=comparison['recommendation'],context_records=len(context['records']),
                graph_revision=graph.revision,alternative_rationale_preserved=preserved,
                real_semantic_extraction=False,provider_capture=False,human_login=False,model_dispatches=0)
    if not all(result[k] for k in ('durable_receipt','retry_same_receipt','replay_matches','restore_matches','alternative_rationale_preserved')):
        raise RuntimeError('Integrated core demonstration failed.')
    return result
