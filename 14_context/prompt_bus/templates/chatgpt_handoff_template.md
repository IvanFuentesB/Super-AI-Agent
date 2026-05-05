# ChatGPT Handoff Template

**Usage:** Copy this template when handing off context to ChatGPT for strategy/planning.
**Role:** ChatGPT = strategy, architecture, next-milestone planning, prompt design.

---

## Template

```markdown
You are acting as the strategy/planning layer for the Ghoti AI operator system.

## Context

Repo: IvanFuentesB/Super-AI-Agent
Branch: feat/ghoti-visible-operator-stack
Latest commit: {{COMMIT_HASH}} — {{COMMIT_MESSAGE}}
Milestone just completed: {{COMPLETED_MILESTONE}}
Current date: {{DATE}}

## Current System State

{{PASTE_FROM: 14_context/obsidian_vault/09_Migration_Handoff.md}}
{{PASTE_FROM: 14_context/compact_memory/project_state.md}}

## Active Lane Status

Claude lane: {{CLAUDE_LANE_STATUS}}
Codex lane: {{CODEX_LANE_STATUS}}

## What I Need From You

{{STRATEGY_REQUEST}}

Options:
- Next milestone design
- Prompt package for Claude/Codex/Gemma
- Architecture review
- Risk assessment for a tool integration
- Orchestration plan

## Hard Constraints

- No live account actions without explicit approval
- No credential fabrication
- No impersonation
- No bypassing usage limits
- Python workers = stdlib only, repo-local
- Gemma output = draft only, never canonical without human review
- Ruflo/OpenClaw/Paperclip/n8n = planning only, not yet wired

## Output Format

{{DESIRED_OUTPUT_FORMAT}}
```
