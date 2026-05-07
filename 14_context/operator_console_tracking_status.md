# Ghoti Operator Console — Tracking Status
Generated: 2026-04-18

## Verified Current Truth
- The supervised operator console path is real in code: deterministic operator tick, persisted latest operator state, approval inbox, manual execution queue, audit trace, control-center read model, MCP read tools, dashboard panels, and CLI surfaces all exist.
- The hardened supervised CLI contract is present for the key console commands: they emit a human-readable header, a literal `---` separator, and a JSON object.
- The dashboard backend parser is now CRLF-safe and treats null or invalid parsed summaries as failures rather than silent success.
- A real approval -> manual queue -> review chain exists in compact memory for approval `approval-0305205ab4984814a8a6af58ff4c403a` and queue item `ready-12c3a6792f6c47c4b14c202159ef115e`.
- The dashboard still reads supervised operator state through CLI subprocesses rather than a direct read-model API path.

## Core Product Files Still Not Tracked In Git
| File | Status | Why it matters |
|------|--------|----------------|
| `01_projects/runtime_mvp/src/super_ai_agent/operator_loop.py` | untracked | Operator lifecycle, approval bridge, queue and audit logic |
| `01_projects/runtime_mvp/src/super_ai_agent/control_center_state.py` | untracked | Pipeline overview and control-center aggregation |
| `01_projects/runtime_mvp/src/super_ai_agent/mcp_runtime.py` | untracked | MCP caller with explicit allowlist and argument support |
| `01_projects/mcp_server/server.py` | untracked | Local stdio MCP server and read-only tool surface |
| `03_scripts/run_mcp_server.ps1` | untracked | Repo-local MCP launch helper |
| `.claude/settings.json` | untracked | Repo-local Claude safety/launch config |
| `CLAUDE.md` | untracked | Repo-local Claude workflow instructions |

## Files That Should Stay Local / Runtime-Only
| Path | Why it should not be committed |
|------|-------------------------------|
| `14_context/compact_memory/approval_inbox.json` | Runtime state snapshot |
| `14_context/compact_memory/latest_operator_state.json` | Runtime state snapshot |
| `14_context/compact_memory/manual_execution_queue.json` | Runtime state snapshot |
| `01_projects/runtime_mvp/runtime_data/*.tmp-*` | Stale temp artifacts / crash leftovers |
| `.claude/settings.local.json` | Machine-local Claude settings |
| `14_context/ghoti_current_prompt.md` | Prompt scratch / handoff artifact |
| `Roaming/` | Local machine spillover, unrelated to product source |
| `gemma4/` | Local artifact, not product source |
| `01_projects/mcp_server/test.txt` | Scratch file, not part of the MCP product surface |

## Current Risks That Are Still Real
- The MCP server duplicates parts of the read-model logic instead of importing a single runtime source of truth.
- The dashboard supervised path still depends on CLI subprocess execution, which is serviceable but not the cleanest long-term read path.
- `approval_gate_intact` in the control-center state is still a hardcoded truthy flag rather than a computed health signal.
- There are still overlapping older and newer "Ghoti control center" concepts in the dashboard/runtime surface.
- One older approved item still has no queue item; the current code surfaces that honestly as legacy state rather than hiding it.

## Note On Earlier Blocked-Write Claims
The earlier cross-user write-failure explanation should not be treated as current truth by default. It was not re-proven in the current session, and recent persisted operator state shows successful writes did happen during the reliability work.
