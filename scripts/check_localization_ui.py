"""Optional real-browser localization QA. Requires Node, Playwright and a browser."""
import json, os, subprocess, sys, tempfile, threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests/runtime')]
from apps.local_ui.server import make_server
from test_conversations import Extractor,install_fixture_analysis_grants

def main():
    with tempfile.TemporaryDirectory() as directory:
        file_root=None
        if os.environ.get('DECIVORA_FILE_UI_FIXTURE')=='1':
            file_root=Path(directory)/'approved-root';file_root.mkdir();(file_root/'output.txt').write_bytes(b'file-check-fixture')
        server=make_server(Path(directory)/'fixture.sqlite',extractor=None if os.environ.get('DECIVORA_SOURCE_PAGES_UI_FIXTURE')=='1' or os.environ.get('DECIVORA_DIALOGUE_UI_FIXTURE')=='1' or os.environ.get('DECIVORA_OPERATIONS_UI_FIXTURE')=='1' else Extractor(),verification_root=file_root,environment='test' if os.environ.get('DECIVORA_OPERATIONS_UI_FIXTURE')=='1' else 'local')
        if os.environ.get('DECIVORA_NATIVE_UI_FIXTURE')=='1':
            from contextlib import contextmanager
            from packages.capture.codex.ui_connection import NativeConnector
            @contextmanager
            def native_client(thread):
                class Client:
                    def read_turns(self,thread_id,limit):
                        return dict(data=[dict(id='native_ui_turn',status='completed',items=[dict(id='native_ui_message',type='userMessage',content=[dict(type='text',text='Synthetic selected chat task; not started.')])])],nextCursor=None)
                yield Client()
            server.app.native_connector=NativeConnector('fixture','host_ui_fixture',native_client)
        if os.environ.get('DECIVORA_ACTIVATION_UI_FIXTURE')=='1':
            import time
            from packages.capture.conversations import ConversationService
            from packages.capture.dialogue_review import DialogueReviewService
            from packages.capture.granted_extractors import GrantedResponsesFactory
            from packages.capture.model_activation import ManagedResponsesFactory
            def send(payload):
                request=json.loads(payload['input']);source=request['source']
                return dict(status='completed',usage=dict(total_tokens=15),output=[dict(type='message',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(dict(source_id=source['id'],source_sha256=source['sha256'],context_sha256=request['context_sha256'],coverage='partial',candidates=[],status_changes=[])))])])
            entries=[]
            with server.app.core() as core:
                owner=core.authority.issue_scope('local_owner');service=ConversationService(core)
                core.create_budget(owner,'personal','ui_fixture_budget',24000)
                for i in range(2):
                    source=service.ingest(owner,'personal',text='Synthetic worker source '+str(i))
                    prepared=DialogueReviewService(core).prepare(owner,'personal',source_id=source['id'])
                    grant=service.authorize_analysis(owner,'personal',source_id=source['id'],key='ui_grant_'+str(i),root_run='ui_fixture_budget',reserved_tokens=12000,provider='OpenAI Responses configured transport',model='fixture',max_output_tokens=2000,expires_at=int(time.time())+3600,reason='Synthetic no-network browser fixture',context_sha256=prepared['context_sha256'])
                    entries.append((grant,send))
            server.app.extractor=None
            server.app.extractor_factory=ManagedResponsesFactory(GrantedResponsesFactory(entries),'activation_ui_fixture')
        if os.environ.get('DECIVORA_SOURCE_PAGES_UI_FIXTURE')=='1':
            from packages.capture.conversations import ConversationService
            with server.app.core() as core:
                owner=core.authority.issue_scope('local_owner')
                for i in range(35):ConversationService(core).ingest(owner,'personal',text='Synthetic paged source '+str(i))
        if os.environ.get('DECIVORA_RATIONALE_UI_FIXTURE')=='1':
            with server.app.core() as core:
                owner=core.authority.issue_scope('local_owner')
                ops=[dict(op='create',id=k,body=dict(type='Task' if k=='task' else 'Decision',title=k,description='Synthetic rationale fixture')) for k in ('task','A','B')]+[dict(op='link',origin='task',target=k,kind='required_by') for k in ('A','B')]
                plan=core.plan(owner,'personal','rationale_fixture',ops);core.apply(owner,plan,core.approve(owner,plan))
        if os.environ.get('DECIVORA_DIALOGUE_UI_FIXTURE')=='1':
            from packages.domain.questions import QuestionService
            with server.app.core() as core:
                owner=core.authority.issue_scope('local_owner')
                plan=core.plan(owner,'personal','dialogue_context_fixture',[dict(op='create',id='d',body=dict(type='Decision',title='Existing storage decision fixture',description='SQLite chosen for local operation')),dict(op='create',id='d2',body=dict(type='Decision',title='Alternative storage fixture',description='Alternative recorded storage choice'))])
                core.apply(owner,plan,core.approve(owner,plan))
                QuestionService(core).present(owner,'personal',question='Q_CONTEXT',base_revision=0,text='Which scope follows?',options=[dict(id='a',label='Keep scope'),dict(id='b',label='Review scope')])
        if os.environ.get('DECIVORA_IMPACT_UI_FIXTURE')=='1':
            with server.app.core() as core:
                owner=core.authority.issue_scope('local_owner')
                plan=core.plan(owner,'personal','impact_fixture',[dict(op='create',id='d',body=dict(type='Decision',title='Storage decision fixture',description='Synthetic')),dict(op='create',id='t',body=dict(type='Task',title='Affected task fixture',description='Synthetic')),dict(op='link',origin='t',target='d',kind='required_by')])
                core.apply(owner,plan,core.approve(owner,plan))
        if os.environ.get('DECIVORA_MCP_UI_FIXTURE')=='1':
            from packages.mcp.server import Server
            with server.app.core() as core:
                a=core.authority;a.replace_grant(a.issue_scope('local_owner'),'fixture_agent',kind='agent',readable=frozenset({'personal'}),writable=frozenset({'personal'}),active=True,base_revision=a.revision());rev=core.project(a.issue_scope('local_owner'),'personal')['knowledge_revision']
            Server(server.app.path,'local_ui_workspace','fixture_agent').call('submit_changeset',dict(project_id='personal',key='fixture_agent_draft',base_revision=rev,operations=[dict(op='create',id='t',body=dict(type='Task',title='Agent UI fixture',description='Separate approval and application'))]))
        if os.environ.get('DECIVORA_PROJECT_UI_FIXTURE')=='1':
            with server.app.core() as core:
                a=core.authority;a.replace_grant(a.issue_scope('local_owner'),'local_owner',kind='human',readable=frozenset({'personal','other'}),writable=frozenset({'personal','other'}),active=True,base_revision=a.revision());core.create_project(a.issue_scope('local_owner'),'other','Other fixture project')
        if os.environ.get('DECIVORA_COVERAGE_UI_FIXTURE')=='1':
            original_extract=Extractor.__call__
            def partial_extract(self,source):
                result=original_extract(self,source);result['coverage']='partial';return result
            Extractor.__call__=partial_extract
        if os.environ.get('DECIVORA_AGED_BLOCKER_UI_FIXTURE')=='1':
            import time
            from unittest.mock import patch
            for title,days in [('Old blocker fixture',8),('Recent blocker fixture',2)]:
                server.app.command(dict(action='create_task',title=title,description='Synthetic age display fixture'))
                task=next(t for t in server.app.state()['tasks'] if t['body']['title']==title)
                recorded=time.time()-days*86400
                with patch('time.time',return_value=recorded):
                    server.app.command(dict(action='task_blocker',task=task['id'],task_version=task['version'],base_revision=0,blocked=True,reason='Fixture permission pending',next_action='Review permission'))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        config=Path(directory)/'session.json'
        config.write_text(json.dumps(dict(origin=server.origin,bootstrap=server.app.bootstrap,file_fixture=str(file_root) if file_root else None)));config.chmod(0o600)
        env=dict(os.environ,DECIVORA_UI_TEST_CONFIG=str(config),DECIVORA_SCREENSHOT_DIR=os.environ.get('DECIVORA_SCREENSHOT_DIR',directory))
        try:return subprocess.run([env.get('DECIVORA_NODE','node'),str(ROOT/env.get('DECIVORA_UI_TEST_SCRIPT','tests/ui-localization.cjs'))],env=env).returncode
        finally:server.shutdown();server.server_close();thread.join()
if __name__=='__main__':
    with install_fixture_analysis_grants():raise SystemExit(main())
