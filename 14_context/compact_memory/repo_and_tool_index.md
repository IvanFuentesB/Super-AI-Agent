---
memory_type: compact_pointer
status: draft
last_updated: 2026-05-05
latest_known_commit: df57706
dirty_state_known: true
source_files:
  - 14_context/obsidian_vault/04_Tools_And_Repos.md
  - 14_context/tooling_intake_priority_n3_17.md
  - 14_context/tool_intake_new_candidates_n3_2.md
generated_by: claude
reviewed_by: none
review_required_before_canonical_use: true
---

# Compact: Repo and Tool Index

> **WARNING:** Compressed pointer layer. Tool status may be stale.
> Verify against milestone docs before acting on install/run decisions.
> **Max target size:** 300–600 words

---

## Key Directories

| Path | Purpose |
|------|---------|
| `01_projects/runtime_mvp/` | Core Python runtime |
| `01_projects/` | Node.js dashboard |
| `03_scripts/` | Helper scripts (stdlib only) |
| `14_context/` | Context, specs, compact memory, vault |
| `14_context/money_workflows/` | Money workflow data files |
| `21_repos/third_party/` | Read-only reference clones |
| `23_configs/` | Local config examples |
| `05_logs/` | Generated run artifacts |

## Tool Status

| Tool | Status | Notes |
|------|--------|-------|
| Gemma3:4b (Ollama) | `installed` `smoke_pass` | N+3.13 |
| Docker Desktop | `installed` `daemon_ready` | N+3.11 |
| TryCUA / CUA Driver | `cloned_read_only` `not_wired` | Approval phrase required for smoke |
| AutoBrowser | `planning_only` `not_wired` | unknown path |
| Obscura (CDP) | `binary_built` `smoke_verified` `not_wired` | unknown path |
| Browser Use | `not_installed` | — |
| Paperclip | `planning_only` | — |
| OpenClaw | `reference_read_only` | `21_repos/third_party/` |
| n8n | `planning_only` | — |
| Screenpipe | `plan_exists` `not_installed` | Status route only |

## Do Not Install/Run (blocked gates)

- CUA container: explicit approval phrase before `docker run`
- Browser Use: install only when browser-role task is ready
- Paperclip / OpenClaw / n8n: planning_only, not installed
- Any tool outside allowlist: operator approval required

## Money Workflow Scripts

| Script | Status |
|--------|--------|
| `03_scripts/money_workflow_new_experiment.py` | `smoke_pass` N+3.17 |
| `03_scripts/weekly_money_review.py` | `smoke_pass` N+3.29 |
| `03_scripts/manual_decision_queue_new_item.py` | `smoke_pass` N+3.31 |
| `03_scripts/obsidian_memory_scaffold.py` | `implemented` N+3.34 |

---

## Source Pointers

- Tool detail: `14_context/obsidian_vault/04_Tools_And_Repos.md`
- Tool priority: `14_context/tooling_intake_priority_n3_17.md`
- Wait/resume gates: `01_projects/runtime_mvp/runtime_data/wait_resume_items.json`

## Next Update Instructions

Update after any tool install, clone, run, or status change.
Codex review before tool truth is used in implementation prompts.
