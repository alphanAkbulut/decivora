import json
import os
import time
import unittest

from helpers import FIX, SpikeCase, assistant, user, write_jsonl
from spike0.extract import extract
from spike0.pipeline import process_session
from spike0.redact import redact
from spike0.transcript import read_delta

C = "/work/demo"


def fx(name):
    return os.path.join(FIX, name)


class TestNoiseAndFiltering(SpikeCase):
    def test_f01_noop_and_non_message_records(self):
        """Onay/no-op mesajlari ve thinking/tool_result/system-reminder aday uretmez."""
        self.bind((C, "demo"))
        self.register("s1", fx("f01_noop.jsonl"), C)
        process_session(self.conn, "s1")
        self.assertEqual(self.q("SELECT COUNT(*) c FROM candidates")[0]["c"], 0)
        texts = [r["text"] for r in self.q("SELECT text FROM messages")]
        self.assertFalse(any("ozel muhakeme" in t or "arac sonucu" in t or "hatirlatma" in t
                             for t in texts))


class TestClaims(SpikeCase):
    def test_f05_claim_is_unverified(self):
        self.bind((C, "demo"))
        self.register("s5", fx("f05_claim.jsonl"), C)
        process_session(self.conn, "s5")
        rows = self.q("SELECT type, verification FROM candidates")
        self.assertEqual([(r["type"], r["verification"]) for r in rows], [("impl_claim", "unverified")])


class TestReversal(SpikeCase):
    def test_f06_explicit_vs_implicit(self):
        self.bind((C, "demo"))
        self.register("s6", fx("f06_reversal.jsonl"), C)
        process_session(self.conn, "s6")
        rows = self.q("SELECT id, recon, recon_ref FROM candidates ORDER BY id")
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["recon"], "new")
        self.assertEqual(rows[1]["recon"], "possible_supersedes")  # acik 'yerine'
        self.assertEqual(rows[1]["recon_ref"], rows[0]["id"])
        self.assertNotEqual(rows[2]["recon"], "possible_supersedes")  # ifadesiz: iddia yok


class TestMixedLanguage(SpikeCase):
    def test_f07_tr_en(self):
        self.bind((C, "demo"))
        self.register("s7", fx("f07_mixed.jsonl"), C)
        process_session(self.conn, "s7")
        types = [r["type"] for r in self.q("SELECT type FROM candidates")]
        self.assertGreaterEqual(types.count("decision"), 3)  # EN + TR + ASCII-TR
        self.assertIn("idea", types)


class TestParallelSessions(SpikeCase):
    def test_f08_three_sessions_one_project(self):
        self.bind((C, "demo"))
        for i in (1, 2, 3):
            self.register("par%d" % i, fx("f08_parallel_s%d.jsonl" % i), C)
        for i in (1, 2, 3):
            process_session(self.conn, "par%d" % i)
        offs = {r["session_id"]: r["offset"] for r in self.q("SELECT session_id, offset FROM sessions")}
        for i in (1, 2, 3):
            self.assertEqual(offs["par%d" % i], os.path.getsize(fx("f08_parallel_s%d.jsonl" % i)))
        rows = self.q("SELECT c.id, c.recon, c.recon_ref, m.session_id FROM candidates c "
                      "JOIN messages m ON m.id=c.message_id ORDER BY c.id")
        by = {r["session_id"]: r for r in rows}
        self.assertEqual(by["par2"]["recon"], "possible_supersedes")
        self.assertEqual(by["par2"]["recon_ref"], by["par1"]["id"])  # oturumlar arasi, ayni proje
        self.assertEqual(by["par3"]["recon"], "new")


class TestProjectIsolation(SpikeCase):
    def test_f04_same_name_two_projects(self):
        a, b = self.mkdir("a", "app"), self.mkdir("b", "app")
        self.bind((a, "app-a"), (b, "app-b"))
        same = "Karar: yerel depolama için SQLite kullanacağız."
        write_jsonl(os.path.join(self.tmp, "ta.jsonl"), [user("u1", "sa", a, same)])
        write_jsonl(os.path.join(self.tmp, "tb.jsonl"), [user("u1", "sb", b, same)])
        self.register("sa", os.path.join(self.tmp, "ta.jsonl"), a)
        self.register("sb", os.path.join(self.tmp, "tb.jsonl"), b)
        process_session(self.conn, "sa")
        process_session(self.conn, "sb")
        rows = self.q("SELECT project, recon FROM candidates ORDER BY id")
        self.assertEqual([(r["project"], r["recon"]) for r in rows],
                         [("app-a", "new"), ("app-b", "new")])  # projeler arasi duplicate YOK

    def test_f10_unbound_cwd_quarantine(self):
        other = self.mkdir("other")
        self.bind((self.mkdir("bound"), "bound"))
        write_jsonl(os.path.join(self.tmp, "t.jsonl"), [user("u1", "sq", other, "Karar: bir şey seçtik.")])
        self.register("sq", os.path.join(self.tmp, "t.jsonl"), other)
        st = process_session(self.conn, "sq")
        self.assertEqual(st["quarantined"], 1)
        self.assertEqual(self.q("SELECT COUNT(*) c FROM candidates")[0]["c"], 0)
        self.assertEqual(self.q("SELECT quarantined FROM messages")[0]["quarantined"], 1)


class TestDeltaReader(SpikeCase):
    def test_f03_partial_line_then_complete(self):
        self.bind((C, "demo"))
        p = os.path.join(self.tmp, "t.jsonl")
        full = json.dumps(user("u3", "sp", C, "Karar: üçüncü mesaj tamamlandı."), ensure_ascii=False)
        write_jsonl(p, [user("u1", "sp", C, "Merhaba dünya, bu bir deneme."),
                        user("u2", "sp", C, "İkinci mesaj burada.")], partial_tail=full[:25])
        self.register("sp", p, C)
        process_session(self.conn, "sp")
        self.assertEqual(self.q("SELECT COUNT(*) c FROM messages")[0]["c"], 2)
        off = self.q("SELECT offset FROM sessions")[0]["offset"]
        self.assertEqual(off, os.path.getsize(p) - 25)  # yarim satir tuketilmedi
        with open(p, "a", encoding="utf-8") as f:
            f.write(full[25:] + "\n")
        process_session(self.conn, "sp")
        self.assertEqual(self.q("SELECT COUNT(*) c FROM messages")[0]["c"], 3)
        process_session(self.conn, "sp")  # tekrar: dup yok
        self.assertEqual(self.q("SELECT COUNT(*) c FROM messages")[0]["c"], 3)

    def test_truncation_resets_without_duplicates(self):
        self.bind((C, "demo"))
        p = os.path.join(self.tmp, "t.jsonl")
        recs = [user("u1", "sr", C, "Karar: ilk kayıt metni burada."),
                user("u2", "sr", C, "Karar: ikinci kayıt metni burada.")]
        write_jsonl(p, recs)
        self.register("sr", p, C)
        process_session(self.conn, "sr")
        write_jsonl(p, recs[:1])  # dosya kisaldi
        st = process_session(self.conn, "sr")
        self.assertTrue(st["reset"])
        self.assertEqual(self.q("SELECT COUNT(*) c FROM messages")[0]["c"], 2)  # dup yok
        self.assertEqual(self.q("SELECT resets FROM sessions")[0]["resets"], 1)

    def test_bad_json_line_counted_not_fatal(self):
        p = os.path.join(self.tmp, "t.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            f.write("{bozuk json\n")
            f.write(json.dumps(user("u1", "sb", C, "Karar: geçerli satır var.")) + "\n")
        d = read_delta(p, 0)
        self.assertEqual((len(d["records"]), d["bad"]), (1, 1))

    def test_idempotent_rerun_same_offset(self):
        self.bind((C, "demo"))
        self.register("s6", fx("f06_reversal.jsonl"), C)
        process_session(self.conn, "s6")
        n1 = self.q("SELECT COUNT(*) c FROM candidates")[0]["c"]
        self.conn.execute("UPDATE sessions SET offset=0")  # kaydedilmemis ofset simulasyonu
        process_session(self.conn, "s6")
        self.assertEqual(self.q("SELECT COUNT(*) c FROM candidates")[0]["c"], n1)
        self.assertEqual(self.q("SELECT COUNT(*) c FROM messages")[0]["c"], 3)


class TestRedactionAndSidechain(SpikeCase):
    def test_redaction(self):
        t = "anahtar sk-abcdefghijklmnopqrstuv ve ghp_abcdefghijklmnopqrstuvwxyz ve AKIAABCDEFGHIJKLMNOP"
        r = redact(t)
        self.assertNotIn("sk-abc", r)
        self.assertNotIn("ghp_abc", r)
        self.assertNotIn("AKIAABC", r)

    def test_stored_text_is_redacted(self):
        self.bind((C, "demo"))
        p = os.path.join(self.tmp, "t.jsonl")
        write_jsonl(p, [user("u1", "sx", C, "Karar: anahtar sk-abcdefghijklmnopqrstuv kullanılacak.")])
        self.register("sx", p, C)
        process_session(self.conn, "sx")
        stored = " ".join(r["text"] for r in self.q("SELECT text FROM messages")) + \
            " ".join(r["text"] for r in self.q("SELECT text FROM candidates"))
        self.assertNotIn("sk-abc", stored)

    def test_sidechain_flagged(self):
        self.bind((C, "demo"))
        p = os.path.join(self.tmp, "t.jsonl")
        rec = assistant("a1", "sc", C, "Karar: alt agent sonucu böyle.")
        rec["isSidechain"] = True
        write_jsonl(p, [rec])
        self.register("sc", p, C)
        process_session(self.conn, "sc")
        self.assertEqual(self.q("SELECT sidechain FROM messages")[0]["sidechain"], 1)


class TestExtractor(unittest.TestCase):
    def test_code_fence_skipped(self):
        t = "Bakalım:\n```\nKarar: kod icindeki satir alinmamali\n```\nSon durum fena degil."
        self.assertEqual([c for c in extract("assistant", t) if c["type"] == "decision"], [])

    def test_ack_only(self):
        for t in ("tamam", "Tamam.", "OK", "devam", "teşekkürler!"):
            self.assertEqual(extract("user", t), [])

    def test_turkish_diacritics_folded(self):
        a = extract("user", "KARAR: şu yaklaşım ile devam edeceğiz.")
        b = extract("user", "karar: su yaklasim ile devam edecegiz.")
        self.assertEqual([c["type"] for c in a], [c["type"] for c in b])
        self.assertEqual(a[0]["type"], "decision")


class TestBurst(SpikeCase):
    def test_f09_burst_1000_no_loss(self):
        """Kayip olmamasi dogrulanir. Sure RAPORLANIR; basari esigi YOK (yalniz takilma korumasi)."""
        self.bind((C, "demo"))
        p = os.path.join(self.tmp, "burst.jsonl")
        recs = []
        for i in range(1000):
            if i % 5 == 0:
                txt = "Karar: %d numaralı modül için seçenek %d ile devam." % (i, i % 7)
            elif i % 5 == 1:
                txt = "Önerim: %d. adımda ek bir kontrol ekleyelim lütfen." % i
            else:
                txt = "Bu sıradan mesaj numara %d, içinde aday kalıbı yok." % i
            recs.append((user if i % 2 == 0 else assistant)("m%d" % i, "burst", C, txt))
        write_jsonl(p, recs)
        self.register("burst", p, C)
        t0 = time.time()
        st = process_session(self.conn, "burst")
        dt = time.time() - t0
        print("\n[burst] 1000 mesaj, %d aday, %.2fs (%.0f mesaj/sn)" % (
            st["candidates"], dt, 1000 / max(dt, 1e-9)))
        self.assertEqual(self.q("SELECT COUNT(*) c FROM messages")[0]["c"], 1000)
        self.assertEqual(self.q("SELECT offset FROM sessions")[0]["offset"], os.path.getsize(p))
        self.assertGreater(st["candidates"], 0)
        self.assertLess(dt, 120, "takilma korumasi (basari esigi degildir)")


if __name__ == "__main__":
    unittest.main()
