# Security Policy

**14 October 2026 — local development profile.** This policy describes review boundaries and required properties; it is not executable authorization, a completed audit, a security certification or a production release claim.

## System and Scope

Decivora preserves project decisions, tasks, sources and evidence with current project state and append-only domain/audit history. Current application is a single-owner local Python/SQLite preview. The product HTTP server binds to127.0.0.1. A separate development tracker also runs locally and exposes repository planning metadata; it is read-only and not a multiuser authenticated service.

Root policy covers the repository, including apps/local_ui, packages/storage, packages/domain, packages/capture, packages/mcp, packages/verification, packaging and diagnostic scripts. Tests/spikes are normally synthetic evidence, not production interfaces; findings in them need a reachable trust boundary or runtime/release consequence, and are not blanket-excluded.

No real MCP host, model/provider, source adapter or verification root is enabled by default. Team/cloud/remote exposure, general code runners and arbitrary tool execution are unimplemented deployment surfaces, not implicitly authorized configurations. See [current security status](docs/quality/security-current-status.md).

## Trust Boundaries and Assets

Protect private source text and derivatives, local DB/backups, bootstrap/session/CSRF secrets, current human/agent grants, scoped project records, approvals, verification receipts and managed budgets. Source/model/tool contents are untrusted data; a textual claim of identity, permission, upload or completion grants no authority.

The local host/OS account and selected application startup configuration are trusted deployment prerequisites. The local bootstrap holder receives the local-owner session; there is no multiuser identity provider. Same-OS full account access can read/edit files and defeat application-only protections. Report remote/cross-origin/unprivileged paths separately; do not assume an attacker already has owner credentials to explain an otherwise unreachable exploit.

## Required Security Properties

- Current workspace/project/source authority is checked before read, proposal, commit and data return. Private-source-derived context cannot acquire a broader audience through summaries, graph relations, MCP or export.
- Agent grants cannot approve human decisions, create new grants or turn reported evidence into verified completion. Provider/model output cannot execute SQL, shell commands, configuration changes or approvals.
- Approvals bind actor, operation digest, relevant data/policy/authority versions. Stale/revoked/mismatched approvals fail closed. Changes and their required audit are atomic; retry/replay cannot repeat mutations, launch models/runners or erase accepted work.
- HTTP session, Host/Origin and CSRF checks preserve the local boundary. Parsing/resource ceilings must be explicit; limit/config failures cannot silently widen access or imply success.
- Completion is current criterion/DoD/related-context evidence, not agent wording, child-count success or mere artifact existence.
- File observation is explicitly configured and bound to approved root/path/hash/criterion revisions. Path traversal, symlink/root replacement, nonregular/oversized/racing files cannot produce a pass. File-read permission is not execution permission.
- Managed parent/child reservations retain unknown consumption and enforce shared caps. No claim of controlling independent external chat usage.
- Private backup requires current whole-workspace/source access and explicit acknowledgment. Restore/replay does not reactivate external connections, manufacture current consent or overwrite active data implicitly.
- No API keys, auth headers/cookies, raw source/prompts, private payloads or sensitive error details in operational logs, issue reports or public artifacts.

## Findings and Severity Context

Report reachable unauthorized data exposure/mutation, cross-project or source leakage, forged/stale approval acceptance, arbitrary execution, file-boundary escape, false verification, lost immutable history/audit, secret disclosure and unbounded resource/cost paths. Provide affected version/path, caller capability, prerequisite, input/flow, observed impact and reproduction on synthetic data.

Localhost is not proof of safety against browser-origin attacks or malicious authorized agents. Availability failures remain reportable with a demonstrated trigger; the current mixed-load503is an unresolved reliability observation, not a validated security vulnerability or confirmed denial-of-service exploit. Calibrate severity to actual reachability, permissions and impact; no universal automatic severity label.

No owner-confirmed finding-class exclusions or accepted-risk suppressions are introduced here. Known limitations must remain visible; 'prototype', 'documented', 'fixture' or 'planned' alone does not suppress a reachable finding. Pure roadmap omissions are implementation gaps unless a currently exposed operation breaks an invariant.

## Current Controls and Limitations

Current local session/scoped transactional checks, private-source MCP withholding, bounded commands/tools, revision-bound review, optional POSIX exact-file checks and temporary backup validation have targeted regression evidence. Tests do not prove complete absence of vulnerabilities.

Full login/token lifecycle/tenant roles, shared source policy, secret-vault integration, model transport/egress protections, isolated code execution, persistent redacted incident operations, encryption/retention/purge and internet-facing hardening remain open. Backups are currently unencrypted private whole-workspace copies. DB/application append-only controls do not make files tamper-proof against an OS administrator. Current per-process rate ceilings are not distributed quotas or a complete HTTP read/connection/time-budget defense. No arbitrary public deployment of the local preview.

See [identity/access](docs/architecture/identity-access.md), [limits](docs/architecture/resource-limits-and-abuse.md), [logging/audit](docs/architecture/logging-audit.md), [storage/memory](docs/architecture/storage-memory-capacity.md) and [mixed-load observation](docs/quality/mixed-load.md).

## Reporting and Release Gates

Report privately to the repository owner through an agreed private channel; redact secrets and source contents and use synthetic reproduction. No dedicated mailbox, response SLA, bug bounty or supported stable release matrix has been established. Do not invent contacts or publicly disclose sensitive reports. Credential rotation, disclosure or destructive actions require their own authorization.

Before first real source/provider/target use, satisfy the relevant consent, grant, secret, data/usage and verifier gates. Before team/cloud/public release, validate authentication/tenant isolation, recovery/privacy lifecycle, resource abuse and supply-chain controls with actual deployment assumptions. No comprehensive independent security scan is claimed by this documentation update.

