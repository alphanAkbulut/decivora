import json
import sys

if sys.version_info[:2] != (3, 12):
    print(json.dumps(dict(status='rejected', error=dict(code='unsupported_python',
          message='This development runtime requires Python 3.12.'))), file=sys.stderr)
    raise SystemExit(2)

from .runtime import main

raise SystemExit(main())
