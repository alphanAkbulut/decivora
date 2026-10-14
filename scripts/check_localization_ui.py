"""Optional real-browser localization QA. Requires Node, Playwright and a browser."""
import json, os, subprocess, sys, tempfile, threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests/runtime')]
from apps.local_ui.server import make_server
from test_conversations import Extractor

def main():
    with tempfile.TemporaryDirectory() as directory:
        file_root=None
        if os.environ.get('DECIVORA_FILE_UI_FIXTURE')=='1':
            file_root=Path(directory)/'approved-root';file_root.mkdir();(file_root/'output.txt').write_bytes(b'file-check-fixture')
        server=make_server(Path(directory)/'fixture.sqlite',extractor=Extractor(),verification_root=file_root)
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
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        config=Path(directory)/'session.json'
        config.write_text(json.dumps(dict(origin=server.origin,bootstrap=server.app.bootstrap,file_fixture=str(file_root) if file_root else None)));config.chmod(0o600)
        env=dict(os.environ,DECIVORA_UI_TEST_CONFIG=str(config),DECIVORA_SCREENSHOT_DIR=os.environ.get('DECIVORA_SCREENSHOT_DIR',directory))
        try:return subprocess.run([env.get('DECIVORA_NODE','node'),str(ROOT/env.get('DECIVORA_UI_TEST_SCRIPT','tests/ui-localization.cjs'))],env=env).returncode
        finally:server.shutdown();server.server_close();thread.join()
if __name__=='__main__':raise SystemExit(main())
