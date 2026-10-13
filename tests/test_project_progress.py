"""Tracker tests: authority, freshness and read-only local boundaries, not product tests."""
import importlib.util
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("project_progress", ROOT / "scripts/project_progress.py")
progress = importlib.util.module_from_spec(spec)
spec.loader.exec_module(progress)


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        report = json.loads((ROOT / progress.SOURCES[3]).read_text())
        for name in (*progress.SOURCES, *report["code_sha256"], "tools/progress/index.html"):
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        # Fresh *temporary test fixture*, not a rewrite of the repository's historical proof.
        # Tests of recorded/stale behavior must not depend on a live README retaining old bytes.
        report['code_sha256'] = {name: hashlib.sha256((self.root/name).read_bytes()).hexdigest()
                                 for name in report['code_sha256']}
        (self.root/progress.SOURCES[3]).write_text(json.dumps(report))

    def test_canonical_status_and_acceptance_not_inferred_from_test_pass(self):
        data = progress.build(self.root)
        self.assertEqual(len(data["tasks"]), 30)
        self.assertEqual(data["counts"], {"IN_PROGRESS": 5, "DONE": 7, "TODO": 18})
        self.assertEqual(next(t for t in data['tasks'] if t['id']=='T12')['status'], 'DONE')
        self.assertEqual(next(t for t in data['tasks'] if t['id']=='T13')['status'], 'TODO')
        self.assertEqual(data["tasks"][3]["status"], "DONE")
        self.assertEqual(data["tasks"][3]["dependencies"], ["T03c"])
        self.assertEqual(data["worker_activity"], "unknown")
        self.assertEqual(data["evidence"]["status"], "recorded")
        self.assertFalse(data["evidence"]["production"])
        self.assertIn("Kabul", data["tasks"][0]["details"])
        self.assertEqual(len(data["engines"]), 10)
        self.assertTrue(all(e["status"] == "PLANNED_PRODUCTION" for e in data["engines"]))
        self.assertEqual(data["tasks"][14]["dependencies"], ["T14", "T07c"])

    def test_active_risk_remains_visible_when_fixture_evidence_passed(self):
        path = self.root / progress.SOURCES[0]
        original = path.read_text()
        task = progress.build(self.root)["tasks"][2]
        old = task["details"].get("Risk durumu")
        self.assertIsNotNone(old)
        path.write_text(original.replace(old, "Observed / High · R20 test source failure", 1))
        data = progress.build(self.root)
        self.assertEqual(data["evidence"]["status"], "recorded")
        self.assertEqual(data["tasks"][2]["status"], "IN_PROGRESS")
        self.assertIn("Observed / High · R20 test source failure", progress.markdown(data))
        self.assertNotIn("R20 Closed", progress.markdown(data))

    def test_completed_small_deliveries_remain_separate_from_parent_gate(self):
        data = progress.build(self.root)
        task = next(t for t in data['tasks'] if t['id'] == 'T03')
        scoped = {s['id']:s for s in task['subtasks']}
        for sid in ('T03g','T03h','T03i','T03j'):
            self.assertEqual(scoped[sid]['status'], 'DONE')
            self.assertIn('| '+sid+' | T03 | DONE |', progress.markdown(data))
        self.assertEqual(task['status'], 'IN_PROGRESS')
        self.assertEqual(data['counts'].get('DONE', 0),
                         sum(t['status'] == 'DONE' for t in data['tasks']))
        self.assertNotIn('T03', [t['id'] for t in data['tasks'] if t['status'] == 'DONE'])

    def test_backlog_change_refreshes_data_and_generated_snapshot(self):
        before = progress.build(self.root)
        path = self.root / progress.SOURCES[0]
        path.write_text(path.read_text().replace("IN_PROGRESS / P0", "DONE / P0", 1))
        after = progress.build(self.root)
        self.assertEqual(after["tasks"][0]["status"], "DONE")
        self.assertNotEqual(after["fingerprint"], before["fingerprint"])
        self.assertNotEqual(progress.markdown(after), progress.markdown(before))

    def test_changed_evidenced_code_is_stale_not_green(self):
        path = self.root / "spikes/semantic-chain/protocol.py"
        path.write_text(path.read_text() + "\n# changed\n")
        data = progress.build(self.root)
        self.assertEqual(data["evidence"]["status"], "stale")
        self.assertIn("spikes/semantic-chain/protocol.py", data["evidence"]["stale_code"])

    def test_changed_evidenced_readme_is_stale_not_new_runtime_failure(self):
        path = self.root / 'spikes/semantic-chain/README.md'
        path.write_text(path.read_text() + '\nNew documentation.\n')
        data = progress.build(self.root)
        self.assertEqual(data['evidence']['status'], 'stale')
        self.assertEqual(data['evidence']['stale_code'], ['spikes/semantic-chain/README.md'])
        self.assertEqual(data['tasks'][2]['status'], 'IN_PROGRESS')

    def test_progress_note_refreshes_without_claiming_task_completion(self):
        before = progress.build(self.root)
        path = self.root / progress.SOURCES[0]
        original = path.read_text()
        old = before["tasks"][2]["details"]["Son ilerleme"]
        path.write_text(original.replace(old, "New bounded preparation; model not_run", 1))
        after = progress.build(self.root)
        self.assertNotEqual(before["fingerprint"], after["fingerprint"])
        self.assertEqual(after["counts"], before["counts"])
        self.assertEqual(after["tasks"][2]["status"], "IN_PROGRESS")
        self.assertIn("New bounded preparation; model not_run", progress.markdown(after))
        self.assertNotIn("New bounded preparation; model not_run", progress.markdown(before))

    def test_preparation_and_gate_updates_refresh_without_model_evidence(self):
        before = progress.build(self.root)
        path = self.root / progress.SOURCES[1]
        text = path.read_text()
        text = text.replace(before["pending"][0]["reason"], "pending_test_review", 1)
        text = text.replace(before["delivered"][0]["output"], "prepared_test_revision", 1)
        path.write_text(text)
        after = progress.build(self.root)
        self.assertNotEqual(before["fingerprint"], after["fingerprint"])
        self.assertIn("pending_test_review", after["pending"][0]["reason"])
        self.assertEqual(after["delivered"][0]["output"], "prepared_test_revision")
        self.assertEqual(after["evidence"]["model"], "not_run")
        self.assertEqual(after["counts"], before["counts"])

    def test_missing_report_is_unknown(self):
        (self.root / progress.SOURCES[3]).unlink()
        evidence = progress.build(self.root)["evidence"]
        self.assertEqual(evidence["status"], "unknown")
        self.assertIsNone(evidence["tests"])

    def test_inconsistent_test_report_is_incomplete(self):
        path = self.root / progress.SOURCES[3]
        report = json.loads(path.read_text())
        report["total_tests"] += 1
        path.write_text(json.dumps(report))
        self.assertEqual(progress.build(self.root)["evidence"]["status"], "incomplete")

    def test_unrecorded_subtask_status_is_explicit(self):
        path = self.root / progress.SOURCES[0]
        path.write_text(path.read_text() + "\n| T01zz / T01 | test scope without state | test AC |\n")
        child = progress.build(self.root)["tasks"][0]["subtasks"][-1]
        self.assertEqual(child["status"], "UNSPECIFIED")

    def test_bad_metadata_or_duplicate_subtask_fails_closed(self):
        path = self.root / progress.SOURCES[0]
        original = path.read_text()
        path.write_text(original.replace("IN_PROGRESS / P0.", "invalid metadata", 1))
        with self.assertRaises(ValueError):
            progress.build(self.root)
        path.write_text(original + "\n| T01zz / T01 | TODO | AC |\n| T01zz / T01 | TODO | AC |\n")
        with self.assertRaises(ValueError):
            progress.build(self.root)

    def start_server(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), progress.make_handler(self.root))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        def stop():
            server.shutdown()
            server.server_close()
            thread.join()
        self.addCleanup(stop)
        return "http://127.0.0.1:" + str(server.server_port)

    def test_api_rereads_sources_without_restart_or_model_dispatch(self):
        base = self.start_server()
        with urlopen(base + "/api/status") as response:
            first = json.load(response)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
        path = self.root / progress.SOURCES[0]
        path.write_text(path.read_text().replace("IN_PROGRESS / P0", "DONE / P0", 1))
        with urlopen(base + "/api/status") as response:
            second = json.load(response)
        self.assertNotEqual(first["fingerprint"], second["fingerprint"])
        self.assertEqual(second["counts"]["DONE"], first["counts"].get("DONE", 0) + 1)
        self.assertEqual(second["evidence"]["model"], "not_run")

    def test_api_has_no_write_filesystem_or_cross_origin_access(self):
        base = self.start_server()
        before = (self.root / progress.SOURCES[0]).read_bytes()
        for request, expected in [
            (Request(base + "/api/status", method="POST", data=b"done"), 405),
            (Request(base + "/docs/delivery/backlog.md"), 404),
            (Request(base + "/../AGENTS.md"), 404),
            (Request(base + "/api/status", headers={"Host": "untrusted.example"}), 403),
            (Request(base + "/api/status", headers={"Origin": "https://untrusted.example"}), 403),
        ]:
            with self.assertRaises(HTTPError) as raised:
                urlopen(request)
            self.assertEqual(raised.exception.code, expected)
            raised.exception.close()
        self.assertEqual(before, (self.root / progress.SOURCES[0]).read_bytes())

    def test_api_source_failure_is_503_not_old_success(self):
        base = self.start_server()
        (self.root / progress.SOURCES[0]).unlink()
        with self.assertRaises(HTTPError) as raised:
            urlopen(base + "/api/status")
        self.assertEqual(raised.exception.code, 503)
        raised.exception.close()


if __name__ == "__main__":
    unittest.main()
