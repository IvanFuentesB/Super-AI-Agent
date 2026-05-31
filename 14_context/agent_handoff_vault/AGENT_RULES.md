# Agent Rules

## Roles
- Hermes/Alfred: coordinator, planner, memory writer, handoff manager.
- Claude Code: implementation only.
- Codex: audit/review/verification.
- Gemini/local model: cheap planning, summarization, compression.
- Human: final approval for risky actions and merges.

## Hard Rules
- One task per agent.
- Never let multiple agents edit the same files at once.
- Use branches/worktrees.
- No secrets in prompts, repos, or notes.
- No destructive actions without human approval.
- No live account/API/posting/money/legal actions without approval.
- Coordinator plans; implementer implements; auditor audits.

## Workflow
1. Coordinator writes CURRENT_TASK.md.
2. Claude Code reads task and implements minimal changes on feature branch.
3. Claude writes CLAUDE_LAST_RUN.md.
4. Codex audits against main and writes CODEX_LAST_AUDIT.md.
5. Coordinator summarizes and recommends merge/fix.
6. Human approves merge.
