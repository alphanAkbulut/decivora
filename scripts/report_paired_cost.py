#!/usr/bin/env python3
"""Compare explicit paired synthetic/pilot measurements without model calls."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.analytics.paired_cost import compare
from packages.domain.source_event import ContractError

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('measurements',type=Path);a=p.parse_args(argv)
    try:
        if a.measurements.is_symlink() or a.measurements.stat().st_size>2097152:raise ValueError()
        print(json.dumps(compare(json.loads(a.measurements.read_text())),indent=2));return 0
    except (ContractError,OSError,ValueError):print('{"error":"paired_comparison_unavailable"}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
