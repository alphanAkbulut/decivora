# Codex exec capture — first implementation

**Güncel gerçek kaynak kanıtı:** [19 Ekim seçilmiş sohbet readback'i](codex-real-capture-001.md)6mesajı TEST'e kaydetti; eski full-turn yanıtı boyut sınırında durdu, mevcut client metadata+item sayfaları kullanır. Aşağıdaki ilk teslim kayıtları tarihsel kapsamlarıyla korunur. Tam capture/MVP kabulü yok.

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

## Remaining release work at the initial exec slice

1. Exercise the adapter against an explicitly authorized real installed CLI stream and record its exact version; no real host transcript was read for this delivery.
2. Add a supported user-message capture surface and distinguish desktop from CLI activation. Agent-only capture cannot establish the full conversation, delayed human answer or all pending questions.
3. Add incremental tail/rotation/backpressure scheduling, source coverage/health controls in the UI and consent revocation UX. Current prefix rewrite detection deliberately stops rather than guessing a new session.
4. Bind only authorized new source/context to model dispatch under a concrete data-sharing grant and durable existing budget. Synthetic API approval is not real transcript-sharing approval.
5. Complete the separate Claude adapter and the existing native end-to-end MVP acceptance gates. T16 remains open; the independent T17 coding preparation does not waive its release dependency.

No new paid API calls, real-user imports, normal/TEST database mutation, global configuration changes or task auto-apply were performed by this delivery's verification.


## 19 October — App Server user-message capture and bounded polling

**New code:** `packages/capture/codex/app_server.py`, `read_client.py`, and `scripts/capture_codex_thread.py`. This is a second capture surface; the existing exec wire parser stays separate. The [official App Server reference](https://developers.openai.com/codex/app-server) documents persisted user/assistant items and read-only turn pagination. Its command/transport has experimental and production-support limitations; this delivery is a controlled integration, not a production compatibility guarantee.

The current stdio client exposes only initialization, `thread/turns/list` and `thread/items/list` for one constructor-bound thread. It never sends thread discovery, `thread/start`, `thread/resume`, `turn/start`, steering, approval or execution requests. No API credential environment variables are inherited. The explicitly selected installed executable still runs with local OS access and can load its own configuration/account files; this method filter is not an OS security sandbox. The initial synthetic delivery did not read an installed user's thread; the later limited real readback is documented separately above.

Current reads use `--turn-limit 1..10` (default10), descending turn metadata with `itemsView=notLoaded`, then ascending one-item pages scoped to selected turn IDs. Each response stays within1MiB; at most32item pages are requested, at most16perturn. A capped item sequence is explicitly partial; summary-only text is not passed off as full text. Public user text is retained with item/turn IDs and observed actor metadata; the user role is not an authenticated human principal or approval. Active-turn assistant text is deferred until the turn becomes terminal. User text can already be captured while its assistant reply is in progress. Images/audio/tool/reasoning bodies are excluded; unknown items and omitted older history are visible. Coverage remains partial even when both text roles are present. Compaction, omitted images and unavailable history cannot be reconstructed by this adapter.

Repeated pages/restarts deduplicate sources. Changed already-captured item text stops instead of silently overwriting history. Source imports and receipt fingerprints share one transaction; current scope is checked before the host request and again before the commit. Revocation during the request prevents persistence. This is bounded newest-page polling, not a complete backfill scheduler: more than ten turns between polls can create an omitted-history gap. Existing32source capacity remains explicit and stops further imports without dropping accepted data.

Prepared dialogue context can include up to six previously captured messages from the same capture/thread, bounded to6,000UTF-8bytes in total. Source IDs, roles, turn/item IDs and truncation flags are included. Arrival order is not claimed to be conversation order; other captures/manual conversations are excluded. Only the current source supplies extractable quotes. Model token admission still applies to the entire prepared request; adding nearby context is not free inference or a token-limit bypass.

Use the following only after selecting and authorizing a real local source. Placeholder values are not the current user's thread:

```sh
python3.12 -B scripts/capture_codex_thread.py \
  --db /selected/private/workspace.sqlite --workspace WORKSPACE \
  --principal OWNER --project PROJECT --capture-id CAPTURE \
  --thread-id THREAD --provider-version VERIFIED_VERSION \
  --codex-executable /selected/installed/codex --consent \
  --polls 30 --interval 2
```

Default is one read. Repeated polling is explicit and bounded to300polls,0.25–60seconds between successful reads; any timeout/error stops without automatic retry. `--codex-home` can select an explicit host profile; no profile discovery is performed. Do not provide a broad account scope when only one thread is required. Disconnect uses the existing capture disconnect API/command, retaining captured sources; the reader rechecks consent between polls. Closing this command stops its child App Server, not another desktop process. Real captured text is not automatically sent to a model: data-sharing consent and the existing source/context/budget grants are separate.

### Installed interface probe and verification

Installed CLI reports **0.162.0-alpha.17.2**. Its offline schema generator succeeded and confirmed the implemented initialization and turn-list parameter fields plus user/assistant item shapes; no thread was read or model invoked. It printed a sandbox permission warning while attempting PATH alias setup; no PATH change was granted. Generated schemas stayed outside the repo. Fingerprints:

| Generated schema | SHA-256 |
|---|---|
| ThreadTurnsListParams | `2a8b93d7d4437cc25e16a1dde16d8db3c338d39e16c5eece2a56e943a21577d7` |
| ThreadTurnsListResponse | `8a49c6f47284a46bf9f717a1899f153353efd083f454481afd17aa48a53479fc` |
| InitializeParams | `b55124e7c0f36a1789396daa5578217a92be67f053903696236686e59f6f212e` |

Twelve additional runtime cases cover both roles→existing Task review/accept, nearby context isolation, active turns, privacy counts, prefix independence/restart/item changes, unsupported/summary/oversized pages, scope/surface and revocation timing, atomic rollback, actual stdio framing against a controlled synthetic child, no inherited API key, timeout/child cleanup/no retry, and bounded CLI polling. These controlled fixtures are not real desktop thread readback or semantic quality evidence. The initial timeout test applied a tiny limit to Python process startup and was made deterministic by applying the short deadline only after initialization; production request limits were not relaxed.

Initial synthetic delivery before real readback:501runtime tests passed;48tracker/tool tests and12synthetic browser scenarios passed;50diagrams rendered offline. GitHub publication and live host source verification remain separately evidenced. T17 remains In Progress; real selected-thread readback, source consent UI, older-history backfill, desktop availability and end-to-end model automation acceptance are open. No paid calls or actual user conversation imports were made.

## Current partial host readback and pagination correction

[Real capture001](codex-real-capture-001.md) preserves failure and success separately. A one-time local source consent was used, then disconnected. Current implementation reports unread item gaps and keeps the original byte limit; it does not yet persist item cursors. A new polling pass can repeat the same head pages, so it must not be treated as completed backfill. No further real source read or model sharing is implied by the consumed one-time consent.
