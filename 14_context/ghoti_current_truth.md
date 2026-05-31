# Ghoti Current Truth Registry

Milestone: N+6.4A — Ghoti Skills System + Karpathy Guidelines + Current Hermes Truth Registration
Date: 2026-05-31
Status: registered (documentation only; no new runtime wiring, no live actions)

This file records the current, verified truth about how Ghoti's multi-agent
system is set up today. It is intentionally conservative: it documents what
exists and what is NOT yet enabled, so no downstream agent assumes more
capability than is real.

## Agent roles (current)

| Agent | Role today |
|-------|-----------|
| ChatGPT | Main strategy / architecture / prompt brain. Designs plans. |
| Hermes | Local coordinator / switchboard / memory writer. Maintains handoffs. |
| Obsidian | Durable shared memory and handoff board. |
| Claude Code | Implementation specialist. Implements assigned tasks only. |
| Codex | Audit / review / verification specialist. |
| Gemma (gemma3:4b) | Cheap summaries / compression / classification. |
| Llama (llama3.1:8b) | Hermes local coordinator brain. |
| Git | Truth / history / rollback. |
| Human | Final approval for risky actions and merges. |

## Hermes local setup (current)

- Hermes runs in the `ai_sandbox` WSL Ubuntu environment.
- Hermes version seen: v0.14.0.
- Hermes coordinator model: llama3.1:8b.
- Provider: custom local endpoint.
- Endpoint: http://127.0.0.1:11434/v1
- Ollama models available locally: llama3.1:8b and gemma3:4b.
- qwen was removed.

## Obsidian

- Obsidian is installed.
- Vault path: C:\Users\ai_sandbox\Documents\AI_Managed_Only\14_context\agent_handoff_vault

## What is NOT enabled (explicit, do not overclaim)

- Telegram is NOT configured for Ghoti Hermes.
- Browser and computer-use tools may appear in Hermes' skill list, but they are
  NOT approved and NOT enabled for Ghoti use. No click, type, or screen control.
- Claude Code and Codex are NOT automatically wired into Hermes. Handoffs are
  manual (copy/paste through the Obsidian vault and the prompt bus).
- Ghoti operates under human supervision. It is supervised, not autonomous;
  human approval gates remain in force for risky actions and all merges.
- No external skill is runtime-wired or auto-executing. External skills are
  inspected as documentation before any use.
- No production analytics and no external telemetry. Local product analytics is
  a documented backlog direction only (see the backlog note), not built here.

## Related documents

- docs/HERMES_LOCAL_SETUP_CURRENT_TRUTH.md
- docs/GHOTI_SKILLS_AND_AGENT_WORKFLOW.md
- docs/CLAUDE_CODE_SKILLS_POLICY.md
- docs/CODEX_AUDIT_WORKFLOW.md
- 14_context/skills/ghoti_skill_registry.md
- 14_context/skills/karpathy_guidelines_intake.md
- 14_context/skills/claude_code_skill_install_log.md
- 14_context/skills/codex_working_rules.md
- 14_context/agent_handoff_vault/05_Backlog/dashboard_performance_and_local_analytics.md
