# Local MCP stdio bridge — current subset

Code: [server](../../packages/mcp/server.py), [durable draft review](../../packages/domain/agent_proposals.py), [tests](../../tests/runtime/test_mcp_local.py), [development/follow-up report](../delivery/api-independent-development.md).

Five tools: get_project_brief, query_records, get_record, submit_changeset, submit_evidence. Last two submit a create-only untrusted draft / untrusted execution claim; neither approves/applies/marks criteria passed. Human Inbox approval/application are separate current-authority actions. Existing private/source-derived records are withheld until a real sharing policy is implemented. Empty output is not proof no duties exist. The stdio bridge reads only an existing selected database and pre-provisioned agent identity; local owner identities and request-supplied identity fields are rejected.

## Launch after a separate host/grant decision

```text
python3.12 -B -m packages.mcp.server --database /ABSOLUTE/SELECTED/workspace.sqlite --workspace WORKSPACE_ID --principal PREPROVISIONED_AGENT_ID
```

Run from the package checkout (or configure its Python module path). This command is an example, not a grant installer and not executed against the user's workspace here. User selects exact client/version and data scope before creating an agent grant or registering this command. No API key required for deterministic tools; host reading tools/results can use its own model quota. A CLI process can only provide the transport; it does not watch all chats, read hidden model reasoning or pause another agent. Native configuration/account authentication and source capture are distinct.

Protocol2025-06-18 initialization + initialized notification, JSON-RPC2 UTF-8 newline stdio, tools/list, tools/call, ping, EOF exit. No HTTP/SSE, resources/prompts/sampling/elicitation, JSON-RPC batches or native SDK certification. Per-process60tool calls/minute is a resource guard, not a global host-token budget. Local framing32KiB, tool content16KiB, brief1024–4096 UTF-8 bytes, visible page1–25, authorized scan bounded500; these are byte/resource ceilings, not exact model-token counts. Cursor HMAC binds principal/workspace/project/current knowledge/current authority/type filter/page size; server restart requires resync. Full delta/tombstone and large-project pagination remain open. No arbitrary SQL, shell or model execution.

Durable proposals max16create operations,12KiB preview,128stored per project; typed claims512per project. Existing admitted history is preserved on limit failure. This is not a global provider budget or OS sandbox. Only selected local identities under the user's OS permissions are considered; remote/team auth belongs later phases. Real client/tool schema/context-token, reconnect and permission-revoke checks are mandatory before first native use.
