import json
import os
import sqlite3
import subprocess
import sys
import unittest

from helpers import ROOT, SpikeCase, assistant, user, write_jsonl
from spike0 import install as inst
from spike0.reporting import report, status, wilson

HOOK = os.path.join(ROOT, "bin", "spike0_hook.py")


class HookCase(SpikeCase):
    def run_hook(self, payload, raw=None, env_extra=None):
        env = dict(os.environ, SPIKE0_DATA=self.data)
        if env_extra:
            env.update(env_extra)
        p = subprocess.run([sys.executable, HOOK], input=raw if raw is not None else json.dumps(payload),
                           capture_output=True, text=True, env=env, timeout=30)
        return p

    def payload(self, ev, sid, cwd, tpath, **kw):
        d = {"session_id": sid, "transcript_path": tpath, "cwd": cwd, "hook_event_name": ev}
        d.update(kw)
        return d


class TestHookRobustness(HookCase):
    def test_bad_json_exit0_no_stdout(self):
        p = self.run_hook(None, raw="{{not json")
        self.assertEqual((p.returncode, p.stdout), (0, ""))
        with open(os.path.join(self.data, "errors.log")) as f:
            self.assertIn("stdin", f.read())

    def test_empty_stdin(self):
        p = self.run_hook(None, raw="")
        self.assertEqual((p.returncode, p.stdout), (0, ""))

    def test_unknown_event_ignored(self):
        p = self.run_hook(self.payload("PreToolUse", "s", "/x", "/nonexistent"))
        self.assertEqual((p.returncode, p.stdout), (0, ""))
        self.assertEqual(self.q("SELECT COUNT(*) c FROM events")[0]["c"], 0)

    def test_locked_db_does_not_break_session(self):
        blocker = sqlite3.connect(os.path.join(self.data, "spike0.db"), isolation_level=None)
        blocker.execute("BEGIN EXCLUSIVE")
        try:
            p = self.run_hook(self.payload("SessionStart", "sl", "/x", "/none", source="startup"))
        finally:
            blocker.execute("ROLLBACK")
            blocker.close()
        self.assertEqual((p.returncode, p.stdout), (0, ""))
        self.assertTrue(os.path.exists(os.path.join(self.data, "errors.log")))

    def test_stdout_always_empty_on_success(self):
        proj = self.mkdir("proj")
        self.bind((proj, "demo"))
        t = os.path.join(self.tmp, "t.jsonl")
        write_jsonl(t, [user("u1", "sh", proj, "Karar: hook stdout boş kalmalı.")])
        p = self.run_hook(self.payload("UserPromptSubmit", "sh", proj, t, prompt="x", prompt_id="p1"))
        self.assertEqual((p.returncode, p.stdout), (0, ""))
        self.assertEqual(self.q("SELECT COUNT(*) c FROM candidates")[0]["c"], 1)


class TestHookDedup(HookCase):
    def test_f02_resend_same_event_single_effect(self):
        proj = self.mkdir("proj")
        self.bind((proj, "demo"))
        t = os.path.join(self.tmp, "t.jsonl")
        write_jsonl(t, [user("u1", "sd", proj, "Karar: tek etki olmalı."),
                        assistant("a1", "sd", proj, "Hook alıcıyı tamamlandı olarak işaretledim.")])
        pl = self.payload("Stop", "sd", proj, t, last_assistant_message="Hook alıcıyı tamamlandı",
                          prompt_id="p9")
        self.run_hook(pl)
        n = [self.q("SELECT COUNT(*) c FROM %s" % tb)[0]["c"] for tb in ("events", "messages", "candidates")]
        self.run_hook(pl)
        self.run_hook(pl)
        m = [self.q("SELECT COUNT(*) c FROM %s" % tb)[0]["c"] for tb in ("events", "messages", "candidates")]
        self.assertEqual(n, m)
        self.assertEqual(n[0], 1)
        self.assertEqual(self.q("SELECT v FROM meta WHERE k='dup_events'")[0]["v"], "2")

    def test_same_prompt_text_different_prompt_id_two_events(self):
        proj = self.mkdir("proj")
        self.bind((proj, "demo"))
        t = os.path.join(self.tmp, "t.jsonl")
        write_jsonl(t, [])
        for pid in ("p1", "p2"):
            self.run_hook(self.payload("UserPromptSubmit", "se", proj, t, prompt="devam", prompt_id=pid))
        self.assertEqual(self.q("SELECT COUNT(*) c FROM events")[0]["c"], 2)


class TestTranscriptLag(HookCase):
    def test_stop_lag_check(self):
        proj = self.mkdir("proj")
        self.bind((proj, "demo"))
        t = os.path.join(self.tmp, "t.jsonl")
        write_jsonl(t, [assistant("a1", "sg", proj, "Birinci cevap burada, tamam.")])
        self.run_hook(self.payload("Stop", "sg", proj, t, last_assistant_message="Birinci cevap burada, tamam.",
                                   prompt_id="a"))
        self.run_hook(self.payload("Stop", "sg", proj, t, last_assistant_message="Henüz yazılmamış ikinci cevap.",
                                   prompt_id="b"))
        self.assertEqual([r["present"] for r in self.q("SELECT present FROM transcript_checks ORDER BY id")],
                         [1, 0])


class TestInstall(SpikeCase):
    def test_install_uninstall_preserves_other_config(self):
        proj = self.mkdir("sandbox")
        sp = os.path.join(proj, ".claude", "settings.local.json")
        os.makedirs(os.path.dirname(sp))
        other = {"permissions": {"allow": ["Bash(ls)"]},
                 "hooks": {"Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "echo benim"}]}]}}
        with open(sp, "w") as f:
            json.dump(other, f)
        inst.install(proj)
        inst.install(proj)  # idempotent
        with open(sp) as f:
            s = json.load(f)
        for ev in inst.EVENTS:
            cmds = [h["command"] for g in s["hooks"][ev] for h in g["hooks"] if inst.MARK in h["command"]]
            self.assertEqual(len(cmds), 1, ev)
        self.assertTrue(os.path.exists(sp + ".spike0-backup"))
        inst.uninstall(proj)
        with open(sp) as f:
            self.assertEqual(json.load(f), other)

    def test_uninstall_removes_file_we_created(self):
        proj = self.mkdir("fresh")
        inst.install(proj)
        inst.uninstall(proj)
        self.assertFalse(os.path.exists(os.path.join(proj, ".claude", "settings.local.json")))

    def test_never_touches_user_level_settings(self):
        home = self.mkdir("home")
        os.environ["HOME"] = home
        try:
            inst.install(self.mkdir("p"))
        finally:
            pass
        self.assertFalse(os.path.exists(os.path.join(home, ".claude")))


class TestStatusReport(HookCase):
    def test_status_unknown_when_no_hook(self):
        self.assertIn("BİLİNMİYOR", status(self.conn))

    def test_report_precision_with_n_and_no_healthy_claim(self):
        proj = self.mkdir("proj")
        self.bind((proj, "demo"))
        t = os.path.join(self.tmp, "t.jsonl")
        write_jsonl(t, [user("u1", "sr", proj, "Karar: birinci seçim bu olacak."),
                        user("u2", "sr", proj, "Önerim: ikinci olarak bunu ekleyelim lütfen.")])
        self.run_hook(self.payload("Stop", "sr", proj, t, last_assistant_message="x", prompt_id="1"))
        ids = [r["id"] for r in self.q("SELECT id FROM candidates ORDER BY id")]
        self.conn.execute("INSERT INTO review_events(candidate_id,decision,decided_at) VALUES(?,?,0)", (ids[0], "accept"))
        self.conn.execute("INSERT INTO review_events(candidate_id,decision,decided_at) VALUES(?,?,0)", (ids[1], "reject"))
        text = report(self.conn)
        self.assertIn("n=2", text)
        self.assertIn("n<30", text)
        self.assertNotIn("sağlıklı", status(self.conn).replace("'sağlıklı' demiyoruz", ""))

    def test_wilson_reference(self):
        lo, hi = wilson(30, 30)
        self.assertAlmostEqual(lo, 0.886, places=3)
        lo, hi = wilson(73, 73)
        self.assertAlmostEqual(lo, 0.950, places=3)


if __name__ == "__main__":
    unittest.main()
