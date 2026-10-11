"""Mini uzlastirma: new / duplicate / possible_supersedes / unknown.

Kesinlik iddiasi yok. Yalniz ayni proje icinde karsilastirir (proje izolasyonu).
possible_supersedes yalniz ACIK degisim ifadesi varsa uretilir.
"""
import re
from .extract import fold

STOP = set("ve bir bu su o ile icin de da mi mu ne the a an to of and is are for in on it that "
           "this we be as at by or".split())
SUPERSEDE_RE = re.compile(
    r"\b(yerine|instead of|vazgec\w*|artik .{0,40}degil|no longer|replac\w*|rather than|"
    r"iptal|degistirdik|switch\w* to|scrap\w*)\b")
DUP_JACCARD = 0.8
NEGATION_RE = re.compile(r"\b(degil|not|never|no longer|cannot|won't|\w*(mayacag|meyeceg|madik|medik)\w*)\b")
SUP_COEF = 0.3
SUP_MIN_OVERLAP = 2


def tokens(text):
    t = re.sub(r"[^a-z0-9]+", " ", fold(text))
    return frozenset(w for w in t.split() if w not in STOP and len(w) > 1)


class Index:
    """Proje basina bellek ici aday indeksi (DB'den tembel yuklenir)."""

    def __init__(self, conn):
        self.conn = conn
        self.by_project = {}

    def _load(self, project):
        rows = self.conn.execute(
            "SELECT id,type,text FROM candidates WHERE project=? ORDER BY id", (project,)).fetchall()
        self.by_project[project] = [(r["id"], r["type"], tokens(r["text"])) for r in rows]

    def items(self, project):
        if project not in self.by_project:
            self._load(project)
        return self.by_project[project]

    def add(self, project, cid, typ, text):
        self.items(project).append((cid, typ, tokens(text)))


def reconcile(index, project, typ, text):
    """-> (recon, ref_id|None)"""
    tk = tokens(text)
    prev = index.items(project)
    sup_word = bool(SUPERSEDE_RE.search(fold(text)))
    if len(tk) >= 3:
        for cid, _t, ptk in prev:
            if _t != typ:
                continue
            if ptk and len(tk | ptk) and len(tk & ptk) / len(tk | ptk) >= DUP_JACCARD:
                prior = index.conn.execute('SELECT text FROM candidates WHERE id=?', (cid,)).fetchone()
                if prior and fold(prior['text']) == fold(text):
                    return "duplicate", cid  # exact content repeat, not canonical identity
                if prior and bool(NEGATION_RE.search(fold(prior['text']))) != bool(NEGATION_RE.search(fold(text))):
                    return 'review_conflict', cid
                if not sup_word:
                    return 'possible_duplicate', cid
    if sup_word:
        best, best_score = None, 0.0
        for cid, ptype, ptk in prev:
            if ptype not in ("decision", "idea") or not ptk:
                continue
            ov = len(tk & ptk)
            if ov < SUP_MIN_OVERLAP:
                continue
            score = ov / min(len(tk), len(ptk))
            if score >= SUP_COEF and score > best_score:
                best, best_score = cid, score
        if best is not None:
            return "possible_supersedes", best
        return "unknown", None
    return "new", None
