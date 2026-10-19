# Multi-turn dialogue journeys

12 synthetic journeys /78 messages. These are authored scenario inputs, not native Codex captures.

- `sources.json`: only case metadata, roles and dialogue text.
- `oracles.json`: separate AI-authored expectation drafts and canonical source hashes. Never send these labels as model context. No human-gold or sealed holdout claim.
- Real semantic runs: **not_run** for every case.

The five local integration tests use controlled messages and scripted outputs; they test production capture/context/review/lineage guards, not semantic accuracy. They do not execute all12journeys as model experiments.

[Protocol, coverage, limits and evaluation plan](../../docs/quality/dialogue-journeys.md).
