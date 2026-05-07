# N+3.43 Parallel Agent Lane Readiness

Status: Codex readiness audit/spec only.
Date: 2026-05-05

## Verdict

The repo is ready to implement parallel-agent lane scaffolding after N+3.34 is pushed.

Reason:

- Money OS local loop is now usable.
- Obsidian and compact memory scaffolding exist.
- Shared state files have become important enough to need locks.
- The earlier N+3.38/N+3.29 overlap proved that parallel agents are valuable but unsafe without lane rules.

## Why Parallel Agents Are Useful Now

Parallel agents can help Ghoti move faster without wasting credits:

- Claude Code can implement bounded code/script/dashboard changes.
- Codex can audit, source-check, and prepare specs without touching runtime.
- ChatGPT can hold strategy and prompt architecture.
- Gemma/Ollama can draft cheap local summaries and compression artifacts.
- Future workers can specialize in UI, data, content, jobs, source research, or external-tool planning.

Parallel agents are useful only if they do not corrupt shared memory, stage unrelated dirt, or work from stale commits.

## What Is Ready

Ready foundations:

- branch `feat/ghoti-visible-operator-stack`
- Money OS local workflow through N+3.32
- Obsidian vault scaffold through N+3.34
- compact memory pointer files through N+3.34
- N+3.39 parallel-agent lane rules
- N+3.41 connector/account policy
- N+3.42 Obsidian readiness lock
- recurring dirty-state awareness

## What Is Missing

Still missing:

- `14_context/agent_lanes/`
- lane lock templates
- lane status templates
- active lock examples
- stale-work protocol in a file future agents can read quickly
- optional stdlib helper for status/check/heartbeat
- branch naming examples
- merge protocol checklist
- stop conditions in compact form

## Branch-Per-Agent Requirement

Default branch naming:

```text
feat/ghoti-agent-<agent_id>-<task>
```

Examples:

```text
feat/ghoti-agent-claude-n3-43-lanes
feat/ghoti-agent-codex-n3-43-audit
feat/ghoti-agent-gemma-memory-draft
```

Exception:

- The operator may assign a specific agent to work directly on `feat/ghoti-visible-operator-stack`.
- If so, the agent must create/update a lane lock and follow the pull/context protocol first.

## Lock Files Requirement

Suggested folder:

```text
14_context/agent_lanes/
```

Suggested active lock path:

```text
14_context/agent_lanes/<agent_id>_active_lock.md
```

Suggested lock format:

```yaml
agent_id: codex_n3_43
model_or_tool: Codex
branch: feat/ghoti-visible-operator-stack
current_task: audit N+3.34 and plan agent lane scaffolding
locked_files:
  - 14_context/current_state.md
  - 14_context/next_actions.md
started_at: 2026-05-05T00:00:00Z
expected_outputs:
  - 14_context/codex_n3_43_post_n3_34_audit.md
  - 14_context/codex_n3_43_parallel_agent_lane_readiness.md
safe_to_interrupt: true
heartbeat_at: 2026-05-05T00:00:00Z
status: active
```

Locks are advisory at first, but future agents must treat them as real.

## Status Beacon Requirement

Suggested status path:

```text
14_context/agent_lanes/<agent_id>_status.md
```

Status beacon should include:

- current task
- branch
- local HEAD
- origin HEAD
- dirty files observed
- files being edited
- last validation run
- last heartbeat
- blockers
- next intended command
- safe interruption notes

## One Writer Per Shared File Rule

Only one active agent may write a shared state file at a time.

Files requiring locks:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `14_context/compact_memory/*`
- `14_context/obsidian_vault/00_Index.md`
- `14_context/obsidian_vault/01_Current_State.md`
- `14_context/obsidian_vault/02_Next_Actions.md`
- `14_context/obsidian_vault/03_Decisions.md`
- `14_context/obsidian_vault/08_Dirty_State.md`

If two agents need to update the same shared file, one agent becomes the integrator and the other writes a separate audit/handoff doc.

## New Computer / New Agent Identity Rules

Every new computer or agent needs:

- stable `agent_id`
- machine label
- branch
- role/lane
- write scope
- active lock file
- status beacon
- fetch/pull verification
- dirty-state snapshot
- human approval scope

No new agent should begin by editing shared state files. It should read lane docs first, then claim a lock.

## Merge Protocol

Before commit:

1. `git fetch origin`
2. compare local HEAD and origin HEAD
3. inspect `git status --short`
4. inspect active lane locks
5. verify no locked shared file conflict
6. run milestone validations
7. stage only whitelisted files
8. inspect `git diff --cached --name-status`
9. commit with exact milestone message
10. push
11. update lane status or final report

No agent may use `git reset --hard`, delete unrelated files, or stage broad dirt without explicit human approval.

## Stop Conditions

An agent must stop and report if:

- branch is diverged from origin
- dirty files conflict with intended edits
- another active lock owns a needed shared file
- a required external tool/install/account is missing
- a task would post, send, sell, pay, scrape, login, or create accounts
- code requires secrets
- validation fails and fix would exceed scope
- the agent cannot tell whether it is overwriting user work

## Readiness Decision

Ready after N+3.34 is pushed.

Recommended next implementation:

```text
N+3.43 Claude - Agent Lane Locks And Parallel Execution Scaffolding
```

This should be scaffolding only. No external agents should be installed or run yet.
