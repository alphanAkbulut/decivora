#!/usr/bin/env python3
"""Explicit local-owner Claude hook bridge. Never edits settings or reads transcripts."""
import argparse,json,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.capture.claude_code.hooks import ClaudeHookCapture,MAX_PACKET_BYTES
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('db','workspace','principal','project','capture-id'):p.add_argument('--'+name,required=True)
    p.add_argument('--mode',choices=('connect','collect','disconnect'),required=True)
    p.add_argument('--session-id');p.add_argument('--cwd');p.add_argument('--provider-version');p.add_argument('--consent',action='store_true');p.add_argument('--delivery-id')
    a=p.parse_args(argv)
    if not Path(a.db).is_file() or Path(a.db).is_symlink():p.error('Select an existing regular workspace database.')
    if a.mode=='connect' and not all((a.session_id,a.cwd,a.provider_version,a.consent)):p.error('Connect requires explicit session, cwd, provider version and consent.')
    try:
        raw=sys.stdin.buffer.read(MAX_PACKET_BYTES+1) if a.mode=='collect' else None
        with Workspace(a.db,a.workspace) as core:
            scope=core.authority.issue_scope(a.principal);adapter=ClaudeHookCapture(core)
            if a.mode=='connect':result=adapter.connect(scope,a.project,capture_id=a.capture_id,session_id=a.session_id,cwd=a.cwd,provider_version=a.provider_version,consent=a.consent)
            elif a.mode=='disconnect':result=adapter.disconnect(scope,a.project,capture_id=a.capture_id)
            else:result=adapter.collect(scope,a.project,capture_id=a.capture_id,delivery_id=a.delivery_id or 'delivery_'+uuid.uuid4().hex,raw=raw)
        # Hook stdout would be injected into the host context. Collection is silent.
        if a.mode!='collect':print(json.dumps(result))
        return 0
    except (ContractError,OSError):
        print('decivora_claude_capture_failed',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
