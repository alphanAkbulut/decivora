# ADR-0013 — Task workflow, proof and familiar UI

**Accepted direction — 14 October 2026.** Human user approved the four-tool benchmark proposal and familiar UI layout, including documentation/schema/diagram/GitHub consistency. Paid APIs, new accounts and public release are excluded.

## Context / alternatives

The four-lane preview mixed a historical work-start claim with current execution; manual impediments were visible but dependency/approval/evidence stages were separate and incompletely integrated. [Benchmark and sources](../../discovery/workflow-status-benchmark.md) compare Jira, Linear, ClickUp and Asana. Preserve all product scope and14MVP AC.

Options: keep four hardcoded lanes (too little execution detail); put every waiting/approval/verification result in one enum (loses concurrent states and creates too many columns); copy all vendor statuses (includes unrelated hiring/sales processes); choose a small preset plus orthogonal assessments. **Selected last option:** Backlog/To Do/In Progress/In Review/Awaiting Verification/Done; Cancelled remains a separate terminal view; reason/evidence/readiness/blocks are distinct.

## Decision / implementation

Python/SQLite and plain HTML/CSS/JS remain. No frontend library/framework installed. `TaskWorkflowService` uses revision-bound append-only audit. Existing event schema/SQL format1 and lifecycle guards remain; no blanket data migration. All UI state reads share one authorized SQLite snapshot. Human transitions and criterion evidence have typed fields, stable request keys and exact task/AC version; agents/source strings cannot spoof human authority. Review stage means implementation handoff, not scope-change permission. Completion requires all applicable required current criteria, no recorded finish impediment, and explicit scope/impact review. Local human review is enabled; automatic/file runners are not.

Dependency relation gate in this UI is **finish**: preparations can start, completion needs current verified prerequisite. Manual impediments choose start/finish/both. This does not rewrite old graph edges; recorded-relation coverage is explicit. Full source-aware gate metadata for adapter-derived relations and unknown/context readiness remains future integration. Blocked by/Blocks direction and manual pending question task binding are visible. Rejected proposal is not Task cancellation; obsolete cancellation still requires existing impact/human review.

UI: stable sidebar, real views, compact board/list, filters/search, end-side task panel with Overview/AC-DoD/Sources/History. Import conversation remains prominent; manual entry secondary. English stage names stay; five locale catalogs and AR RTL remain. Source text is untrusted text, never HTML/command. Desktop board scroll is within board; narrow screens use full detail panel with focus/Escape handling. Screenshot blueprint is not product proof.

## Consequences / open limits

No paid model request. Legacy starts can be read without rewriting history. Current Done can become stale after evidence, contract, task or recorded prerequisite changes; original success remains historical. Status presentation is not proof of target deployment/upload. Current local human-review evidence carries a reference and observation note; it does not hash or independently fetch external artifacts. Automatic verifier, native capture/semantic extraction, multi-user review, full workflow configurator, parent completion and external sync remain open.

## Validation

[Runtime/browser proof](../../quality/workflow-ui-runtime.md) and exported [payload schemas](../../../manifests/task-stage.schema.json) distinguish human review, automatic verification and model quality. Test stale/partial/failure/authority/retry, dependency direction, start vs finish, legacy cancel-reopen, replay/restore and all supported view/locale interactions. Publish exact commit readback separately from runtime/visual validation.
