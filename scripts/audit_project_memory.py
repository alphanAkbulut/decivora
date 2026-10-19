#!/usr/bin/env python3
"""Explicit scoped, read-only structural report; never reads chats or calls a model."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.storage.workspace import Workspace
from packages.reconciliation.orphan_audit import OrphanAudit
from packages.domain.source_event import ContractError

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for f in ('db','workspace','principal','project'):p.add_argument('--'+f,required=True)
    a=p.parse_args(argv)
    if not Path(a.db).is_file() or Path(a.db).is_symlink():p.error('Select an existing regular workspace database.')
    try:
        with Workspace(a.db,a.workspace) as core:result=OrphanAudit(core).run(core.authority.issue_scope(a.principal),a.project)
        print(json.dumps(result));return 0
    except (ContractError,OSError):print('{"status":"audit_unavailable"}');return 1
if __name__=='__main__':raise SystemExit(main())
