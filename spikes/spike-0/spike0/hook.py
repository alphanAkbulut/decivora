"""Claude Code hook alicisi.

KURALLAR: stdout'a ASLA yazma (SessionStart/UserPromptSubmit'te stdout Claude'un
baglamina girer). Her durumda cikis kodu 0. Hata -> data/errors.log.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

from .db import connect, data_dir, log_error, meta_incr
from .pipeline import process_session, resolve_project
from .redact import redact
from .transcript import tail_assistant_texts

HANDLED = {"SessionStart", "UserPromptSubmit", "Stop", "SessionEnd"}
BUDGET_S = 1.5


def _norm(s):
    return " ".join((s or "").split())


def prepare(payload):
    """Minimal durable receipt; prompt/transcript text is not spooled."""
    ev, sid = payload.get('hook_event_name'), payload.get('session_id')
    if ev not in HANDLED or not isinstance(sid, str) or not sid:
        return None
    cwd, path = payload.get('cwd'), payload.get('transcript_path')
    identity = [os.path.realpath(cwd) if cwd else None, os.path.realpath(path) if path else None]
    try:
        st = os.stat(path)
        identity += [st.st_dev, st.st_ino]
    except (OSError, TypeError):
        identity += [None, None]
    source = hashlib.sha256(json.dumps(identity).encode()).hexdigest()
    key = hashlib.sha256(json.dumps([sid, source]).encode()).hexdigest()
    answer = _norm(redact(payload.get('last_assistant_message') or ''))
    return dict(hook_event_name=ev, session_id=key, transport_session_id=sid,
                source_identity=source, cwd=cwd, transcript_path=path,
                prompt_id=payload.get('prompt_id'), source=payload.get('source'),
                body_digest=hashlib.sha256((payload.get('prompt') or payload.get('last_assistant_message') or '').encode()).hexdigest(),
                assistant_digest=hashlib.sha256(answer.encode()).hexdigest() if answer else None)


def recover_receipts():
    """Retry persisted receipts explicitly; no model or host execution."""
    count = 0
    for path in sorted((Path(data_dir()) / 'receipts').glob('*.json')):
        receipt = json.loads(path.read_text())
        _run(receipt)
        path.unlink()
        count += 1
    return count


def run(payload):
    receipt = prepare(payload)
    if receipt is None:
        return
    folder = Path(data_dir()) / 'receipts'
    folder.mkdir(exist_ok=True, mode=0o700)
    digest = hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()
    path = folder / (digest + '.json')
    # Unique staging name avoids concurrent writers clobbering a common temp file.
    import tempfile
    fd, name = tempfile.mkstemp(dir=folder, prefix='.pending-')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(receipt, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
        dirfd = os.open(str(folder), os.O_RDONLY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    _run(receipt)
    path.unlink(missing_ok=True)


def _run(payload):
    ev = payload.get("hook_event_name")
    sid = payload.get("session_id")
    if ev not in HANDLED or not sid:
        return
    cwd = payload.get("cwd")
    tpath = payload.get("transcript_path")
    pid = payload.get("prompt_id")
    now = time.time()
    digest = hashlib.sha256(json.dumps(
        {"e": ev, "s": sid, "p": pid, "c": cwd, "x": payload.get('body_digest'), "src": payload.get("source")},
        sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    note = None
    if ev == "SessionStart":
        note = "source=%s" % payload.get("source")

    conn = connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            cur = conn.execute(
                "INSERT OR IGNORE INTO events(received_at,hook_event,session_id,cwd,transcript_path,"
                "prompt_id,payload_digest,project,note) VALUES(?,?,?,?,?,?,?,?,?)",
                (now, ev, sid, cwd, tpath, pid, digest, resolve_project(cwd), note))
            is_new = cur.rowcount == 1
            if is_new:
                event_id = cur.lastrowid
            else:
                meta_incr(conn, "dup_events")
                event_id = conn.execute("SELECT id FROM events WHERE payload_digest=?",
                                        (digest,)).fetchone()["id"]
            conn.execute(
                "INSERT INTO sessions(session_id,transcript_path,cwd,project,first_seen,last_hook_at,transport_session_id,source_identity) "
                "VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(session_id) DO UPDATE SET "
                "last_hook_at=excluded.last_hook_at, "
                "transcript_path=COALESCE(excluded.transcript_path, transcript_path), "
                "cwd=COALESCE(excluded.cwd, cwd), project=excluded.project",
                (sid, tpath, cwd, resolve_project(cwd), now, now, payload.get('transport_session_id'), payload.get('source_identity')))
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise

        # Stop aninda transkript guncel mi? (asenkron yazim gozlemi) — ingest'ten ONCE.
        if ev == "Stop" and is_new and tpath:
            expected = payload.get('assistant_digest')
            if expected:
                present = any(hashlib.sha256(_norm(redact(t)).encode()).hexdigest() == expected
                              for t in tail_assistant_texts(tpath))
                conn.execute("INSERT INTO transcript_checks(session_id,checked_at,present) VALUES(?,?,?)",
                             (sid, time.time(), 1 if present else 0))

        process_session(conn, sid, budget_s=BUDGET_S, event_id=event_id)
    finally:
        conn.close()


def main():
    try:
        raw = sys.stdin.read(1048577)
        if len(raw) > 1048576:
            raise ValueError('hook payload exceeds 1 MiB limit')
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("payload nesne degil")
    except Exception as e:
        log_error("stdin", e)
        return 0
    try:
        run(payload)
    except Exception as e:  # oturumu asla bozma
        log_error("hook:%s" % payload.get("hook_event_name"), e)
    return 0
