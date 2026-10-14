# Local performance measurement —14October2026

**Conclusion:** the measured small/current localhost views are responsive. This is a bounded developer-machine observation, not a capacity guarantee or production SLO. Product live workspace contains0tasks; tracker contains30main/129subtasks. No user task/source mutation or model call; same local application session refreshed normally. No secrets, payload contents or user source text are included in these results.

## HTTP response latency

Times include new connection, response headers and complete body download. TTFB is additionally in the JSON. One warm-up per group excluded. Median is typical; p95 describes upper samples, not maximum future latency.

| Service/endpoint | Parallel workers | Samples | Median ms | p95 ms | Max ms |
|---|---:|---:|---:|---:|---:|
| tracker / | 1 | 30 | 0.496 | 1.93 | 2.944 |
| tracker /api/status | 1 | 30 | 5.203 | 12.31 | 13.868 |
| product / | 1 | 30 | 0.381 | 2.89 | 12.167 |
| product /app.js | 1 | 30 | 0.306 | 0.959 | 1.515 |
| product /api/state | 1 | 30 | 1.236 | 4.339 | 14.922 |
| tracker /api/status | 4 | 32 | 20.562 | 55.315 | 55.951 |
| product /api/state | 4 | 32 | 4.411 | 16.597 | 16.731 |

All measured responses were HTTP200. This includes basic session/state/static reads, not provider calls or mutation latency. Four workers simulate short overlapping reads, not4real humans, tenant scale or long-duration load.

## Browser readiness

Independent headless Chrome context, desktop1440×1000. First load is one sample with fresh context, not a statistically established cold-start number. Later readings use10real page.reload operations, not same-document fragment navigation. Readiness means loaded status/project data, not LCP/paint/mobile interaction. Browser automation/control overhead is included.

| Surface | First ready ms (n=1) | Reload median ms | Reload p95 ms | Board switch median ms | Page errors |
|---|---:|---:|---:|---:|---:|
| tracker | 193.13 | 34.34 | 49.75 | not measured | 0 |
| product | 169.49 | 133.47 | 188.81 | 34.37 | 0 |

The first browser attempt incorrectly used repeated fragment navigation for the product, yielding2.57ms median. This was a harness issue and the value was rejected; explicitly reloading produced133.47ms median. Do not cite the rejected number as product load performance. User's in-app browser tab/GPU/extension state was not measured by this isolated Chrome run.

## Synthetic state size

Separate temporary database, synthetic manual Task titles/descriptions, no file root, model, real source, dependency edges or completed AC history. Dataset creation excluded from request timings; no user's database seeded.12requests/group plus one excluded warm-up. At12samples, nearest-rank p95 equals max; tail confidence is limited. Browser and synthetic groups overlapped in the first measurement; scheduling/contention can affect the150-task outlier, so194.892ms is not established intrinsic worst-case latency.

| Stored tasks | Returned tasks | Truncated | Median ms | p95/max ms |
|---|---:|---|---:|---:|
| 10 | 10 | False | 3.094 | 3.739 |
| 50 | 50 | False | 15.728 | 16.265 |
| 100 | 100 | False | 43.494 | 50.89 |
| 150 | 100 | True | 57.076 | 194.892 |

**100record preview limit matters:**150stored tasks returns only100withtruncated=true. Faster bounded rendering is not evidence that every task is displayed/assessed. Global audit/history still grows. No claim about1000/100k events or high-volume model processing follows from this run.

## Findings and suggested next work (not applied)

- Live endpoints are not the observed bottleneck in this small snapshot. If the user sees multi-second delays, reproduce in the affected in-app tab and correlate request timing/browser errors/rendering; don't attribute them to the model/DB from these results alone.
-100returned synthetic tasks cause4452SQLite execute calls in one profiled state snapshot; workflow stage/evidence, acceptance and repeated current scope checks contribute.150stored tasks still yields4452calls for100returned rows but greater cumulative SQL time. Profile instrumentation adds overhead; its wall-clock time is not the unprofiled endpoint median.
- Consider per-snapshot read reuse and bulk audit/criterion reads inside the existing read transaction. Current authority/revision checks and source ACL must remain; never cache authorization across commits or skip permission checks for speed. Measure before/after with identical fixtures and negative revocation tests. No optimization/refactor in this diagnosis.
- Tracker response is about106kB and reparses/hashes source documents; current5.203ms median is acceptable for this use. Its15second polling interval is refresh scheduling, not a15second server response. Manual refresh reads now. Lightweight caching only if future measured need justifies it.
- Product frontend asset serving and first load remain local; no native capture/model latency measured. An API/CLI extractor would need separate inference, queue-wait, retries, output binding, approval and verification timing.

## Mandatory later performance checks

1. Dense and long-lived relations/audit/AC/source histories, private source scopes and changed evidence; clarify pagination coverage beyond100records.
2. Approved file-root checks (up to16reads/snapshot), concurrent writers/readers, revoked grants, diskfull/busy/restore/cold start, long soak and memory/CPU.
3. Actual in-app browser, mobile/RTL,100task DOM interactions/search/detail/graph; measure LCP/long tasks/keyboard latency and source-update-to-visible latency.
4. Queue burst/catch-up and actual model/provider response/usage under explicit permission/budget; split upstream delay from our processing time.
5. Repeat representative groups sequentially on idle machine with larger samples before setting p95/p99/SLO or capacity/cost promises.

## Reproduction and evidence

[HTTP/synthetic/profile results](local-performance-results.json), [browser results](local-performance-browser.json). Original bounded scripts: [measurement](../../scripts/measure_local_performance.py), [browser measurement](../../tests/ui-performance.cjs). Use a private live session-file path in --session-file; never commit that file/bootstrap/cookie. Scripts output aggregate metrics only. No third-party application/model installed or activated. Existing T23d/T24l/T20 performance scopes cover follow-up; no duplicate task or closure created.
