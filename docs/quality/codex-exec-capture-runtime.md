# Codex exec capture — first implementation

**19 October 2026. T17 In Progress; not native desktop or MVP acceptance.** This delivery connects a selected Codex CLI JSONL stream to the existing conversation/source and dialogue-review code. It does not start Codex, read other chats, or dispatch a model. The ordinary application still has no default extractor.

## Implemented boundary

| Step | Current code | Evidence / limit |
|---|---|---|
| Source selection | Explicit local caller supplies project, capture ID, thread ID, reported CLI version and consent | No home-directory discovery, hooks installation or global configuration edits |
| Collection | Completed `agent_message` items from `codex exec --json` | Public assistant text only; user prompt is not present in the documented example; user conversation coverage remains partial |
| Missing data | Pending trailing JSONL line, waiting turn end, terminal failure and unknown item count are explicit | Complete assistant items can be saved before turn-end arrives; an absent event cannot be invented or guaranteed recoverable |
| Durability | One transaction imports sources and commits prefix cursor/hash | Restart/repeated prefix returns the same receipt; rewritten/truncated committed prefixes stop; accepted data is preserved |
| Provenance | `codex_exec_jsonl`, capture/thread/turn/item/version, observed actor and partial coverage | Observer remains the local human principal; upstream identities/version are claimed metadata, not authenticated host credentials |
| Privacy | Existing source redaction before DB persistence and source text hash | Tool arguments/output, reasoning and provider error text are excluded. Raw stream is not copied into the database or logs; prefix continuity retains a SHA-256 fingerprint only |
| Review | Existing prepare → structured response validation → candidate review → human accept | Capture cannot approve or mark tasks Done; model sharing and spend require their existing distinct grants |
| Operations | Durable capture-specific audit receipts and a command summary | Full Operations dashboard integration, live liveness detection and automated incident creation remain open |

## Supported interface and exclusions

The [official non-interactive documentation](https://developers.openai.com/codex/noninteractive) describes `codex exec --json`, thread/turn/item events and completed assistant messages. It describes a **controlled CLI run**, not passive access to already-open desktop chats. Checked 19 October 2026. No claim is made that the installed desktop application exposes this same wire surface.

The adapter ignores partial item updates and reasoning, commands, file changes, MCP/collaboration calls, searches and plan bodies. Unknown top-level event types fail closed; unknown item types count as unsupported coverage. A CLI error produces a failed capture state without retaining its arbitrary error message. `turn.completed` means the host turn ended, never that an extracted product task is verified Done. Usage fields in this adapter are not trusted as a billed cost ledger.

The first implementation is bounded to a selected stream snapshot of 1 MiB, individual wire lines of 64 KiB and message bodies of 12,000 UTF-8 bytes. Existing preview capacity is 32 source imports and 32 capture bindings per project. Crossing a limit stops the new transaction; it does not truncate or delete accepted work. These are explicit implementation limits, not universal product capacity promises. Snapshot replay is bounded prefix replay, not a scalable continuous tailer.

## Run against an explicitly selected local file

Use Python 3.12 from the repository root. The database and project must already exist; the local principal must have current human write permission. Values below are placeholders, not this user's real source or workspace identity:

```sh
python3.12 -B scripts/capture_codex_exec.py \
  --db /selected/private/workspace.sqlite --workspace WORKSPACE \
  --principal OWNER --project PROJECT --capture-id CAPTURE \
  --thread-id THREAD --provider-version SELECTED_CLI_VERSION \
  --snapshot /selected/private/exec.jsonl --consent
```

The selected file is read once, without following a final symlink, with a fixed size ceiling. This command does not launch `codex exec`; launching an agent is a separate execution and usage decision. Repeating the command with the same growing prefix captures newly completed messages without repeating prior sources. `--disconnect` with the same database/workspace/principal/project/capture arguments disables collection and preserves accepted sources. Reconnecting after revocation requires a new explicit capture identity; stale authority revision cannot silently continue.

Do not publish real raw streams: a host may write credentials into tool or reasoning events even though Decivora excludes those fields. Existing source audience controls still apply. This CLI uses the local operating-system trust boundary; its principal argument is not a remote login or multi-tenant authentication mechanism.

## Verification and findings

`tests/runtime/test_codex_capture.py` covers 14 synthetic integration and failure cases: binding/consent/current authority, restart/retry, pending line, no turn-end, redaction, ignored private fields, failure, prefix rewrite/truncation, conflicting item, unknown events/items, capacity rollback, receipt failure rollback, same-text distinct turn identity, selected-file CLI/symlink, and capture→existing review→explicit Task accept. The injected model response is controlled test data, not a new semantic model result.

An initial implementation exposed nested SQLite transactions when importing a source inside the cursor transaction. It was corrected by an internal explicit transaction-reuse path; the rollback test confirms no orphan source or falsely advanced cursor on failure. Original manual source IDs and their deduplication behavior remain unchanged.

The prepared model request carries assistant-only provenance and a human-authority warning; complete-conversation coverage claims are rejected by code.

Full runtime regression: **489 tests passed** with local loopback allowed. Existing **50 Mermaid diagrams rendered** offline; the changed local-preview source and SVG provenance were refreshed. The existing 48 tracker/tool tests also passed after updating the expected T17 In Progress count. These checks do not invoke a model or prove native host capture.

## Remaining release work

1. Exercise the adapter against an explicitly authorized real installed CLI stream and record its exact version; no real host transcript was read for this delivery.
2. Add a supported user-message capture surface and distinguish desktop from CLI activation. Agent-only capture cannot establish the full conversation, delayed human answer or all pending questions.
3. Add incremental tail/rotation/backpressure scheduling, source coverage/health controls in the UI and consent revocation UX. Current prefix rewrite detection deliberately stops rather than guessing a new session.
4. Bind only authorized new source/context to model dispatch under a concrete data-sharing grant and durable existing budget. Synthetic API approval is not real transcript-sharing approval.
5. Complete the separate Claude adapter and the existing native end-to-end MVP acceptance gates. T16 remains open; the independent T17 coding preparation does not waive its release dependency.

No new paid API calls, real-user imports, normal/TEST database mutation, global configuration changes or task auto-apply were performed by this delivery's verification.
