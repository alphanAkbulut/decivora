#!/usr/bin/env python3
"""Emit a 14-criterion template or validate an explicit evidence inventory offline."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.analytics.acceptance_inventory import assess,template
from packages.domain.source_event import ContractError

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args(argv)
    try:
        if a.manifest:
            if a.manifest.is_symlink() or a.manifest.stat().st_size>65536:raise ValueError()
            result=assess(a.root,json.loads(a.manifest.read_text()))
        else:result=template()
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (ContractError,OSError,ValueError):print('{"error":"acceptance_inventory_unavailable"}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
