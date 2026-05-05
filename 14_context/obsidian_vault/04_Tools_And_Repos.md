# Ghoti Tools And Repos (Compact — N+3.34 canonical)

**Updated:** 2026-05-05 — Milestone N+3.34
**Branch:** `feat/ghoti-visible-operator-stack`
**Source:** `14_context/obsidian_vault/04_Tools.md` (N+3.7 predecessor), `14_context/tooling_intake_priority_n3_17.md`

---

## Purpose

Compact truth for tools installed, cloned, evaluated, planning-only, or blocked.
Predecessor note: `04_Tools.md` (N+3.7) — not overwritten, still valid.

## Source of Truth

- `14_context/tool_intake_new_candidates_n3_2.md`
- `14_context/tooling_intake_priority_n3_17.md`
- `14_context/obsidian_vault/04_Tools.md`
- Milestone docs for each tool in `14_context/`

## Update Rules

- Only update after tool status genuinely changes.
- Do not mark tool as `installed` or `wired` without confirmed smoke test + operator approval.
- Keep `04_Tools.md` (N+3.7) intact; this file is the N+3.34+ canonical form.
- Mark unknown paths as `unknown`.

---

## Computer-Use Candidates

| Tool | Status | Path |
|------|--------|------|
| TryCUA / CUA Driver | `cloned_read_only` / `not_wired` / docker_smoke_pending_approval | `21_repos/third_party/evals/cua` |
| AutoBrowser | `planning_only` / `not_wired` | unknown |
| Obscura (CDP) | `binary_built` / `smoke_verified` / `not_wired` | unknown |
| Browser Use | `not_installed` | — |

## Local AI / Knowledge

| Tool | Status |
|------|--------|
| Gemma3:4b (Ollama) | `installed` / `smoke_pass` (N+3.13) |
| AnythingLLM | `not_installed` |
| Open WebUI | `not_installed` |
| LibreChat | `not_installed` |

## Money Workflow Scripts (stdlib-only)

| Script | Status | Path |
|--------|--------|------|
| `weekly_money_review.py` | `smoke_pass` (N+3.29) | `03_scripts/weekly_money_review.py` |
| `manual_decision_queue_new_item.py` | `smoke_pass` (N+3.31) | `03_scripts/manual_decision_queue_new_item.py` |
| `money_workflow_new_experiment.py` | `smoke_pass` (N+3.17) | `03_scripts/money_workflow_new_experiment.py` |
| `obsidian_memory_scaffold.py` | `implemented` (N+3.34) | `03_scripts/obsidian_memory_scaffold.py` |

## MCP / Runtime

| Tool | Status | Path |
|------|--------|------|
| ghoti-local MCP server | `connected_read_only` (N+3.36) | `01_projects/mcp_server/` |
| MCP launcher | `implemented` | `03_scripts/run_mcp_server.ps1` |
| Dashboard launcher | `implemented` | `03_scripts/run_dashboard.ps1` |

## Third-Party Clones (read-only, 21_repos/third_party/)

| Repo | Status |
|------|--------|
| trycua/cua | `read_only_clone` |
| OpenClaw | `read_only_reference` |
| Paperclip / n8n | `planning_only` — not cloned |

## Blocked Gates

- CUA container: Docker ready (N+3.11); explicit approval phrase required before `docker run`
- Browser Use: not installed; install only when browser-role task ready
- Paperclip/OpenClaw/n8n: planning_only — not installed, not wired
- Screenpipe: not started; status route exists only (`GET /api/ghoti/screenpipe/status`)

---

## Review Status

**status:** draft
**review_required:** yes — verify tool status against milestone docs before canonical use
**unknown:** AutoBrowser exact repo path, OpenFang exact repo

## Related Files

- `14_context/obsidian_vault/04_Tools.md` — N+3.7 predecessor (intact)
- `14_context/tool_intake_new_candidates_n3_2.md`
- `14_context/tooling_intake_priority_n3_17.md`
