# Shared File Lock Policy

Files listed here require an active lock record in active_locks.jsonl before
any agent may write to them during parallel execution. Read-only access is always
permitted without a lock.

## Core State Files — Always Require Lock

- 14_context/current_state.md
- 14_context/next_actions.md
- 14_context/ghoti_finish_line_log.md

## Compact Memory Files — Require Lock

- 14_context/compact_memory/agent_routing_memory.md
- 14_context/compact_memory/project_state.md
- 14_context/compact_memory/safety_rules.md
- 14_context/compact_memory/repo_and_tool_index.md
- 14_context/compact_memory/money_os_memory.md
- 14_context/compact_memory/dirty_state_warning.md

## Obsidian Vault Index and Active Notes — Require Lock

- 14_context/obsidian_vault/00_Index.md
- 14_context/obsidian_vault/01_Current_State.md
- 14_context/obsidian_vault/02_Next_Actions.md
- 14_context/obsidian_vault/08_Dirty_State.md
- 14_context/obsidian_vault/09_Migration_Handoff.md

## Dashboard Runtime Files — Require Lock If UI Lane Owns Them

- 01_projects/runtime_mvp/src/super_ai_agent/server.js
- 01_projects/runtime_mvp/src/super_ai_agent/app.js

## Implementation Scripts — Require Lock If Implementation Lane Owns Them

- 03_scripts/agent_lane_status.py
- 03_scripts/weekly_money_review.py
- 03_scripts/manual_decision_queue_new_item.py

## Agent Lane Meta Files — Owned by Implementation Lane Only

- 14_context/agent_lanes/agent_lane_registry.json
- 14_context/agent_lanes/active_locks.jsonl
- 14_context/agent_lanes/lane_status.jsonl

## Policy

- During sequential execution: no lock needed; single-writer implicit.
- During declared parallel execution: lock required before writing any file in this list.
- Lock granularity: per-file or per-directory group, declared in locked_files of the lock record.
- Lock release: append a released status record after merge or abandonment.
- Dispute resolution: human operator resolves conflicts; neither agent may force-write.
