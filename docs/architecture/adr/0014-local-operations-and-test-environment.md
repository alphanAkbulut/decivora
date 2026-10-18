# ADR-0014 — Local Operations and separate TEST environment

**Accepted local direction — 19 October2026.** The human approved implementation of the proposed read-only Operations view, persistent safe error diagnostics, stage tracing and separate test launcher, together with documentation/diagrams and GitHub commit. This grants no paid API, external collector, production access or new security-policy exception.

## Alternatives and decision

Per-operation microservices would multiply deployment, network, retry and consistency boundaries before the core user flow is accepted. Keep logical engines as modules in the current local application; a background worker may later be separated when actual asynchronous workloads justify it. No automatic promise that service extraction is trivial. Current Operations reports only this application, not a complete OS/service inventory.

Do not mix diagnostic traces into canonical domain events or claim operational success is product completion. Use a separate private SQLite diagnostics sidecar with allowlisted labels, no free-text bodies, bounded run/error retention, visible loss/eviction and measured command boundaries. A telemetry failure does not grant permission or reverse a committed canonical result. Security/audit transactions retain their existing stronger requirements. OpenTelemetry-compatible detailed spans/collector are future integration; no new runtime dependency is installed.

For local manual testing, choose a separate TEST DB, marker, port and session-cookie name rather than adding dummy records to the user's workspace. Existing unmarked/local-marked DBs cannot be silently adopted as TEST. TEST starts without model/file-target configuration and is labelled by the server before hydration. This is not a container or OS sandbox, hosted staging or a paid-model testing grant.

## Consequences and validation

The initial trace records project authorization and component command execution; receipt/job/model/review/evidence joins and inner engine spans remain open.200run/100error-group bounds are development protection defaults, not a production retention decision. Diagnostic backups, incident lifecycle/actions, remote export and team operator-role UI remain open. T20/T21/T23/T24 parent acceptance is not closed by this delivery.

[Runtime scope, architecture/sequence diagrams and tests](../../quality/operations-runtime.md) document restart, safe-code redaction, authorization, loss, eviction, environment refusal, actual launcher and browser/cookie coexistence checks. A source ZIP contains code/launchers only; real user data, session secrets and private backups are excluded from publication.
