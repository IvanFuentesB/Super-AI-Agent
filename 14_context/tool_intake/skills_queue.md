# Skills Queue

Skills grouped by whether they are already in this repo's workflow or awaiting a
manual install. Status of record: `14_context/tool_stack/skills_registry.json`.
Setup steps: `docs/GHOTI_AGENT_SKILLS_SETUP.md`.

## Already in workflow (use directly, no install)

| Skill | Agent(s) |
|-------|----------|
| karpathy-guidelines | claude_code, codex |
| context-engineering | claude_code, codex |
| search-first/source-driven-development | claude_code |
| incremental-implementation | claude_code |
| verification-loop | claude_code, codex |
| code-review-security | claude_code |
| mcp-builder | claude_code |
| skill-creator | claude_code |
| security-review | codex |
| rust-guard-audit | codex |
| merge-gate | codex |
| repo-intake-audit | codex |

## Awaiting manual install (confirm source first)

| Skill | Agent(s) | Note |
|-------|----------|------|
| parallel-execution-optimizer | claude_code, codex | Confirm canonical source. |
| frontend-design | claude_code | Confirm canonical source. |
| prompt-optimizer | claude_code | Confirm canonical source. |
| hooks-mastery | claude_code | Confirm canonical source. |
| ccstatusline | claude_code | Confirm canonical source. |
| claudekit | claude_code | Confirm canonical source. |
| claude-code-action | claude_code | Confirm canonical source. |
| claude-task-master | claude_code | Confirm canonical source. |
| claude-loop | claude_code | Confirm canonical source. |
| claude-squad | claude_code | Confirm canonical source. |
| claude-mem | claude_code | Memory bridge; do not duplicate memory. |
| superclaude / bmad / archon | claude_code | Frameworks; extract patterns, do not import wholesale. |
| official-anthropic-skills-repo | claude_code | Intake-first; inspect before adopting. |
| token-saving-audit | codex | Confirm canonical source. |
| local-coordinator, status-summarizer, memory-compressor, handoff-summarizer, top-5-next-actions-reporter | hermes | Read-only; no execution. |
| morning-dashboard-artifact, ghoti-command-dashboard-artifact, gmail-calendar-figma-connectors, github-notion-connector-view, prompt-memory-manager | chatgpt_cowork | Artifact specs, not live integrations. |

## Rules

- Never overwrite global/user skill folders. Install into a project-scoped
  location chosen by the human.
- Run any repo-backed skill source through repo intake first.
- Listing a skill never installs it; update the registry only after a reviewed
  install.
