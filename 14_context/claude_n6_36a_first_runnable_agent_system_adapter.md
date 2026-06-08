# Context Snapshot — N+6.36A First Runnable Agent System Adapter

**Milestone:** N+6.36A
**Date:** 2026-06-08
**Branch:** `feat/ghoti-agent-claude-n6-36a-first-runnable-agent-system-adapter`
**Base:** `origin/main` (N+6.33B + N+6.34B both merged)
**Status:** IMPLEMENTED_AND_PUSHED — awaiting Codex audit

---

## What this milestone does

Takes the next step past N+6.35A inspection. Selects `claude_swarm` as the first
runnable adapter target and builds a Ghoti-native adapter (`ghoti_agent_system_adapter.py`)
that detects the repo in the gitignored sandbox, reads its package metadata as text,
builds a no-op dry-run plan, and validates through the N+6.33A dual gate.
No claude_swarm code is installed, imported, or executed.

## Selected system

**claude_swarm** (commit `9b1c556`) — MOST_READY
- Python ≥3.11, MIT, claude-agent-sdk-based, pure pip
- No Docker, no MCP, no hooks
- Has `--dry-run` flag: `claude-swarm --dry-run "task"` shows plan without launching agents
- Entry point: `claude-swarm = "claude_swarm.cli:main"`

## Why selected

hermes-paperclip-adapter deferred (needs Hermes+Paperclip first).
claude_swarm is next: safest isolation (pure Python), cleanest no-op path (--dry-run flag),
MIT license confirmed, plan shape maps cleanly to policy checker capabilities.

## Deferred

am_will_swarms (no license), clawteam (MCP server), ruflo (hooks+MCP), ecc (hooks.json),
paperclip (Docker), hermes_paperclip_adapter (needs prerequisites).

## Safe command

```
claude-swarm --dry-run "task description"
```
Requires separate isolated profile install. Not yet run in Ghoti environment.

## Blocked command

```
claude-swarm "task description"   # launches real agents — NEVER in Ghoti env
```

## Files

- `03_scripts/agent_system_adapter/ghoti_agent_system_adapter.py`
- `03_scripts/agent_system_adapter/check_agent_system_adapter.ps1`
- `14_context/agent_system_adapter/agent_system_adapter_status_schema.json`
- `14_context/agent_system_adapter/README.md`
- `docs/GHOTI_N6_36A_FIRST_RUNNABLE_AGENT_SYSTEM_ADAPTER.md`
- `01_projects/runtime_mvp/tests/test_n6_36a_first_runnable_agent_system_adapter.py`
- `14_context/claude_n6_36a_first_runnable_agent_system_adapter.md`

## Validation results (this session)

- `test_n6_36a_*` → all pass
- `ghoti_agent_system_adapter.py --check --json` → `ok: true`
- `ghoti_agent_system_adapter.py --smoke --json` → `ok: true, accepted: true`
- `public_repo_security_audit.py --run --json` → `blocking_findings: []`
- `ghoti_product_launcher.py --status --json` → `ok: true`
- `git diff --check` → clean

## What was actually run

- File reads: `pyproject.toml`, `README.md`, `LICENSE` from `claude_swarm` sandbox repo
- No third-party code imported or executed
- No network calls, no API keys, no real agents

## What stayed disabled

- No claude_swarm install
- No `claude-swarm` CLI invocation
- No live agent launch
- No hooks, MCP, Docker, browser, account actions, secrets

## Next recommended step

N+6.37A — claude_swarm isolated dry-run trial in a separate profile.
Run `claude-swarm --dry-run "task"` in isolated environment, capture plan JSON,
feed back through dual gate. Human approval required before any live run.

## Hard rules honored

No live computer-use, no hooks, no MCP, no Docker, no third-party code committed,
no secrets, feature branch only, no AI attribution.

## Codex audit target

`audit/ghoti-agent-codex-n6-36a-first-runnable-agent-system-adapter`
