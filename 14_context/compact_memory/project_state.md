---
memory_type: compact_pointer
status: draft
last_updated: 2026-05-05
latest_known_commit: df57706
dirty_state_known: true
source_files:
  - 14_context/current_state.md
  - 14_context/next_actions.md
  - 14_context/ghoti_finish_line_log.md
generated_by: claude
reviewed_by: none
review_required_before_canonical_use: true
---

# Compact: Project State

> **WARNING:** Compressed pointer layer. If latest commit differs from `df57706`, re-read `14_context/current_state.md`.
> **Max target size:** 400–700 words

---

## Latest Known Pushed HEAD

`df57706` — `docs(ghoti): audit N+3.32 and lock Obsidian readiness`
N+3.34 commit pending.

## Branch

`feat/ghoti-visible-operator-stack` — in sync with origin at N+3.34 start.

## Working Capabilities (through N+3.34)

- Python operator runtime with approval-aware lifecycle (`01_projects/runtime_mvp/`)
- Node.js dashboard with live state, tasks, approvals, artifacts (`01_projects/`)
- MCP server (read-only, 11 tools, ghoti-local, N+3.36)
- Local brain router (Gemma3:4b, preview_only policy, N+3.14)
- Multi-agent MVP (5 local agents, repo-bound, N+3.something)
- Money workflow scripts: weekly review (N+3.29), manual queue (N+3.31), experiment scoring (N+3.17)
- Obsidian vault: 10-file scaffold (N+3.7 original + N+3.34 full)
- Compact memory: older files + N+3.34 new 6-file set
- Helper script: `03_scripts/obsidian_memory_scaffold.py` (N+3.34)

## Major Blocked / Not-Yet-Wired

- No live external adapters (AutoBrowser, RUFLO, Obscura, CUA) wired
- No live mail/LinkedIn/Notion writes
- No Screenpipe capture started
- No Browser Use installed
- CUA smoke: Docker ready (N+3.11), requires explicit operator approval phrase

## Current Dirty-State Headline

Untracked local dirt (logs, CVs, skills, prompt scratch) intentionally unstaged.
Dirty tracked: `ghoti_external_repo_tool_intake.md` + `21_repos/third_party/.gitkeep` — do not stage.
See `14_context/compact_memory/dirty_state_warning.md` for file list.

## Next Milestone

N+3.43 — Agent Lane Locks And Parallel Execution Scaffolding.
Source: `14_context/codex_n3_42_next_sequence_lock.md`

---

## Source Pointers

- Full state: `14_context/current_state.md`
- Full next actions: `14_context/next_actions.md`
- Codex sequence: `14_context/codex_n3_42_next_sequence_lock.md`
- Finish line: `14_context/ghoti_finish_line_log.md`

## Next Update Instructions

Update after next pushed milestone commit.
Replace HEAD hash, update capabilities, update blocked section.
Mark `status: stale` if commit or dirty-state differs.
