"""status / report / html. Hukum yazmaz; sayi ve gozlem raporlar."""
import html as htmllib
import math
from datetime import datetime
import os
import platform
import subprocess
import sys
import time

from .db import HERE, data_dir, meta_get
from .extract import RULE_DESC

TYPE_TR = {"decision": "karar ADAYI", "idea": "fikir/öneri", "instruction": "talimat",
           "incomplete": "yarım/bekleyen", "impl_claim": "tamamlama İDDİASI"}


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    a = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - a) / d, (c + a) / d)


def pct(xs, q):
    if not xs:
        return None
    s = sorted(xs)
    return s[min(len(s) - 1, max(0, math.ceil(q * len(s)) - 1))]


def _errors():
    p = os.path.join(data_dir(), "errors.log")
    try:
        with open(p, encoding="utf-8") as f:
            return [l.rstrip("\n").split("\t") for l in f if l.strip()]
    except FileNotFoundError:
        return []


def _ago(ts):
    if not ts:
        return "-"
    s = int(time.time() - ts)
    return "%ds" % s if s < 120 else "%dm" % (s // 60)


def status(conn):
    out = []
    sess = conn.execute("SELECT * FROM sessions ORDER BY last_hook_at DESC").fetchall()
    ev_total = conn.execute("SELECT COUNT(*) c FROM events").fetchone()["c"]
    if not ev_total:
        return ("Hiç hook olayı görülmedi → durum: BİLİNMİYOR.\n"
                "(Kurulum yapıldı mı? Kurulumdan SONRA yeni bir Claude Code oturumu açtın mı?)")
    out.append("Hook olayı: %d (tekrar eden/yutulan: %d) | hata kaydı: %d satır" % (
        ev_total, meta_get(conn, "dup_events"), len(_errors())))
    for s in sess:
        ev = conn.execute("SELECT hook_event, COUNT(*) c FROM events WHERE session_id=? "
                          "GROUP BY hook_event", (s["session_id"],)).fetchall()
        evs = ", ".join("%s×%d" % (r["hook_event"], r["c"]) for r in ev)
        try:
            size = os.stat(s["transcript_path"]).st_size
        except Exception:
            size = None
        pend = (size - s["offset"]) if size is not None else None
        m = conn.execute("SELECT COUNT(*) c, SUM(quarantined) q FROM messages WHERE session_id=?",
                         (s["session_id"],)).fetchone()
        pc = conn.execute(
            "SELECT COUNT(*) c FROM candidates c JOIN messages m ON m.id=c.message_id "
            "WHERE m.session_id=? AND NOT EXISTS (SELECT 1 FROM review_events r WHERE r.candidate_id=c.id)",
            (s["session_id"],)).fetchone()["c"]
        flag = ""
        if size is None:
            flag = "  ⚠ transkript dosyası okunamadı"
        elif pend and pend > 0:
            flag = "  ⚠ GERİDE: %d bayt işlenmedi (`spike process`)" % pend
        out.append("- oturum %s | proje: %s | son hook: %s önce | cc: %s\n"
                   "    olaylar: %s\n    işlenen: %s / %s bayt | mesaj: %d (karantina: %d) | "
                   "bekleyen kart: %d | sıfırlama: %d%s" % (
                       s["session_id"][:8], s["project"] or "BAĞSIZ(karantina)",
                       _ago(s["last_hook_at"]), s["cc_version"] or "?", evs,
                       s["offset"], size if size is not None else "?", m["c"], m["q"] or 0,
                       pc, s["resets"], flag))
    tc = conn.execute("SELECT COUNT(*) n, SUM(present) p FROM transcript_checks").fetchone()
    if tc["n"]:
        out.append("Stop tam cevap içeriği eşleşmesi: %d/%d" % (tc["p"] or 0, tc["n"]))
    out.append("Not: 'sağlıklı' demiyoruz; yalnız hook'un gördüğü ve işlenen aralık raporlanır.")
    out.append('Kısa cevap association unmatched: %d | extraction limited: %d' % (
        conn.execute('SELECT COUNT(*) FROM answer_candidates WHERE association=\'unmatched\'').fetchone()[0],
        conn.execute("SELECT COUNT(*) FROM messages WHERE extraction_status='limited'").fetchone()[0]))
    out.append('Stop ölçümü tam içerik eşleşmesidir; turn kimliği/freshness garantisi değildir.')
    return "\n".join(out)


def _git_commit():
    try:
        return subprocess.check_output(["git", "-C", HERE, "rev-parse", "--short", "HEAD"],
                                       stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "?"


def report(conn):
    L = []
    L.append("# Spike-0 raporu")
    L.append("")
    L.append("> Bu bir ölçüm çıktısıdır; MVP kanıtı veya başarı/başarısızlık hükmü değildir. "
             "Küçük örneklemler genelleştirilemez.")
    L.append("")
    ver = [r["cc_version"] for r in conn.execute(
        "SELECT DISTINCT cc_version FROM sessions WHERE cc_version IS NOT NULL")]
    L.append("## Ortam")
    L.append("- Zaman: %s | repo commit: %s | Python %s | %s" % (
        time.strftime("%Y-%m-%d %H:%M:%S"), _git_commit(), platform.python_version(),
        platform.platform()))
    L.append("- Gözlenen Claude Code sürümleri (transkriptten): %s" % (", ".join(ver) or "?"))
    L.append("")
    n_ev = conn.execute("SELECT COUNT(*) c FROM events").fetchone()["c"]
    n_sess = conn.execute("SELECT COUNT(*) c FROM sessions").fetchone()["c"]
    L.append("## Hook kapsamı")
    L.append("- Hook olayı: %d | oturum: %d | tekrar eden olay: %d" % (
        n_ev, n_sess, meta_get(conn, "dup_events")))
    for r in conn.execute("SELECT hook_event, COUNT(*) c FROM events GROUP BY hook_event"):
        L.append("  - %s: %d" % (r["hook_event"], r["c"]))
    nomsg = conn.execute(
        "SELECT COUNT(*) c FROM sessions s WHERE NOT EXISTS "
        "(SELECT 1 FROM messages m WHERE m.session_id=s.session_id)").fetchone()["c"]
    L.append("- Hiç mesajı işlenmemiş oturum: %d" % nomsg)
    stop_no_end = conn.execute(
        "SELECT COUNT(*) c FROM sessions s WHERE EXISTS (SELECT 1 FROM events e WHERE "
        "e.session_id=s.session_id AND e.hook_event='Stop') AND NOT EXISTS "
        "(SELECT 1 FROM events e WHERE e.session_id=s.session_id AND e.hook_event='SessionEnd')"
    ).fetchone()["c"]
    L.append("- SessionEnd görülmeyen (Stop görülen) oturum: %d" % stop_no_end)
    tc = conn.execute("SELECT COUNT(*) n, SUM(present) p FROM transcript_checks").fetchone()
    if tc["n"]:
        L.append("- Stop tam cevap içeriği transkriptte eşleşti: %d/%d "
                 "(turn kimliği ve freshness garantisi değildir)" % (tc["p"] or 0, tc["n"]))
    L.append("")
    L.append("## Mesaj ve karantina")
    m = conn.execute("SELECT COUNT(*) c, SUM(quarantined) q, SUM(sidechain) s FROM messages").fetchone()
    L.append("- Mesaj: %d | karantina: %d | sidechain (alt-agent): %d" % (
        m["c"], m["q"] or 0, m["s"] or 0))
    bad = conn.execute("SELECT SUM(bad_lines) b, SUM(resets) r FROM sessions").fetchone()
    L.append("- Bozuk JSON satırı: %d | transkript kısalma/sıfırlama: %d" % (bad["b"] or 0, bad["r"] or 0))
    L.append("")
    L.append("## Adaylar (kural tabanlı; recall düşük, gürültü beklenir)")
    rows = conn.execute("SELECT type, recon, COUNT(*) c FROM candidates GROUP BY type, recon").fetchall()
    L.append("| tür | recon | adet |")
    L.append("|---|---|---|")
    for r in rows:
        L.append("| %s | %s | %d |" % (TYPE_TR.get(r["type"], r["type"]), r["recon"], r["c"]))
    L.append("")
    L.append("## Gecikme (hook alındı → aday yazıldı)")
    lat = [r["d"] for r in conn.execute(
        "SELECT (c.created_at - e.received_at) d FROM candidates c JOIN events e ON e.id=c.event_id")]
    if lat:
        L.append("- n=%d | p50=%.3fs | p95=%.3fs (hook içi işleme süresi; bekleme dahil değil)" % (
            len(lat), pct(lat, .5), pct(lat, .95)))
    else:
        L.append("- veri yok")
    L.append("")
    L.append("## Yakalama gecikmesi (mesaj zamanı → işlendi)")
    L.append("Transkript asenkron yazıldığı için asıl gecikme budur; hook'un kendi süresi değil.")
    lag2 = []
    for r in conn.execute("SELECT ts, ingested_at FROM messages WHERE ts IS NOT NULL"):
        try:
            t = datetime.fromisoformat(r["ts"].replace("Z", "+00:00")).timestamp()
            lag2.append(r["ingested_at"] - t)
        except Exception:
            pass
    if lag2:
        L.append("- n=%d | p50=%.1fs | p95=%.1fs | max=%.1fs" % (
            len(lag2), pct(lag2, .5), pct(lag2, .95), max(lag2)))
    else:
        L.append("- veri yok")
    L.append("")
    L.append("## İnceleme sonuçları (senin etiketlerin)")
    dec = {r["decision"]: r["c"] for r in conn.execute(
        "SELECT decision, COUNT(*) c FROM (SELECT candidate_id, decision, MAX(id) FROM review_events "
        "GROUP BY candidate_id) GROUP BY decision")}
    a, r_, d = dec.get("accept", 0), dec.get("reject", 0), dec.get("defer", 0)
    pending = conn.execute(
        "SELECT COUNT(*) c FROM candidates c WHERE NOT EXISTS "
        "(SELECT 1 FROM review_events r WHERE r.candidate_id=c.id)").fetchone()["c"]
    L.append("- onayla: %d | reddet: %d | ertele: %d | bekleyen: %d" % (a, r_, d, pending))
    n = a + r_
    if n:
        lo, hi = wilson(a, n)
        L.append("- precision (onay/(onay+red)): %.2f, n=%d, Wilson %%95 aralık [%.2f, %.2f]%s" % (
            a / n, n, lo, hi, "  ⚠ n<30: yalnız yön göstergesi" if n < 30 else ""))
    else:
        L.append("- precision: N/A (etiket yok)")
    L.append("- Bu oran yalnız incelenen kartların kabul oranıdır; bağımsız gold precision/recall değildir.")
    L.append("- 'onayla' = doğru yakalama demektir; task oluşturmaz, 'verified' üretmez.")
    L.append("")
    L.append("## Hatalar (errors.log)")
    errs = _errors()
    L.append("- toplam: %d" % len(errs))
    kinds = {}
    for e in errs:
        k = "%s/%s" % (e[1] if len(e) > 1 else "?", e[2] if len(e) > 2 else "?")
        kinds[k] = kinds.get(k, 0) + 1
    for k, c in sorted(kinds.items(), key=lambda x: -x[1])[:8]:
        L.append("  - %s: %d" % (k, c))
    return "\n".join(L) + "\n"


def export_html(conn, path):
    rows = conn.execute(
        "SELECT c.*, m.role, m.ts, m.session_id FROM candidates c JOIN messages m ON m.id=c.message_id "
        "ORDER BY c.id DESC LIMIT 500").fetchall()
    decided = {r["candidate_id"]: r["decision"] for r in conn.execute(
        "SELECT candidate_id, decision, MAX(id) FROM review_events GROUP BY candidate_id")}
    cards = []
    for r in rows:
        dec = decided.get(r["id"], "bekliyor")
        warn = "<p class=w>İddia — doğrulanmadı.</p>" if r["type"] == "impl_claim" else ""
        cards.append(
            "<article><h3>#%d · %s <small>%s</small></h3><blockquote>%s</blockquote>%s"
            "<p class=m>proje: %s · oturum %s · %s · kural %s (%s) · uzlaştırma: %s%s · durum: %s</p></article>" % (
                r["id"], htmllib.escape(TYPE_TR.get(r["type"], r["type"])), htmllib.escape(r["role"]),
                htmllib.escape(r["text"]), warn, htmllib.escape(r["project"]),
                htmllib.escape(r["session_id"][:8]), htmllib.escape(r["ts"] or ""),
                htmllib.escape(r["rule"]), htmllib.escape(RULE_DESC.get(r["rule"], "")),
                htmllib.escape(r["recon"]),
                (" → #%d" % r["recon_ref"]) if r["recon_ref"] else "", htmllib.escape(dec)))
    doc = ("<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
           "<title>Spike-0 kartlar</title><style>:root{color-scheme:light dark}body{font:15px/1.5 system-ui;"
           "max-width:820px;margin:0 auto;padding:16px}article{border:1px solid #8884;border-radius:8px;"
           "padding:8px 14px;margin:12px 0}blockquote{margin:6px 0;padding-left:10px;border-left:3px solid #8886}"
           ".m{font-size:12px;opacity:.75}.w{color:#b45309;font-weight:600}small{opacity:.6;font-weight:400}</style>"
           "<h1>Spike-0 kartları</h1><p>Salt okunur görünüm. Karar vermek için: <code>spike review</code> veya "
           "<code>spike decide ID accept|reject|defer</code>. Onay doğrulama değildir.</p>%s"
           % ("".join(cards) or "<p>Kart yok.</p>"))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    return path
