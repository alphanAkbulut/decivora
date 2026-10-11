#!/usr/bin/env python3
"""Read-only development tracker. Canonical backlog remains the authority."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/alphanAkbulut/decivora/blob/main/"
SOURCES = (
    "docs/delivery/backlog.md", "docs/delivery/implementation-readiness.md",
    "docs/architecture/engines.md", "docs/quality/semantic-readiness-results.json",
)
OUTPUT = "docs/delivery/progress.md"


def table(text, heading):
    section = text.split(heading, 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r"[-: ]+", c) for c in cells):
            continue
        rows.append(cells)
    return rows[1:]


def build(root=ROOT):
    raw = {name: (root / name).read_bytes() for name in SOURCES[:3]}
    report_path = root / SOURCES[3]
    raw[SOURCES[3]] = report_path.read_bytes() if report_path.exists() else b""
    texts = {name: value.decode("utf-8") for name, value in raw.items()}
    backlog = texts[SOURCES[0]]
    headings = list(re.finditer(r"^## (T\d+) — ([^\n]+)\n", backlog, re.M))
    tasks = []
    for i, h in enumerate(headings):
        section = backlog[h.end():headings[i + 1].start() if i + 1 < len(headings) else len(backlog)]
        meta = re.search(r"- \*\*Durum / faz:\*\* ([^/.\n]+) / ([^.]+)\. \*\*Bağımlılık:\*\* ([^.]+)\.", section)
        if not meta:
            raise ValueError("Eksik görev metadatası: " + h.group(1))
        state, phase, deps = (x.strip() for x in meta.groups())
        details = {m.group(1): m.group(2) for m in re.finditer(r"^- \*\*([^*]+):\*\* (.+)$", section, re.M)}
        tasks.append({"id": h.group(1), "title": h.group(2), "status": state,
                      "phase": phase, "dependencies": re.findall(r"T\d+[a-z]*", deps),
                      "details": details, "subtasks": [], "url": REPO_URL + SOURCES[0]})
    if len(tasks) != 30 or len({t["id"] for t in tasks}) != 30:
        raise ValueError("30 ayrı ana görev bekleniyor; bilinmeyen durum başarı sayılamaz")
    by_id = {t["id"]: t for t in tasks}
    seen = set()
    for line in backlog.splitlines():
        match = re.match(r"^\| (T\d+[a-z]+) / ([^|]+) \| (.+)$", line)
        if not match:
            continue
        sid, deps, rest = match.groups()
        if sid in seen:
            raise ValueError("Tekrarlı alt görev: " + sid)
        seen.add(sid)
        parent = re.match(r"T\d+", sid).group()
        if parent not in by_id:
            raise ValueError("Alt görev parent bulunamadı: " + sid)
        cells = [c.strip() for c in rest.rstrip("|").split("|")]
        state = re.search(r"\b(IN_PROGRESS|TODO|DONE|COMPLETED|PROPOSED|BLOCKED|CANCELLED)\b", cells[0])
        by_id[parent]["subtasks"].append({"id": sid, "dependencies": deps,
            "status": state.group() if state else "UNSPECIFIED", "scope": cells[0],
            "acceptance": " · ".join(cells[1:])})
    readiness = texts[SOURCES[1]]
    delivered = [{"title": row[0], "output": row[1], "verification": row[2],
                  "url": REPO_URL + SOURCES[1]} for row in table(readiness, "## Beklemeyen işler: uygulandı")]
    pending = [{"title": row[0], "kind": row[1], "reason": row[2], "next": row[3],
                "url": REPO_URL + SOURCES[1]} for row in table(readiness, "## Kalanlar: kimin neye karar vermesi gerekiyor?")]
    engines = []
    for line in texts[SOURCES[2]].splitlines():
        if not re.match(r"^\| ENG-\d+ ", line):
            continue
        row = [c.strip() for c in line.strip("|").split("|")]
        eid, name = row[0].split(" ", 1)
        engines.append({"id": eid, "name": name, "flow": row[1], "authority": row[2],
                        "failure": row[3], "plan": row[4], "status": "PLANNED_PRODUCTION",
                        "tasks": re.findall(r"T\d+", row[4]), "url": REPO_URL + SOURCES[2]})
    if len(engines) != 10:
        raise ValueError("10 engine sözleşmesi bekleniyor")
    report = json.loads(texts[SOURCES[3]]) if raw[SOURCES[3]] else {}
    code_hashes = report.get("code_sha256", {})
    stale = []
    for name, digest in code_hashes.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError("Repo dışı kanıt yolu")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            stale.append(name)
    suites = report.get("suites", [])
    total = report.get("total_tests")
    evidence_state = "unknown"
    if report:
        evidence_state = "stale" if stale else "recorded"
        if (not code_hashes or not suites or any(s.get("status") != "passed" for s in suites)
                or not isinstance(total, int) or total != sum(s.get("tests", 0) for s in suites)):
            evidence_state = "incomplete"
    hashes = {name: hashlib.sha256(value).hexdigest() for name, value in raw.items()}
    # Include current evidenced code, so changing code invalidates the view without editing reports.
    fingerprint = hashlib.sha256(json.dumps({"sources": hashes, "stale_code": stale}, sort_keys=True).encode()).hexdigest()
    return {"schema_version": 1, "fingerprint": fingerprint, "source_hashes": hashes,
            "stage": "Açık çalışma fazı: " + (", ".join(sorted({t["phase"] for t in tasks if t["status"] == "IN_PROGRESS"})) or "kayıt yok"), "tasks": tasks,
            "counts": dict(Counter(t["status"] for t in tasks)), "delivered": delivered,
            "pending": pending, "engines": engines, "worker_activity": "unknown",
            "evidence": {"status": evidence_state, "date": report.get("date"), "tests": total,
                "suites": suites, "stale_code": stale,
                "model": report.get("semantic_model_dispatch", "unknown"),
                "human_gold": report.get("human_gold", "unknown"),
                "native": report.get("native_comparison", "unknown"),
                "production": report.get("production_runtime"), "url": REPO_URL + SOURCES[3]}}


def markdown(data):
    lines = ["# Proje ilerleme görünümü", "", "> Otomatik üretilir. Ana kaynak backlog’dur; bu dosyayı elle düzenleme.", "",
        "**" + data["stage"] + "**", "",
        "[Canlı yerel ekranı açma ve güncelleme rehberi](progress-guide.md). GitHub bu Markdown görünümünü gösterir; canlı ekran yerel dosyaları izler.", "",
        "`IN_PROGRESS` açık çalışma kaydıdır; bir agent’ın şu anda çalıştığını göstermez. Plan ön koşulları otomatik teknik blocker değildir. Test sayısı ürün tamamlanma yüzdesi değildir.", "",
        "| Ana görev durumu | Sayı |", "|---|---|"]
    lines += ["| " + status + " | " + str(count) + " |" for status, count in sorted(data["counts"].items())]
    lines += ["", "## Açık fazda neler değişti?", "", "Ana görev kapanışı ile hazırlık/kod/ölçüm ilerlemesi ayrıdır. Aşağıdaki kayıtlar backlog'dan gelir; canlı agent etkinliği değildir.", ""]
    for task in data["tasks"]:
        if task["status"] != "IN_PROGRESS":
            continue
        lines += ["### " + task["id"] + " · " + task["title"], "",
                  task["details"].get("Son ilerleme", "Son ilerleme kaydı yok."), "",
                  "**Aktif teknik risk:** " + task["details"].get("Risk durumu", "Bu görev için ayrı risk kaydı yok; risksiz olduğu anlamına gelmez."), "",
                  "**Denemeler / sonuç:** " + task["details"].get("Denemeler / sonuç", "Ayrıntılı kaynak kayıtlarını kontrol et."), "",
                  "**Etkilenen iş:** " + task["details"].get("Etkilenen iş", "Backlog kabul ve bağımlılıkları geçerli."), "",
                  "Sıradaki adım: " + task["details"].get("Sıradaki adım", "Ayrıntılı backlog'u kontrol et."), ""]
    lines += ["", "## Mevcut teslim parçaları", "", "Bunlar P0 hazırlığı ve kontrollü deney kodudur; tamamlanmış production engine/MVP değildir.", ""]
    lines += ["- **" + row["title"] + "** — " + row["output"] + "; " + row["verification"] for row in data["delivered"]]
    lines += ["", "## Açık karar ve doğrulama kapıları", "", "| Konu | Etkisi | Sonraki adım |", "|---|---|---|"]
    lines += ["| " + r["title"] + " | " + r["reason"] + " | " + r["next"] + " |" for r in data["pending"]]
    lines += ["", "## Fazlara göre tüm ana işler", "", "| ID | Faz | Durum | İş | Plan ön koşulu | Alt dilim |", "|---|---|---|---|---|---|"]
    lines += ["| " + t["id"] + " | " + t["phase"] + " | " + t["status"] + " | " + t["title"] + " | " + ", ".join(t["dependencies"]) + " | " + str(len(t["subtasks"])) + " |" for t in data["tasks"]]
    e = data["evidence"]
    lines += ["", "## Kanıt kapsamı", "", f"Kayıt durumu: **{e['status']}**; rapor tarihi: {e['date']}; kayıtlı test sayısı: {e['tests']}. Kaynak raporun tarihsel model kaydı: {e['model']}; insan gold: {e['human_gold']}; native kıyas: {e['native']}. Production runtime: {e['production']}.", "",
        "Güncel model denemesi T03 son ilerleme kaydındadır. Bu alan kaynak raporun tarihsel checkpoint’idir. Kod hash kontrolü yalnız raporun listelediği dosyaları kapsar; bütün repo veya güncel CI sonucu değildir. [Kaynak rapor](../quality/semantic-readiness-results.json).", "",
        "Görev kabul kriterleri, doğrulama ve alt görevler [kanonik backlog](backlog.md) içinde; 10 production engine [engine sözleşmesinde](../architecture/engines.md) planlıdır.", "",
        "Kaynak fingerprint: `" + data["fingerprint"] + "`", ""]
    # Preserve links from source tables, correcting their original relative base (same delivery folder).
    return "\n".join(lines)


def make_handler(root=ROOT):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # No request/query/transcript logging.

        def send(self, status, content, kind):
            self.send_response(status)
            self.send_header("Content-Type", kind + "; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            port = self.server.server_port
            if self.headers.get("Host") not in {f"127.0.0.1:{port}", f"localhost:{port}"}:
                self.send(403, b"Forbidden host", "text/plain")
                return
            origin = self.headers.get("Origin")
            if origin and origin not in {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}:
                self.send(403, b"Forbidden origin", "text/plain")
                return
            route = urlsplit(self.path).path
            if route == "/":
                self.send(200, (root / "tools/progress/index.html").read_bytes(), "text/html")
            elif route == "/api/status":
                try:
                    data = build(root)
                    data["observed_at"] = datetime.now(timezone.utc).isoformat()
                    self.send(200, json.dumps(data, ensure_ascii=False).encode(), "application/json")
                except (ValueError, OSError, KeyError, IndexError):
                    self.send(503, b'{"error":"Kaynak okunamadi; onceki veri guncel kabul edilmemeli."}', "application/json")
            else:
                self.send(404, b"Not found", "text/plain")

        def do_POST(self):
            self.send(405, b"Read only", "text/plain")
        do_PUT = do_DELETE = do_PATCH = do_POST
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.serve:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler())
        print(f"Decivora: http://127.0.0.1:{server.server_port} (read-only; local files)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    else:
        data = build()
        content = markdown(data)
        if args.write:
            (ROOT / OUTPUT).write_text(content, encoding="utf-8")
            print("Generated " + OUTPUT)
        elif args.check:
            if not (ROOT / OUTPUT).exists() or (ROOT / OUTPUT).read_text(encoding="utf-8") != content:
                raise SystemExit("STALE: python3 scripts/project_progress.py --write")
            print("PASS: progress matches canonical sources and recorded evidence")
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
