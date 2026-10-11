"""Proje baglama, delta ingest, cikarim ve uzlastirma boru hatti."""
import hashlib
import json
import os
import time

from .db import data_dir, log_error
from .extract import extract_with_coverage, SHORT_ANSWER_RE, fold
from .reconcile import Index, reconcile
from .redact import redact
from .transcript import read_delta, to_message

CHUNK = 500


# ---- proje baglama (acik bindings.json; baglanamayan -> karantina) ----
def bindings_path():
    return os.path.join(data_dir(), "bindings.json")


def load_bindings():
    try:
        with open(bindings_path(), encoding="utf-8") as f:
            return json.load(f).get("bindings", [])
    except FileNotFoundError:
        return []
    except Exception as e:
        log_error("bindings", e)
        return []


def save_bindings(items):
    with open(bindings_path(), "w", encoding="utf-8") as f:
        json.dump({"bindings": items}, f, indent=2, ensure_ascii=False)


def resolve_project(cwd, bindings=None):
    """En uzun yol oneki eslesmesi (dizin siniri gozetilerek). Yoksa None."""
    if not cwd:
        return None
    b = load_bindings() if bindings is None else bindings
    c = os.path.realpath(cwd)
    best, blen = None, -1
    for item in b:
        p = os.path.realpath(item["path"])
        if (c == p or c.startswith(p + os.sep)) and len(p) > blen:
            best, blen = item["project"], len(p)
    return best


# ---- ingest ----
def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:32]


def process_session(conn, session_id, budget_s=None, event_id=None):
    """Oturumun transkript deltasini isler. Idempotent. -> stats dict"""
    stats = dict(messages=0, candidates=0, quarantined=0, dup_messages=0, bad=0,
                 reset=False, partial_budget=False)
    sess = conn.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,)).fetchone()
    if not sess or not sess["transcript_path"]:
        return stats
    deadline = time.time() + budget_s if budget_s else None
    bindings = load_bindings()
    index = Index(conn)
    offset = sess["offset"]
    version_seen = sess["cc_version"]

    while True:
        d = read_delta(sess["transcript_path"], offset)
        if d["reset"]:
            stats["reset"] = True
            conn.execute("UPDATE sessions SET resets=resets+1 WHERE session_id=?", (session_id,))
            offset = 0
        recs = d["records"]
        stats["bad"] += d["bad"]
        if not recs:
            conn.execute(
                "UPDATE sessions SET offset=?, file_size_seen=?, bad_lines=bad_lines+? "
                "WHERE session_id=?", (d["new_offset"], d["size"], d["bad"], session_id))
            break
        chunks = [recs[i:i + CHUNK] for i in range(0, len(recs), CHUNK)]
        for ci, ch in enumerate(chunks):
            end = d["new_offset"] if ci == len(chunks) - 1 else ch[-1][1]
            conn.execute("BEGIN IMMEDIATE")
            try:
                for start, _e, rec in ch:
                    m = to_message(rec)
                    if not m:
                        continue
                    if not version_seen and m.get("version"):
                        version_seen = m["version"]
                        conn.execute("UPDATE sessions SET cc_version=? WHERE session_id=?",
                                     (version_seen, session_id))
                    _handle_message(conn, index, bindings, sess, session_id, m, start,
                                    event_id, stats)
                conn.execute(
                    "UPDATE sessions SET offset=?, file_size_seen=?, bad_lines=bad_lines+? "
                    "WHERE session_id=?",
                    (end, d["size"], d["bad"] if ci == len(chunks) - 1 else 0, session_id))
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
            offset = end
            if deadline and time.time() > deadline and ci < len(chunks) - 1:
                stats["partial_budget"] = True
                return stats
        if d["new_offset"] >= d["size"]:
            break
        if deadline and time.time() > deadline:
            stats["partial_budget"] = True
            break
    return stats


def _handle_message(conn, index, bindings, sess, session_id, m, start, event_id, stats):
    text = redact(m["text"])
    chash = _sha(text)
    uuid = m["uuid"] or "nouuid:%s:%d" % (chash, start)
    cwd = m["cwd"] or sess["cwd"]
    project = resolve_project(cwd, bindings)
    quarantined = 1 if project is None else 0
    cur = conn.execute(
        "INSERT OR IGNORE INTO messages(session_id,uuid,role,text,ts,cwd,project,quarantined,"
        "sidechain,content_hash,byte_offset,ingested_at,event_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (session_id, uuid, m["role"], text, m["ts"], cwd, project, quarantined,
         1 if m["sidechain"] else 0, chash, start, time.time(), event_id))
    if cur.rowcount == 0:
        stats["dup_messages"] += 1
        return
    mid = cur.lastrowid
    stats["messages"] += 1
    if quarantined:
        stats["quarantined"] += 1
        return
    if m['role'] == 'user' and SHORT_ANSWER_RE.match(fold(text.strip())):
        conn.execute('INSERT OR IGNORE INTO answer_candidates(message_id,text) VALUES(?,?)', (mid, text))
    extracted, coverage = extract_with_coverage(m['role'], text)
    conn.execute('UPDATE messages SET extraction_status=? WHERE id=?', (coverage, mid))
    for c in extracted:
        recon, ref = reconcile(index, project, c["type"], c["text"])
        cc = conn.execute(
            "INSERT OR IGNORE INTO candidates(message_id,project,type,text,span_start,span_end,"
            "rule,recon,recon_ref,created_at,event_id) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (mid, project, c["type"], c["text"], c["start"], c["end"], c["rule"],
             recon, ref, time.time(), event_id))
        if cc.rowcount:
            index.add(project, cc.lastrowid, c["type"], c["text"])
            stats["candidates"] += 1


def process_all(conn):
    total = dict(messages=0, candidates=0, quarantined=0, dup_messages=0, bad=0)
    for r in conn.execute("SELECT session_id FROM sessions").fetchall():
        s = process_session(conn, r["session_id"])
        for k in total:
            total[k] += s[k]
    return total


def catch_up(conn, seconds=60.0, interval=1.0):
    """Explicit bounded polling for already selected sessions, without a closing hook."""
    if not 0 < seconds <= 3600 or not 0.05 <= interval <= 60:
        raise ValueError('watch bounds: seconds (0,3600], interval [0.05,60]')
    from .hook import recover_receipts
    deadline = time.monotonic() + seconds
    rounds = 0
    while True:
        recover_receipts()
        process_all(conn)
        rounds += 1
        left = deadline - time.monotonic()
        if left <= 0:
            return rounds
        time.sleep(min(left, interval))
