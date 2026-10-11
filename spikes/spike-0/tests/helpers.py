import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from spike0 import db  # noqa: E402
from spike0.pipeline import save_bindings  # noqa: E402

FIX = os.path.join(ROOT, "fixtures")


def user(uuid, sid, cwd, text, ts="2026-10-10T10:00:00.000Z"):
    return {"type": "user", "uuid": uuid, "parentUuid": None, "sessionId": sid, "cwd": cwd,
            "timestamp": ts, "isSidechain": False, "version": "2.1.300",
            "message": {"role": "user", "content": text}}


def assistant(uuid, sid, cwd, text, ts="2026-10-10T10:00:01.000Z"):
    return {"type": "assistant", "uuid": uuid, "parentUuid": None, "sessionId": sid, "cwd": cwd,
            "timestamp": ts, "isSidechain": False, "version": "2.1.300",
            "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


def write_jsonl(path, recs, partial_tail=None):
    with open(path, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        if partial_tail:
            f.write(partial_tail)


class SpikeCase(unittest.TestCase):
    """Her test izole bir veri dizini ve tmp dizinleri kullanir."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="spike0-")
        self.data = os.path.join(self.tmp, "data")
        os.environ["SPIKE0_DATA"] = self.data
        self.conn = db.connect()
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        self.conn.close()
        os.environ.pop("SPIKE0_DATA", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def bind(self, *pairs):
        save_bindings([{"path": p, "project": n} for p, n in pairs])

    def mkdir(self, *parts):
        p = os.path.join(self.tmp, *parts)
        os.makedirs(p, exist_ok=True)
        return p

    def register(self, sid, tpath, cwd):
        self.conn.execute(
            "INSERT OR REPLACE INTO sessions(session_id,transcript_path,cwd,first_seen,last_hook_at) "
            "VALUES(?,?,?,?,?)", (sid, tpath, cwd, 0, 0))

    def q(self, sql, *a):
        return self.conn.execute(sql, a).fetchall()
