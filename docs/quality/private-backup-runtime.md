# Private local backup download — T23a slice

**14 October 2026 — current local implementation.** [Code](../../packages/storage/local_backup.py), [UI/server](../../apps/local_ui/server.py), [HTTP tests](../../tests/runtime/test_local_app.py), [real download test](../../tests/ui-backup.cjs).

Sources view has a private-backup section. An explicit acknowledgment precedes POST /api/backup; current local-human session, exact Origin/Host, CSRF and shared30/minute write limiter apply. GET and caller paths are rejected; one backup may run at a time. The8MiB SQLite and64KiB manifest development ceilings bound local resources; they are not measured capacity guarantees. Existing data is not deleted on rejection.

The bundle contains exactly workspace.sqlite + manifest.json. It preserves original source text, local permissions, questions, decisions, stage/evidence and event history. It is **unencrypted and private**, not a secret-redacted shareable export. UI session cookie/bootstrap live only in server memory and are not in the database. No API key is configured or copied by this feature; if users themselves pasted secrets into source text, a private backup retains that source text. Never publish these bundles in GitHub. Public/redacted export, encrypted backup, retention/purge/migration and active restore UX remain T23 work.

Existing consistent snapshot backup performs source/project access checks, integrity and projection digests. Before download, the package is restored into a new throwaway file: SHA, source hashes, event replay/projection and foreign-key integrity are checked, with zero external dispatches. Exact ZIP members and bounded uncompressed sizes reject path traversal/duplicates/oversized members; current ACL is rechecked before returning bytes. All temporary files are cleaned. Multi-workspace local export is rejected; no arbitrary file selection or active database overwrite endpoint is introduced.

The button prepares a download; browser/user download success is not claimed just from an HTTP200. Backend and actual browser download are separately checked. A restore-check validates this snapshot; it does not replace future OS/migration/purge/operational recovery testing or prove a user's device backup strategy. T23 starts; full acceptance remains open. Automatic extraction/API quality remain pending. No new paid model, third-party connection or shell runner.

The existing local UI architecture graph retains the same authenticated-server/private-SQLite boundaries; the new endpoint adds no schema/table or external actor. Full diagram source inventory is checked separately; a duplicate diagram is unnecessary for this small endpoint.

## Verification

[Machine record](private-backup-results.json):263runtime +46tracker tests; actual isolated browser download saved locally and its ZIP was separately restored/validated offline. Required acknowledgment makes no request before selection; one acknowledged request/download; desktop/mobile no viewport overflow. HTTP guards, current source/task/question retention, session-secret exclusion, restored hashes/projections, corruption/traversal/oversize, concurrent backup, rate limit and ACL denial covered. Five new runtime tests use fixtures, not user data. Existing43Mermaid hashes/inventory unchanged; no new diagram needed. No paid model/external dispatch.
