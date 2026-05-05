---
memory_type: compact_pointer
status: draft
last_updated: 2026-05-05
latest_known_commit: df57706
dirty_state_known: true
source_files:
  - 14_context/agent_registry/agent_routing_policy_n3_14.md
  - 14_context/n3_14_api_saving_agent_routing_summary.md
  - 14_context/api_saving_memory_workflow_n3_17.md
  - 23_configs/local_brain_router_policy.example.json
generated_by: claude
reviewed_by: none
review_required_before_canonical_use: true
---

# Compact: Agent Routing Memory

> **WARNING:** Compressed pointer layer. Routing claims are guidance only — not autonomous.
> Future candidates remain planning_only unless operator approves and implementation is verified.
> **Max target size:** 300–600 words

---

## Current Routing (active)

| Agent | Task Class | Status |
|-------|-----------|--------|
| **ChatGPT** | strategy, prompt design, architecture, next-milestone planning | active |
| **Claude Code** | hard implementation, commits, validation, runtime fixes | active |
| **Codex** | audit, source verification, spec writing | active |
| **Gemma/Ollama (local)** | cheap local drafts, compression, scoring | active — gemma3:4b smoke-passed (N+3.13) |

## Future Candidates (planning_only — not wired)

| Agent | Status |
|-------|--------|
| Paperclip | planning_only — not installed |
| OpenClaw | reference_read_only — not wired |
| n8n | planning_only — not installed |
| CUA / Browser Use | gated — explicit approval required |

## Not Cap Bypass

Routing decisions are operator convenience, not Claude provider limit bypass.
Each model runs in its own session. No shared credential path.

## Local Brain Router

- File: `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- Policy: `23_configs/local_brain_router_policy.example.json`
- Task classes: `compress_context`, `video_to_money`, `draft_checklist`
- Mode: `preview_only` (enabled: false in policy)

## Worker Card Registry

- `14_context/agent_registry/active_worker_cards_n3_14.md`
- 6 cards: LOCAL-GEMMA-EASY-001, CODEX-AUDIT-001, CLAUDECODE-IMPLEMENT-001, PAPERCLIP-CONTROL-PLANE-CANDIDATE, OPENCLAW-WORKER-CANDIDATE, N8N-WORKFLOW-CANDIDATE

---

## Source Pointers

- Routing policy: `14_context/agent_registry/agent_routing_policy_n3_14.md`
- API-saving plan: `14_context/api_saving_memory_workflow_n3_17.md`
- Vault note: `14_context/obsidian_vault/07_Agent_Routing.md`

## Next Update Instructions

Update after model/router milestones or worker-card policy changes.
Human review before autonomous routing is enabled.

## N+3.43 Pointer Update

- Agent lane scaffold: `14_context/agent_lanes/`
- Lane helper: `03_scripts/agent_lane_status.py`
- Milestone doc: `14_context/agent_lane_locks_n3_43.md`
- Controlled parallel rule: branch per agent, lock shared files before writing, emit status beacons, merge one branch at a time.
- Gate: controlled parallel execution can begin only after the N+3.43 implementation commit is pushed and Codex audit confirms lane locks pass.
