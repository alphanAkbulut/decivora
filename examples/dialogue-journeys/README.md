# Multi-turn dialogue journeys

48 synthetic journeys /294 messages. These are authored scenario inputs, not native Codex captures.

- `sources.json`: only case metadata, roles and dialogue text.
- `oracles.json`: separate AI-authored expectation drafts and canonical source hashes. Never send these labels as model context. No human-gold or sealed holdout claim.
- Real first batch: J01 completed draft task/status checks; J02/J03 partial/review required; J04–J48 not_run. [Findings and approval gate](../../docs/quality/dialogue-batch-001.md).

The five local integration tests use controlled messages and scripted outputs; they test production capture/context/review/lineage guards, not semantic accuracy. They do not execute all48journeys as model experiments.

[Protocol, coverage, limits and evaluation plan](../../docs/quality/dialogue-journeys.md).

J13–J48 extend cancellation/reopening, verified and unverified Done, blocker aging with virtual clocks, AND/OR rationale, stale question versions, conflicting agents and permissions. See [blocker timer](../../docs/quality/blocker-aging.md) for the implemented local subset.

[Owner-approved continuation, confirmed client timeout and linked clarification code](../../docs/quality/dialogue-batch-001-continuation.md). New clarification prompt has not been model-retested; baseline results stay unchanged.
