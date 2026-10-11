"""Run the controlled typed-input experiment; never call a model or a provider."""
import hashlib
import json
import tempfile
from pathlib import Path
from chain import Chain, digest, read_target


def run():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);c=Chain(root/'events.db')
        def send(cmd,payload,actor='human'):
            rev=c.snapshot()['revision']
            return c.dispatch(cmd,payload,actor,rev,str(rev)+'-'+cmd)
        try:
            send('seed',dict(decision='markdown',active=['markdown','security'],
                 tasks={'sync':dict(expr='markdown',status='todo'),
                 'export':dict(expr={'any':['markdown','sqlite']},status='todo'),
                 'watch':dict(expr=None,status='todo')},criteria=['migration','rollback']))
            send('ask',dict(question_id='Q_STORE',option_revision=1,
                           options={'A':'markdown','B':'sqlite'},source_session='chat-1'))
            send('answer',dict(question_id='Q_STORE',option_revision=1,option='B',source_session='chat-2'))
            preview=c.preview()
            send('impact',dict(preview_digest=preview['preview_digest'],
                              actions={'sync':'obsolete','export':'retained','watch':'review'}))
            content=b'SQLite migration document';(root/'bundle.md').write_bytes(content)
            artifact=dict(artifact_revision=2,sha256=hashlib.sha256(content).hexdigest(),ref='fixture-ref-2',path='bundle.md')
            send('expect',artifact)
            send('observe',read_target(root/'bundle.md',2,'old-ref','bundle.md'),'observer')
            old_status=c.snapshot()['observation']['status']
            send('observe',read_target(root/'bundle.md',2,'fixture-ref-2','bundle.md'),'observer')
            send('verify',dict(artifact_revision=2,criteria={'rollback':'passed'}),'verifier')
            partial=c.snapshot()['verified']
            send('verify',dict(artifact_revision=2,criteria={'migration':'passed'}),'verifier')
            state=c.snapshot()
            backup=c.backup(root/'backup.db')
            return dict(kind='typed_fixture_decision_chain',result='passed',
                automatic_semantic_extraction=False,real_host=False,production_runtime=False,
                oracle_status='synthetic_authored_pending_human_review',
                current_decision=state['decision'],impact=preview['impact'],
                old_ref_status=old_status,partial_ac_verified=partial,
                all_fixture_ac_verified=state['verified'],backup_projection_digest=backup,
                projection_digest=digest(state),event_count=state['revision'],
                external_dispatches=0,additional_paid_model_dispatches=0,
                limitations=['trusted fixture roles are not IAM','typed inputs are not extracted chat',
                             'fixture ref is not a GitHub observation','verifier outcomes are controlled synthetic inputs'])
        finally:c.close()


if __name__=='__main__':
    print(json.dumps(run(),ensure_ascii=False,indent=2))
