#!/usr/bin/env python3
"""Finite read of explicitly selected Codex threads; no model or chat creation."""
import argparse,json,sys,time
from contextlib import ExitStack
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from packages.capture.codex.project_pipeline import CodexProjectPipeline
from packages.capture.codex.read_client import ReadOnlyAppServer
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace
from packages.operations.local import LocalOperations,identity_from_scope


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('db','workspace','principal','project','provider-version','codex-executable'):p.add_argument('--'+name,required=True)
    p.add_argument('--selection',action='append',required=True,help='Exact CAPTURE_ID=THREAD_ID; repeat only for authorized chats.')
    p.add_argument('--codex-home');p.add_argument('--consent',action='store_true')
    p.add_argument('--polls',type=int,default=1);p.add_argument('--interval',type=float,default=2);p.add_argument('--turn-limit',type=int,default=10)
    a=p.parse_args(argv)
    if not a.consent:p.error('Explicit consent for every selected conversation required.')
    if not 1<=len(a.selection)<=4 or not 1<=a.polls<=300 or not .25<=a.interval<=60 or not 1<=a.turn_limit<=10:p.error('Bounded selections, polls, interval and turns required.')
    pairs=[]
    try:
        for selection in a.selection:
            if selection.count('=')!=1:raise ValueError()
            cid,tid=selection.split('=');identifier(cid);identifier(tid);pairs.append((cid,tid))
        if len({c for c,t in pairs})!=len(pairs) or len({t for c,t in pairs})!=len(pairs):raise ValueError()
    except (ValueError,ContractError):p.error('Unique exact CAPTURE_ID=THREAD_ID selections required.')
    db=Path(a.db)
    if not db.is_file() or db.is_symlink():p.error('Select an existing regular TEST workspace database.')
    try:
        with Workspace(db,a.workspace) as core,ExitStack() as stack:
            scope=core.authority.issue_scope(a.principal);pipe=CodexProjectPipeline(core)
            for cid,tid in pairs:
                pipe.capture.connect(scope,a.project,capture_id=cid,thread_id=tid,provider_version=a.provider_version,consent=True)
            selections=[dict(capture_id=cid,client=stack.enter_context(ReadOnlyAppServer(a.codex_executable,tid,cwd=ROOT,codex_home=a.codex_home))) for cid,tid in pairs]
            ops=LocalOperations(db.with_suffix('.operations.sqlite'))
            for poll in range(a.polls):
                started=time.monotonic();run=ops.begin(a.project,'native_capture',identity=identity_from_scope(core,scope,a.project))
                try:
                    with ops.span(run,1,'capture','execute_command'):
                        result=pipe.tick_selected(scope,a.project,selections=selections,turn_limit=a.turn_limit)
                    if result['errors']:
                        ops.finish(run,started,ContractError('codex_read_failed','Selected capture partial'))
                        print(json.dumps(dict(status='partial',result=result,model_calls=0)),flush=True);return 1
                except Exception as error:ops.finish(run,started,error);raise
                ops.finish(run,started)
                print(json.dumps(dict(status='captured',result=result,model_calls=0)),flush=True)
                if poll+1<a.polls:time.sleep(a.interval)
        return 0
    except KeyboardInterrupt:return 130
    except (ContractError,OSError) as error:
        print(json.dumps(dict(status='Capture stopped',code=error.code if isinstance(error,ContractError) else 'codex_host_unavailable',model_calls=0)))
        return 1

if __name__=='__main__':raise SystemExit(main())
