# Ghoti Agent Routing (Compact)

**Updated:** 2026-05-05 — Milestone N+3.34
**Branch:** `feat/ghoti-visible-operator-stack`
**Source:** `14_context/agent_registry/agent_routing_policy_n3_14.md`, `14_context/codex_n3_34_compact_memory_contract.md`

---

## Purpose

Compact routing truth for Gemma, Claude Code, Codex, ChatGPT, and future control planes.
Not a cap bypass. Not an autonomous routing claim. Routing guidance for operator use only.

## Source of Truth

- `14_context/agent_registry/agent_routing_policy_n3_14.md`
- `14_context/n3_14_api_saving_agent_routing_summary.md`
- `14_context/api_saving_memory_workflow_n3_17.md`
- `23_configs/local_brain_router_policy.example.json`

## Update Rules

- Update after model/router milestones.
- Update after worker-card policy changes.
- Human review before autonomous routing is enabled.

---

## Current Routing Policy

| Agent | Task Class | Status |
|-------|-----------|--------|
| **ChatGPT** | strategy, prompt design, architecture, next-milestone planning | active |
| **Claude Code** | hard implementation, commits, validation, runtime fixes | active |
| **Codex** | audit, source verification, spec writing | active |
| **Gemma/Ollama (local)** | cheap local drafts, compression, scoring, context summarization | active — gemma3:4b smoke-passed (N+3.13) |
| **Paperclip** | control plane candidate | planning_only — not installed, not wired |
| **OpenClaw** | worker/operator candidate | planning_only — reference read-only |
| **n8n** | workflow automation candidate | planning_only — not installed |
| **CUA / Browser Use** | browser execution | gated — explicit approval required |

## Not Cap Bypass

- Model routing is operator convenience, not Claude provider limit bypass.
- Each model runs in its own session; there is no shared credential path.

## Worker Card Registry

- `14_context/agent_registry/active_worker_cards_n3_14.md`
- 6 cards: LOCAL-GEMMA-EASY-001, CODEX-AUDIT-001, CLAUDECODE-IMPLEMENT-001, PAPERCLIP-CONTROL-PLANE-CANDIDATE, OPENCLAW-WORKER-CANDIDATE, N8N-WORKFLOW-CANDIDATE

## Local Brain Router

- File: `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- Policy: `23_configs/local_brain_router_policy.example.json`
- Task classes routed: `compress_context`, `video_to_money`, `draft_checklist`
- Current mode: `preview_only` (enabled: false in policy)

---

## Review Status

**status:** draft
**review_required:** yes — before implementing autonomous routing; human approval required
**unknown:** Paperclip exact source/repo, OpenClaw exact source, n8n workflow integration path

## Related Files

- `14_context/agent_registry/agent_routing_policy_n3_14.md`
- `14_context/obsidian_vault/03_Decisions.md`
- `14_context/compact_memory/agent_routing_memory.md`
