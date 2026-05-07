# N+3.36 - Claude MCP Read-Only Bridge: Connection Report

**Date:** 2026-05-01
**Branch:** feat/ghoti-visible-operator-stack
**Starting HEAD:** e25a24c

---

## Push Status

e25a24c is present at origin/feat/ghoti-visible-operator-stack - precondition push already satisfied.

---

## MCP Server Inspected

**File:** 01_projects/mcp_server/server.py
**Transport:** stdio JSON-RPC 2.0
**Entrypoint:** python 01_projects/mcp_server/server.py

---

## Tools Exposed (11 tools, all read-only)

| Tool | Description |
|------|-------------|
| ghoti_status | Minimal health payload (time, system name) |
| read_repo_summary | Shallow file/folder count from repo root only |
| read_current_state | Existence check + 300-char preview of current_state.md |
| read_latest_operator_state | Latest persisted operator state JSON snapshot |
| read_manual_execution_queue | All ready-for-manual-execution queue items |
| read_audit_trace | Full supervised lifecycle trace for one approval_id |
| read_control_center_state | Unified pipeline status: inbox counts, queue counts, health flags |
| read_pipeline_items_overview | Per-item overview across all approval/queue/review stages |
| read_approval_inbox | All approval inbox items with pending count |
| read_approval_item | Single approval item by id |
| read_manual_queue_item | Single manual queue item by id |

Implemented but NOT registered in TOOLS (not exposed via MCP):
relay_status, read_compact_memory, read_next_actions - internal helpers only

---

## Safety Verdict: SAFE - APPROVED FOR LOCAL CONNECTION

- No shell execution tool: PASS
- No arbitrary file write/delete: PASS
- No network/browser automation: PASS
- No secrets or env access: PASS
- No live account/email/payment tools: PASS
- Path traversal protection in read_compact_memory: PASS
- All file reads bounded to repo root or compact_memory subdirectory: PASS
- Transport is local stdio - no network listener: PASS
- AST syntax validation: PASS

---

## Connection Command Used

claude mcp add ghoti-local --scope local -- python C:\Users\ai_sandbox\Documents\AI_Managed_Only\14_context\n3_36_claude_mcp_connection_report.md

Config written to: C:\Users\Navif\.claude.json (local/private - not committed to repo)

---

## Claude MCP List Result

ghoti-local: python C:\Users\ai_sandbox\Documents\AI_Managed_Only_projects\mcp_server\server.py - Connected

## Claude MCP Get Result

ghoti-local:
  Scope: Local config (private to you in this project)
  Status: Connected
  Type: stdio
  Command: python
  Args: C:\Users\ai_sandbox\Documents\AI_Managed_Only_projects\mcp_server\server.py

---

## Smoke Test Results (JSON-RPC direct pipe)

| Request | Result |
|---------|--------|
| initialize | protocolVersion 2024-11-05, serverInfo ghoti-mcp v0.1.0 - PASS |
| tools/list | 11 tools returned - PASS |
| tools/call ghoti_status | status ok, system ghoti-mcp, time 2026-05-01T...Z - PASS |

---

## What Remains Unconnected

Intentionally NOT connected per hard safety rules:

- Shell execution tools: none added
- Filesystem write/delete tools: none added
- Network/browser automation: not wired
- Secrets, env vars, API keys: not exposed
- Live account tools (email, social, Whop, Stripe, Gumroad, YouTube, TikTok, Instagram, LinkedIn, job platforms): none
- OSINT/security tools: none

The MCP connection is strictly read-only and repo-local.

---

## Validation Summary

| Check | Result |
|-------|--------|
| git diff --check | PASS |
| python AST parse server.py | PASS |
| claude mcp list | ghoti-local Connected |
| claude mcp get ghoti-local | Scope: Local, Type: stdio, Status: Connected |
| JSON-RPC smoke (initialize / tools/list / ghoti_status) | All PASS |

---

## Files Changed in This Milestone

- 14_context/n3_36_claude_mcp_connection_report.md - this file (new)
- 14_context/current_state.md - short N+3.36 status line appended
- 14_context/next_actions.md - short N+3.36 status line prepended

MCP config written to C:\Users\Navif\.claude.json (local scope, not repo-tracked).

---

## Dirty Files Intentionally Left Unstaged

- 14_context/ghoti_external_repo_tool_intake.md (unrelated modification)
- 21_repos/third_party/.gitkeep (unrelated modification)
- .claude/skills/ (untracked session-only Claude Code skills)
- 01_projects/mcp_server/test.txt (scratch file, not part of this milestone)
- 05_logs/local_brain_runs/* (untracked local brain run logs)
- 05_logs/money_runs/ (untracked money run artifacts)
- 14_context/ghoti_current_prompt_N1_6.md (untracked session prompt)
- CV_Ivan_*.docx, output/ (untracked personal files, out of scope)

---

## Manual Command for Human

To reconnect in a new Claude Code session if needed:

claude mcp add ghoti-local --scope local -- python "C:\Users\ai_sandbox\Documents\AI_Managed_Only_projects\mcp_server\server.py"

Verify with: claude mcp list && claude mcp get ghoti-local

---

## Next Recommendations

**Claude (next milestone):**
N+3.37 - Use ghoti-local MCP tools in a Claude Code session to query live Ghoti operator state (read_control_center_state, read_approval_inbox) and confirm round-trip read visibility from inside Claude Code.

**Codex (next):**
No Codex action required for MCP. Continue video-to-money or experiment scoring work if requested.

**Future milestone:**
N+3.38 - Add relay_status and read_compact_memory to the TOOLS list in server.py if the operator wants those endpoints exposed, after review of which compact memory files should be readable via MCP.
