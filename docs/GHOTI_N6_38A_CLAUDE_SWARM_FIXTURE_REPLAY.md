# GHOTI N+6.38A  --  Claude-Swarm Fixture Replay

**Milestone:** N+6.38A
**Branch:** `feat/ghoti-agent-claude-n6-38a-claude-swarm-fixture-replay`
**Status:** Implemented

---

## Background

N+6.37A established that `claude-swarm --dry-run` is **not a true no-op**: the tool checks `ANTHROPIC_API_KEY` and calls `decompose_task()` via the Claude API _before_ the dry-run skip applies (see `cli.py:79-83`). This blocks safe use in Ghoti's provider-free simulation gate.

N+6.38A solves this with a **fixture replay system**: a static JSON payload shaped like claude-swarm output that Ghoti can load, validate, and render locally  --  no `claude-swarm` binary required, no provider API called, no API key needed.

---

## What was built

### Core files

| File | Purpose |
|------|---------|
| `14_context/claude_swarm_fixture/sample_claude_swarm_plan.json` | Static 5-task fixture (auth refactor scenario) |
| `14_context/claude_swarm_fixture/claude_swarm_fixture_schema.json` | JSON Schema for fixture validation |
| `14_context/claude_swarm_fixture/README.md` | Fixture directory documentation |
| `03_scripts/claude_swarm_fixture/ghoti_claude_swarm_fixture_replay.py` | Python wrapper: validate + replay |
| `03_scripts/claude_swarm_fixture/check_claude_swarm_fixture_replay.ps1` | PowerShell checker (Windows) |
| `01_projects/runtime_mvp/tests/test_n6_38a_claude_swarm_fixture_replay.py` | Test suite (60+ tests) |
| `14_context/claude_n6_38a_claude_swarm_fixture_replay.md` | Compact context snapshot |
| `docs/GHOTI_N6_38A_CLAUDE_SWARM_FIXTURE_REPLAY.md` | This file |

---

## Safety invariants

All fixtures **must** satisfy (enforced by `_validate_fixture_schema()`):

| Property | Required value | Enforcement |
|----------|---------------|-------------|
| `source` | `"static_fixture"` | Schema + code |
| `swarm.dry_run` | `true` | Schema + code |
| `swarm.live_execution` | `false` | Schema + code |
| `swarm.simulation` | `true` | Schema + code |
| `safety.live_execution` | `false` | Schema + code |
| `safety.live_agent_launch` | `false` | Schema + code |
| `safety.api_key_used` | `false` | Schema + code |

Provider API keys in environment -> replay blocked immediately (before fixture loading).

---

## Wrapper interface

```bash
# Check readiness (documents external CLI block)
python 03_scripts/claude_swarm_fixture/ghoti_claude_swarm_fixture_replay.py --check

# Validate a fixture
python 03_scripts/claude_swarm_fixture/ghoti_claude_swarm_fixture_replay.py --validate [--fixture PATH]

# Replay a fixture
python 03_scripts/claude_swarm_fixture/ghoti_claude_swarm_fixture_replay.py --replay [--fixture PATH]
```

Each entry point returns a JSON-serialisable dict with:
```json
{
  "milestone": "N+6.38A",
  "mode": "replay",
  "status": "ok",
  "arena_status": {
    "safety_block": {
      "simulation": true,
      "live_execution": false,
      "live_agent_launch": false,
      "api_key_used": false,
      "network_attempted": false,
      "provider_called": false
    }
  }
}
```

---

## Fixture format

The fixture is shaped like `claude-swarm` dry-run output with additional safety fields. See `claude_swarm_fixture_schema.json` for the full JSON Schema.

Key additions over raw claude-swarm output:
- `source: "static_fixture"`  --  identifies as a fixture, not live output
- `safety` block  --  explicit per-field safety audit
- `swarm.simulation: true`  --  explicit simulation flag

---

## What does NOT happen

- `claude-swarm` is never executed
- No subprocess is launched for any agent
- No provider API call is made
- No API key is read or required
- No network connection is attempted
- No files outside the repo are written

---

## Start conditions

`_run_check()` documents the following gate status:

| Milestone | Status |
|-----------|--------|
| N+6.35B | merged to main |
| N+6.36B | merged to main |
| N+6.37B | merged to main |
| N+6.38B (this) | pending Codex audit gate |
| N+6.39A Obsidian | blocked until N+6.38B merged |

**External CLI still blocked**: `claude-swarm --dry-run` requires `ANTHROPIC_API_KEY` and calls the model decomposition path before the dry-run skip applies. This wrapper avoids that entirely by replaying a pre-authored static fixture.

---

## Tests

```bash
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_38a_*.py" -v
```

Test classes:
- `TestSourceSafety`  --  wrapper never imports or calls `claude_swarm`
- `TestFixtureLoading`  --  valid/invalid fixtures handled correctly
- `TestSchemaValidation`  --  each safety field enforced individually
- `TestOverlapDetection`  --  files claimed by multiple tasks detected
- `TestParallelGroups`  --  topological sort correct
- `TestBlockedPaths`  --  sensitive paths rejected
- `TestApiKeyRefusal`  --  provider API keys block replay
- `TestArenaStatus`  --  arena status shape correct
- `TestCheckMode`  --  `--check` output shape
- `TestFullReplay`  --  end-to-end replay with sample fixture

---

## Codex audit target

`audit/ghoti-agent-codex-n6-38a-claude-swarm-fixture-replay`
