# Concurrent storage, audit read reuse and decision impact UI —14October2026

**Implemented and locally verified.** User authorized503fix, API-independent work, tests and docs/schema/diagrams. No paid provider/native capture/root grant or real transcript imported. This delivery implements a controlled SQLite lock mechanism fix, targeted read optimization, and explicit manual decision-hypothesis UI. Full semantic extraction/AND-OR authoring/impact approval+cancel application/native adapter remain separate open tasks.

##503mechanism and correction

Controlled temporary database: old read transaction held open; writer ready to commit; new state read started. Rollback journal mode produced503after2126ms with safe diagnostic OperationalError:database is locked. LocalApp now selects/checks WAL once at startup before HTTP serving. Same ordered fixture returned200in20ms. These are single mechanistic observations, not latency guarantees. The original uninstrumented mixed-run failure has no underlying trace: compatible mechanism demonstrated, historical exact cause not proved.

No timeout increase, indefinite retry, hidden fallback or permission weakening. Initialization refuses a journal mode other than wal. WAL is a local same-host file profile, not network-drive/distributed DB support or simultaneous multiwriter support. SQLite lock/corruption/disk exhaustion can still fail; do not claim every possible503is eliminated. Current live journal queried read-only after restart iswal; records remained0, no fixture seeding into user workspace. Startup/reactivation changes session normally and preserves canonical data/schema1.

Two real SQLite/HTTP regressions: restart from existing delete-mode data enableswalwithout changing task/snapshot; old reader retains old snapshot while writer commits and HTTP sees the committed record. Existing backup/restore/current ACL/transaction rollback and workflow tests passed.

## Read optimization and same-fixture comparison

TaskWorkflow grouped audit rows by project/action/task only inside a current owned read_snapshot. Repeated consumers reuse that snapshot; returned structures are copied to avoid cache poisoning. Transaction writes do not use it; cache is discarded after read and subsequent requests reread. Current authority/source/version checks unchanged. Cache negative regression covers returned-object tamper, write disable and next-query freshness.

| Same workload | Old single median ms | New single median ms | Old4-reader median ms | New4-reader median ms |
|---|---:|---:|---:|---:|
| small_mixed | 59.966 | 15.587 | 457.256 | 88.243 |
| medium_mixed | 181.556 | 50.551 | 923.1 | 160.29 |
| dense_mixed | 438.581 | 132.969 | 1097.918 | 259.569 |

[Before](mixed-load-results.json), [afterWAL/audit-cache](mixed-load-after-wal-audit-cache.json): identical fixture descriptions/counts, script unchanged, full after groups all200; sources preserved, overflow/oversize rejected, falseDone0. These measurements preceded the added decision-impact state/UI slice, so do not claim full impact-history throughput from them. Short developer-machine samples and100record preview cap remain; not production SLO/100k-history proof. No claim that one change alone caused the combined measured gain.

## Manual decision impact UI / current boundary

Questions and decisions view: select an existing Decision, preview the hypothesis that it stops being valid, then inspect reason paths/currentness. Human+projectwrite capability required because the preview stores audit. Record version, project base and current authority/source coverage checked. Expected knowledge revision is rechecked inside the existing persisted-preview transaction, including a prepare→persist race test. Result survives reload; canonical state/task lane/decision unchanged. Latest5recorded previews shown; stale ones retained/labeled.

Facts are an explicitly manual hypothesis. Other facts unknown, missing rationale remains review, historical Done is preserved; no invented AND/OR expression, cancellation or replacement. Partial source/graph coverage comes from the existing kernel and stays visible. This is a working bridge into our impact engine, not real LLM extraction or complete approval/apply integration. Existing MCP draft remains create-only; no new agent authority/tool granted.

[Request schema](../../manifests/local-decision-impact.schema.json) matches actual service arguments; SQL schema and existing MCP definitions/TaskStage v2 payload unchanged. UI strings EN/TR; newES/PT-BR/ARlabels fall back toEnglish pending native review. Synthetic browser verifies linked task/reason path, persisted preview, unchanged ToDo and no page errors.

## Validation and remaining checks

318runtime +48tracker/evaluation tests passed,7fixture browser flows passed (localization/workflow/backup/routing-graph/file-agent/project-selection/newimpact). [Machine evidence](concurrency-impact-results.json). Source-only ZIP43files, noDB/credentials/transcripts; clean-machine install/platform limits still open. Changed local-preview Mermaid rendered/XML/hash/title/description/visually inspected; remaining inventory checked, not all diagrams rerendered.

Remaining: real inference transport/quality and token counters require existing access/budget decisions; full source-aware impact review/apply and next-action explanation remain API-free implementation scope; native MCP/capture requires selectedhost/currentgrant. Longer soak/disk/crash/coverage/retention checks and original503correlation remain. No main-task closure or scope reduction from fixture success. Use existingT15/T20/T23d and T13/T19 ownership instead of duplicate tasks.
