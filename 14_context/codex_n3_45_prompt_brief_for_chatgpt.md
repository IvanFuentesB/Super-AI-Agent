# N+3.45 Prompt Brief For ChatGPT

Status: prompt design brief.
Date: 2026-05-05

## Goal

Prepare two parallel prompts: one for Claude Code implementation and one for Codex audit/source-check. Keep branches, paths, locks, and final reports separate.

## Shared Rules For Both Prompts

- Start with `git fetch origin`.
- Compare local HEAD to origin.
- Stop on divergence.
- Use the assigned branch only.
- Create or dry-run a lane lock before edits.
- Do not edit files outside assigned paths.
- Do not install, clone, connect MCPs, create accounts, email, post, sell, pay, scrape, apply to jobs, enter giveaways, or use live accounts.
- Do not use external tools unless separately approved.
- Run validation.
- Stage only intentional files.
- Final report must include branch, starting HEAD, new commit hash, pushed yes/no, validation, files changed, dirty files left unstaged, and lane-lock status.

## Claude Prompt Target

Milestone:

```text
N+3.45A - Agent Lane Dashboard Read Card
```

Branch:

```text
feat/ghoti-agent-claude-n3-45-agent-lane-dashboard
```

Owns:

- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/index.html`
- `14_context/agent_lane_dashboard_n3_45.md`

Must not touch unless explicitly designated state owner:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `14_context/compact_memory/`
- `14_context/obsidian_vault/`

Task:

- Add a read-only dashboard route/card for agent lane status.
- Read local `14_context/agent_lanes/active_locks.jsonl`, `lane_status.jsonl`, and `agent_lane_registry.json`.
- Tolerate missing/malformed/empty JSONL.
- No mutation buttons.
- No approve/execute buttons.
- No live actions.

Validation:

- `python 03_scripts/agent_lane_status.py --check`
- `node --check 01_projects/dashboard_mvp/server.js`
- `node --check 01_projects/dashboard_mvp/public/app.js`
- `git diff --check`

Suggested commit:

```text
feat(ghoti): add N+3.45 agent lane dashboard read card
```

## Codex Prompt Target

Milestone:

```text
N+3.45B - External Tool Routing Source-Check Pack
```

Branch:

```text
audit/ghoti-agent-codex-n3-45-external-tool-routing
```

Owns:

- `14_context/codex_n3_45_*.md`

Must not touch:

- dashboard files
- runtime scripts
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- compact memory files
- Obsidian vault files

Task:

- Source-check and risk-classify OpenClaw, Paperclip, Ruflo, CUA, JobSpy, Firecrawl MCP, Glif MCP, Chrome DevTools MCP, agentcy-agents, SalesMaxAI, and connector/account routing candidates.
- Do not install, clone, run, connect, scrape, or use live accounts.
- Produce docs only.

Validation:

- `python 03_scripts/agent_lane_status.py --check`
- `git diff --check`
- targeted doc diff check

Suggested commit:

```text
docs(ghoti): source-check N+3.45 external tool routing
```

## Merge Strategy

- Merge one branch at a time.
- Claude lane should merge first if dashboard implementation is clean.
- Codex lane may merge first if Claude is blocked.
- State docs should be updated only by a designated state-owner follow-up after both branches are reviewed.
