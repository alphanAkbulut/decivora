#!/usr/bin/env python3
"""Read one selected Codex thread into an existing project; no agent/model start."""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from packages.capture.codex.app_server import CodexAppServerCapture
from packages.capture.codex.read_client import ReadOnlyAppServer
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ('db','workspace','principal','project','capture-id','thread-id','provider-version','codex-executable'):
        parser.add_argument('--'+field,required=True)
    parser.add_argument('--codex-home')
    parser.add_argument('--consent',action='store_true')
    parser.add_argument('--polls',type=int,default=1)
    parser.add_argument('--turn-limit',type=int,default=10)
    parser.add_argument('--interval',type=float,default=2)
    args = parser.parse_args(argv)
    if not args.consent: parser.error('Explicit selected-thread local capture consent is required.')
    if not 1<=args.polls<=300 or not 0.25<=args.interval<=60: parser.error('Bounded polls/interval required.')
    if not 1<=args.turn_limit<=10: parser.error('Turn limit must be between 1 and 10.')
    db = Path(args.db)
    if not db.is_file() or db.is_symlink(): parser.error('Select an existing regular workspace database.')
    try:
        with Workspace(db,args.workspace) as core:
            scope = core.authority.issue_scope(args.principal)
            adapter = CodexAppServerCapture(core)
            adapter.connect(scope,args.project,capture_id=args.capture_id,thread_id=args.thread_id,
                            provider_version=args.provider_version,consent=args.consent)
            with ReadOnlyAppServer(args.codex_executable,args.thread_id,cwd=ROOT,codex_home=args.codex_home) as client:
                for poll in range(args.polls):
                    receipt = adapter.collect(scope,args.project,capture_id=args.capture_id,client=client,limit=args.turn_limit)
                    print(json.dumps({k:v for k,v in receipt.items() if k!='fingerprints'}),flush=True)
                    if poll+1<args.polls: time.sleep(args.interval)
        return 0
    except KeyboardInterrupt: return 130
    except (ContractError,OSError) as error:
        print(json.dumps(dict(status='Capture stopped',code=error.code if isinstance(error,ContractError) else 'codex_host_unavailable',reason='Selected host read or capture contract failed; no automatic retry.')))
        return 1


if __name__=='__main__': raise SystemExit(main())
