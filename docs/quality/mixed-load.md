# Mixed-load measurement and stage plan —14October2026

**Do this now, repeat before release.** This is the first representative local-volume/relationship/history/concurrency measurement. It exposes risks early; it is neither a long-duration stress test nor proof that the MVP, security or semantic model quality is accepted. No user database, transcript, native client, file root or model modified/activated. All fixtures used temporary databases and unchanged production code paths.

## Workload / measured responses

Three independently created fixtures: Task and Decision records, required_by reasons and acyclic depends_on links;100/300/900record-update events;4/12/32source receipts;5AC/DoD contracts and50alternating criterion evidence records, with explicit implementation handoff; DoD incomplete and prerequisites unverified.12additional committed update operations overlap24HTTP reads. Payloads are unique synthetic ASCII byte-volume filler (not real conversation semantics/Unicode or authenticated multiuser sessions). No extractor called. Fixture creation excluded from response measurements.

| Profile | Tasks / decisions | Sources / total bytes | Relations | Domain events / audit rows before concurrent writes | Single-read median / p95 ms | Four-reader median / p95 ms | Reads during writes median / p95 ms |
|---|---|---|---:|---|---|---|---|
| small_mixed | 30 / 5 | 4 / 4000 | 59 | 199 / 409 | 59.966 / 83.743 | 457.256 / 663.535 | 834.438 / 1167.194 |
| medium_mixed | 60 / 10 | 12 / 72000 | 177 | 552 / 947 | 181.556 / 246.495 | 923.1 / 1038.276 | 1591.204 / 1904.491 |
| dense_mixed | 100 / 10 | 32 / 380800 | 394 | 1409 / 2327 | 438.581 / 504.272 | 1097.918 / 1453.509 | 1141.775 / 1352.113 |

20sequential requests and24requests/four-reader group; one excluded warm-up per HTTP group. Mixed group has24read requests plus12writer operations. These are short controlled bursts, not sustained throughput/p99/SLO evidence. Concurrency includes local Python client/server scheduling and SQLite activity. Non-monotonic differences between medium/dense writer latency cannot establish causality from one run.

## Correctness and observed failure

- Complete measured run: every sequential/parallel/mixed read returned200.24successful mixed reads per profile retained correct selected project/source count and bounded records. After writes all4/12/32source receipts remained, required unverified dependencies remained finish-blocked, and no returned task was falsely Done.
- Oversized12001byte input was rejected in all three profiles. The33rdsource was rejected in the32-source profile and prior accepted32remained. No data deleted to fit a limit.
-110records in dense fixture exceed100record preview: returned records100, tasks less than100because decisions share the same bounded result. truncated=true is explicit. Do not report these timings as exhaustive110record evaluation/rendering.
- **Unresolved intermittent503:** an earlier attempt failed during HTTP read/write overlap. That run stopped before a complete aggregate result; failure rate and root exception were not captured. A later run with safe exception counters returned all200and no exceptions, so root cause remains unknown. Do not erase the earlier failure or describe it as fixed. Lock/contention is a candidate, not a confirmed cause; swallowed storage exceptions/context-open behavior must be traced in a focused reproducer.
- Setup first tried criterion evidence before implementation handoff and correctly hit evidence_stage_required; fixture now follows transitions. A Python harness variable also shadowed concurrent module and was renamed. These two preparation problems are not product load failures.
- Count checks do not certify complete event/projection integrity under crashes, permissions revocation, cancellation or lost acknowledgments. Existing correctness tests remain separate; richer load correctness is a release gate.

## Findings / existing task owners

1. **P1 now — T20/T23d:** current source/audit/graph complexity increases whole-state read cost: dense439msmedian versus simple100task43ms earlier. Those fixtures differ in more than one variable, so this is an aggregate comparison, not proof of one bottleneck. Existing per-task query/history/source scans merit profiling and bulk snapshot reads. Preserve current authorization/source isolation/revision checks; no permission caching across commits.
2. **P1 now — T15/T23d:** reproduce intermittent503with bounded counters/exception classes and request/transaction correlation on fixtures. Investigate read/write lock lifetime, current2second connection timeout, journal mode and context initialization. Do not simply raise timeout, swallow errors, retry indefinitely or change production SQLite settings from this report.
3. **P1 before pilot — T18/T20:**100record and32source preview limits affect completeness. Explicit pagination/delta/coverage must be designed/tested; faster truncated views do not mean full processing capacity. Native/cross-project scoped context remains separate.
4. **P1 before release — T24l/T15:** repeated larger/fair batches on idle hardware, long soak/memory/disk/cold-start, more workers and actual in-app/mobile rendering. Check exact final revisions/event/source/projection consistency and zero unauthorized/false closure under load.
5. **First authorized model integration — T09/T21:** add provider latency, queue wait, retry/unknown usage and token/monetary budget measurement. This API-free test says nothing about LLM throughput or cost. Full capture/native permission needed before real transcript ingress.
6. **P2/P4:** larger retained histories and team/cloud tenant fairness/isolated sessions/quotas; only after earlier local findings resolved. No need to postpone all performance work to those phases.

No optimization or runtime/config change made in this diagnosis. Existing task ownership used; no duplicate task, fake parent closure or new user approval invented. Later optimization requires its concrete scope/recovery/negative test plan.

## Evidence and reproduction

[Aggregate measurements, script hash and safe exception history](mixed-load-results.json); [bounded isolated script](../../scripts/measure_mixed_load.py). Run from repo root with Python3.12: python3 -B scripts/measure_mixed_load.py --output docs/quality/mixed-load-results.json. The script opens only temporary localhost fixture servers; no live session file/key/import access. Rerunning has CPU/disk cost but no provider dispatch. Original [simple/live benchmark](local-performance.md) remains separate historical evidence.
