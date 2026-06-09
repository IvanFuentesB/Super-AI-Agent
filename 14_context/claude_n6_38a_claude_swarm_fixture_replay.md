# Compact Context  --  N+6.38A Claude-Swarm Fixture Replay

**Milestone:** N+6.38A
**Date:** 2026-06-08
**Branch:** `feat/ghoti-agent-claude-n6-38a-claude-swarm-fixture-replay`
**Status:** IMPLEMENTED_AND_PUSHED

---

## Problem

`claude-swarm --dry-run` requires `ANTHROPIC_API_KEY` and calls `decompose_task()` via the Claude API before applying the dry-run skip. This was confirmed in N+6.37A by reading `cli.py:79-83`. Status: BLOCKED for Ghoti provider-free use.

## Solution

Static fixture replay: pre-authored JSON shaped like claude-swarm output. No external execution. No provider API. No API key required.

## Files created

| File | Role |
|------|------|
| `14_context/claude_swarm_fixture/sample_claude_swarm_plan.json` | 5-task static fixture |
| `14_context/claude_swarm_fixture/claude_swarm_fixture_schema.json` | JSON Schema |
| `14_context/claude_swarm_fixture/README.md` | Fixture docs |
| `03_scripts/claude_swarm_fixture/ghoti_claude_swarm_fixture_replay.py` | Wrapper (check/validate/replay) |
| `03_scripts/claude_swarm_fixture/check_claude_swarm_fixture_replay.ps1` | PS1 checker |
| `01_projects/runtime_mvp/tests/test_n6_38a_claude_swarm_fixture_replay.py` | Test suite |
| `docs/GHOTI_N6_38A_CLAUDE_SWARM_FIXTURE_REPLAY.md` | Full docs |

## Safety verdict

| Property | Value |
|----------|-------|
| live_execution | false |
| simulation | true |
| live_agent_launch | false |
| api_key_used | false |
| network_attempted | false |
| provider_called | false |
| external_cli_run | false |

## Key constants (wrapper)

```python
MILESTONE = "N+6.38A"
FIXTURE_RELATIVE = "14_context/claude_swarm_fixture/sample_claude_swarm_plan.json"
SCHEMA_RELATIVE  = "14_context/claude_swarm_fixture/claude_swarm_fixture_schema.json"
_API_KEY_ENV_VARS = ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY", "OPENAI_API_KEY"]
```

## Entry points

- `--check` -> `_run_check()`  --  documents external CLI block, start conditions gap
- `--validate [--fixture PATH]` -> `_run_validate(path)`  --  schema + safety validation
- `--replay [--fixture PATH]` -> `_run_replay(path)`  --  full fixture replay with plan summary

## Start conditions

| Milestone | Status |
|-----------|--------|
| N+6.35B | merged to main |
| N+6.36B | merged to main |
| N+6.37B | merged to main |
| N+6.38B (this) | pending Codex audit gate |
| N+6.39A | blocked until N+6.38B merged |

`claude-swarm --dry-run` BLOCKED: API key required before flag processing.

## Codex audit target

`audit/ghoti-agent-codex-n6-38a-claude-swarm-fixture-replay`

## Next milestone

N+6.39A -- Obsidian memory bridge (requires N+6.38B merged + human approval)
