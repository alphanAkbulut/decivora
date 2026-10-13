"""Optional real-browser localization QA. Requires Node, Playwright and a browser."""
import json, os, subprocess, sys, tempfile, threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests/runtime')]
from apps.local_ui.server import make_server
from test_conversations import Extractor

def main():
    with tempfile.TemporaryDirectory() as directory:
        server=make_server(Path(directory)/'fixture.sqlite',extractor=Extractor())
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        config=Path(directory)/'session.json'
        config.write_text(json.dumps(dict(origin=server.origin,bootstrap=server.app.bootstrap)));config.chmod(0o600)
        env=dict(os.environ,DECIVORA_UI_TEST_CONFIG=str(config),DECIVORA_SCREENSHOT_DIR=os.environ.get('DECIVORA_SCREENSHOT_DIR',directory))
        try:return subprocess.run([env.get('DECIVORA_NODE','node'),str(ROOT/env.get('DECIVORA_UI_TEST_SCRIPT','tests/ui-localization.cjs'))],env=env).returncode
        finally:server.shutdown();server.server_close();thread.join()
if __name__=='__main__':raise SystemExit(main())
