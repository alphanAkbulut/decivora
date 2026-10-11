"""Yerel SQLite: events/review_events append-only; digest ile tekillestirme."""
import os
import sqlite3
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA = os.path.join(HERE, "data")

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY,
  received_at REAL NOT NULL,
  hook_event TEXT NOT NULL,
  session_id TEXT NOT NULL,
  cwd TEXT,
  transcript_path TEXT,
  prompt_id TEXT,
  payload_digest TEXT NOT NULL UNIQUE,
  project TEXT,
  note TEXT
);
CREATE TABLE IF NOT EXISTS sessions(
  session_id TEXT PRIMARY KEY,
  transport_session_id TEXT,
  source_identity TEXT,
  transcript_path TEXT,
  cwd TEXT,
  project TEXT,
  cc_version TEXT,
  first_seen REAL,
  last_hook_at REAL,
  offset INTEGER NOT NULL DEFAULT 0,
  file_size_seen INTEGER NOT NULL DEFAULT 0,
  resets INTEGER NOT NULL DEFAULT 0,
  bad_lines INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS messages(
  id INTEGER PRIMARY KEY,
  session_id TEXT NOT NULL,
  uuid TEXT NOT NULL,
  role TEXT NOT NULL,
  text TEXT NOT NULL,
  ts TEXT,
  cwd TEXT,
  project TEXT,
  quarantined INTEGER NOT NULL DEFAULT 0,
  sidechain INTEGER NOT NULL DEFAULT 0,
  content_hash TEXT NOT NULL,
  byte_offset INTEGER,
  ingested_at REAL NOT NULL,
  event_id INTEGER,
  extraction_status TEXT NOT NULL DEFAULT 'unknown',
  UNIQUE(session_id, uuid)
);
CREATE TABLE IF NOT EXISTS answer_candidates(
  message_id INTEGER PRIMARY KEY REFERENCES messages(id),
  text TEXT NOT NULL,
  association TEXT NOT NULL DEFAULT 'unmatched'
);
CREATE TABLE IF NOT EXISTS candidates(
  id INTEGER PRIMARY KEY,
  message_id INTEGER NOT NULL REFERENCES messages(id),
  project TEXT NOT NULL,
  type TEXT NOT NULL,
  text TEXT NOT NULL,
  span_start INTEGER NOT NULL,
  span_end INTEGER NOT NULL,
  rule TEXT NOT NULL,
  confidence TEXT NOT NULL DEFAULT 'rule',
  verification TEXT NOT NULL DEFAULT 'unverified',
  recon TEXT NOT NULL,
  recon_ref INTEGER,
  created_at REAL NOT NULL,
  event_id INTEGER,
  UNIQUE(message_id, span_start, span_end, type)
);
CREATE TABLE IF NOT EXISTS review_events(
  id INTEGER PRIMARY KEY,
  candidate_id INTEGER NOT NULL REFERENCES candidates(id),
  decision TEXT NOT NULL,
  decided_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS transcript_checks(
  id INTEGER PRIMARY KEY,
  session_id TEXT NOT NULL,
  checked_at REAL NOT NULL,
  present INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_cand_project ON candidates(project);
CREATE INDEX IF NOT EXISTS ix_msg_session ON messages(session_id);
"""


def data_dir():
    d = os.environ.get("SPIKE0_DATA") or DEFAULT_DATA
    os.makedirs(d, exist_ok=True)
    return d


def connect(timeout=2.0):
    path = os.path.join(data_dir(), "spike0.db")
    conn = sqlite3.connect(path, timeout=timeout, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    # Additive migration for an existing measurement DB, not a production schema.
    for table, name, definition in (
        ('sessions', 'transport_session_id', 'TEXT'),
        ('sessions', 'source_identity', 'TEXT'),
        ('messages', 'extraction_status', "TEXT NOT NULL DEFAULT 'unknown'"),
    ):
        if name not in {r[1] for r in conn.execute('PRAGMA table_info(%s)' % table)}:
            conn.execute('ALTER TABLE %s ADD COLUMN %s %s' % (table, name, definition))
    return conn


def log_error(where, exc):
    """Hata dosyasina yazar. Payload/mesaj icerigi yazilmaz."""
    try:
        line = "%s\t%s\t%s\t%s\n" % (
            time.strftime("%Y-%m-%dT%H:%M:%S"), where,
            type(exc).__name__, str(exc).replace("\n", " ")[:160])
        with open(os.path.join(data_dir(), "errors.log"), "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def meta_incr(conn, key, n=1):
    conn.execute(
        "INSERT INTO meta(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=CAST(v AS INTEGER)+?",
        (key, str(n), n))


def meta_get(conn, key, default=0):
    r = conn.execute("SELECT v FROM meta WHERE k=?", (key,)).fetchone()
    return int(r["v"]) if r else default
