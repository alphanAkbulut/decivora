"""Tracker tests: authority, freshness and read-only local boundaries, not product tests."""
import importlib.util
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

    def test_canonical_status_and_acceptance_not_inferred_from_test_pass(self):
        data = progress.build(self.root)
        self.assertEqual(len(data["tasks"]), 30)
        self.assertEqual(data["counts"], {"IN_PROGRESS": 3, "TODO": 27})
        self.assertEqual(data["worker_activity"], "unknown")
        self.assertEqual(data["evidence"]["status"], "recorded")
        self.assertFalse(data["evidence"]["production"])
        self.assertIn("Kabul", data["tasks"][0]["details"])
        self.assertEqual(len(data["engines"]), 10)
        self.assertTrue(all(e["status"] == "PLANNED_PRODUCTION" for e in data["engines"]))
        self.assertEqual(data["tasks"][14]["dependencies"], ["T14", "T07c"])

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
        path.write_text(path.read_text().replace("pending_capability_review", "pending_test_review"))
        after = progress.build(self.root)
        self.assertNotEqual(before["fingerprint"], after["fingerprint"])
        self.assertIn("pending_test_review", after["pending"][0]["reason"])
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
        self.assertEqual(second["counts"]["DONE"], 1)
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
