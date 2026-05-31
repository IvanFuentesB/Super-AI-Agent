# Codex Audit Prompt

Use this when Codex quota resets.

Audit the active feature branch against main.

Read:
- 14_context/agent_handoff_vault/AGENT_RULES.md
- 14_context/agent_handoff_vault/02_Agent_Handoffs/CURRENT_TASK.md
- 14_context/agent_handoff_vault/04_Logs/CLAUDE_LAST_RUN.md

Verify:
- Task was followed
- No secrets
- No unsafe actions
- No unrelated file edits
- Tests/checks pass
- Claims match repo truth

Write result to:
14_context/agent_handoff_vault/04_Logs/CODEX_LAST_AUDIT.md
