"""spike komut satiri."""
import argparse
import os
import sys
import time

from . import install as inst
from .db import connect, data_dir
from .extract import RULE_DESC
from .pipeline import load_bindings, process_all, save_bindings
from .reporting import TYPE_TR, export_html, report, status

KEYS = {"a": "accept", "r": "reject", "d": "defer"}


def _card(conn, c):
    m = conn.execute("SELECT * FROM messages WHERE id=?", (c["message_id"],)).fetchone()
    print("-" * 70)
    print("#%d  [%s]  proje: %s" % (c["id"], TYPE_TR.get(c["type"], c["type"]), c["project"]))
    print("  \"%s\"" % c["text"])
    if c["type"] == "impl_claim":
        print("  ⚠ İDDİA: agent 'bitti' dedi; doğrulanmadı.")
    rec = c["recon"]
    if c["recon_ref"]:
        ref = conn.execute("SELECT text FROM candidates WHERE id=?", (c["recon_ref"],)).fetchone()
        print("  uzlaştırma: %s → #%d: \"%s\"" % (rec, c["recon_ref"], (ref["text"] if ref else "")[:100]))
    else:
        print("  uzlaştırma: %s" % rec)
    print("  neden: kural %s (%s) | güven: kural tabanlı" % (c["rule"], RULE_DESC.get(c["rule"], "")))
    print("  kaynak: oturum %s · %s · %s · mesaj %s" % (
        m["session_id"][:8], m["role"], m["ts"] or "", m["uuid"][:8]))


def _pending(conn, project=None, deferred=False, limit=50):
    q = ("SELECT c.* FROM candidates c WHERE " +
         ("EXISTS (SELECT 1 FROM review_events r WHERE r.candidate_id=c.id AND r.id=(SELECT MAX(id) "
          "FROM review_events WHERE candidate_id=c.id) AND r.decision='defer')" if deferred else
          "NOT EXISTS (SELECT 1 FROM review_events r WHERE r.candidate_id=c.id)"))
    args = []
    if project:
        q += " AND c.project=?"
        args.append(project)
    q += " ORDER BY c.id LIMIT ?"
    args.append(limit)
    return conn.execute(q, args).fetchall()


def _decide(conn, cid, decision):
    if not conn.execute("SELECT 1 FROM candidates WHERE id=?", (cid,)).fetchone():
        raise SystemExit("aday yok: %s" % cid)
    conn.execute("INSERT INTO review_events(candidate_id,decision,decided_at) VALUES(?,?,?)",
                 (cid, decision, time.time()))


def cmd_review(conn, a):
    rows = _pending(conn, a.project, a.deferred, a.limit)
    if not rows:
        print("İncelenecek kart yok.")
        return
    print("%d kart. [a]onayla [r]reddet [d]ertele [s]geç [q]çık   (onay = doğru yakalama; "
          "doğrulama/task değildir)" % len(rows))
    for c in rows:
        _card(conn, c)
        while True:
            k = input("> ").strip().lower()[:1]
            if k in KEYS:
                _decide(conn, c["id"], KEYS[k])
                break
            if k == "s":
                break
            if k == "q":
                return


def main(argv=None):
    p = argparse.ArgumentParser(prog="spike", description="Decivora Spike-0 (ölçüm düzeneği)")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("install", help="hook'u bir sandbox projeye kur")
    s.add_argument("project_dir")
    s = sub.add_parser("uninstall", help="hook'u kaldır")
    s.add_argument("project_dir")
    s = sub.add_parser("bind", help="klasör → proje bağla")
    s.add_argument("path")
    s.add_argument("project")
    sub.add_parser("bindings", help="bağları listele")
    sub.add_parser("process", help="bekleyen transkript deltalarını işle")
    s = sub.add_parser('watch', help='seçilmiş oturumlarda sınırlı catch-up; model çağrısı yok')
    s.add_argument('--seconds', type=float, default=60)
    s.add_argument('--interval', type=float, default=1)
    sub.add_parser("status", help="capture durumu")
    s = sub.add_parser("review", help="kartları incele")
    s.add_argument("--project")
    s.add_argument("--deferred", action="store_true")
    s.add_argument("--limit", type=int, default=50)
    s = sub.add_parser("decide", help="tek kart için karar")
    s.add_argument("id", type=int)
    s.add_argument("decision", choices=["accept", "reject", "defer"])
    s = sub.add_parser("export-html", help="salt okunur HTML")
    s.add_argument("--out", default=None)
    s = sub.add_parser("report", help="ölçüm raporu")
    s.add_argument("--save", action="store_true", help="results/ altına kaydet")
    a = p.parse_args(argv)

    if a.cmd == "install":
        path = inst.install(a.project_dir)
        print("Kuruldu:", path)
        print("Veri dizini:", data_dir())
        print("Sonraki: `spike bind %s <proje-adı>` — sonra o klasörde YENİ bir Claude Code oturumu aç." %
              os.path.abspath(a.project_dir))
        return 0
    if a.cmd == "uninstall":
        print("Kaldırıldı:", inst.uninstall(a.project_dir))
        return 0
    if a.cmd == "bind":
        items = [b for b in load_bindings() if os.path.realpath(b["path"]) != os.path.realpath(a.path)]
        items.append({"path": os.path.abspath(a.path), "project": a.project})
        save_bindings(items)
        print("Bağlandı: %s → %s" % (os.path.abspath(a.path), a.project))
        return 0
    if a.cmd == "bindings":
        for b in load_bindings():
            print("%s → %s" % (b["path"], b["project"]))
        return 0

    conn = connect()
    if a.cmd == "process":
        from .hook import recover_receipts
        print('Recovered receipts:', recover_receipts())
        print(process_all(conn))
    elif a.cmd == "status":
        print(status(conn))
    elif a.cmd == 'watch':
        from .pipeline import catch_up
        print('Catch-up rounds:', catch_up(conn, a.seconds, a.interval))
    elif a.cmd == "review":
        cmd_review(conn, a)
    elif a.cmd == "decide":
        _decide(conn, a.id, a.decision)
        print("#%d → %s" % (a.id, a.decision))
    elif a.cmd == "export-html":
        out = a.out or os.path.join(data_dir(), "cards.html")
        print("Yazıldı:", export_html(conn, out))
    elif a.cmd == "report":
        text = report(conn)
        print(text)
        if a.save:
            from .db import HERE
            d = os.path.join(HERE, "results")
            os.makedirs(d, exist_ok=True)
            fp = os.path.join(d, "report-%s.md" % time.strftime("%Y%m%d-%H%M%S"))
            with open(fp, "w", encoding="utf-8") as f:
                f.write(text)
            print("Kaydedildi:", fp)
    return 0
