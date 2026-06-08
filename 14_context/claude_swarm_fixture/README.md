# claude_swarm_fixture — N+6.38A Provider-Free Fixture Replay

## Purpose

Provides static fixture replay for claude-swarm-shaped output without executing `claude-swarm` or calling any provider API.

## Why this exists

`claude-swarm --dry-run` is **not a true no-op** (N+6.37A finding): it checks `ANTHROPIC_API_KEY` and calls `decompose_task()` via the Claude API before applying the dry-run skip. This makes it unsuitable for Ghoti's provider-free simulation gate.

This fixture system solves that by providing a static JSON fixture shaped like claude-swarm output that can be loaded, validated, and replayed entirely locally.

## Files

| File | Purpose |
|------|---------|
| `sample_claude_swarm_plan.json` | Static 5-task fixture (auth refactor scenario) |
| `claude_swarm_fixture_schema.json` | JSON Schema for fixture validation |
| `README.md` | This file |

## Safety invariants

All fixtures **must** satisfy:
- `source == "static_fixture"` — prevents live execution payloads
- `swarm.dry_run == true` — dry-run flag preserved
- `swarm.live_execution == false` — hard block
- `swarm.simulation == true` — simulation flag required
- `safety.live_execution == false` — redundant safety check
- `safety.live_agent_launch == false` — no agent launch allowed
- `safety.api_key_used == false` — no provider API calls

## Usage

```bash
# Check system readiness (no fixture required)
python 03_scripts/claude_swarm_fixture/ghoti_claude_swarm_fixture_replay.py --check

# Validate a fixture against the schema
python 03_scripts/claude_swarm_fixture/ghoti_claude_swarm_fixture_replay.py --validate

# Replay the default fixture
python 03_scripts/claude_swarm_fixture/ghoti_claude_swarm_fixture_replay.py --replay

# Replay a custom fixture
python 03_scripts/claude_swarm_fixture/ghoti_claude_swarm_fixture_replay.py --replay --fixture path/to/plan.json

# PowerShell checker (Windows)
.\03_scripts\claude_swarm_fixture\check_claude_swarm_fixture_replay.ps1 -Verbose
```

## Fixture format

See `claude_swarm_fixture_schema.json` for the full schema. Minimum required fields:

```json
{
  "fixture_id": "unique-id",
  "source": "static_fixture",
  "swarm": {
    "name": "swarm-name",
    "dry_run": true,
    "live_execution": false,
    "simulation": true
  },
  "tasks": [
    {
      "id": "task-1",
      "description": "...",
      "agent_type": "coder",
      "status": "pending",
      "dependencies": [],
      "files_to_modify": []
    }
  ],
  "safety": {
    "live_execution": false,
    "simulation": true,
    "live_agent_launch": false,
    "api_key_used": false,
    "network_attempted": false
  }
}
```

## Milestone

N+6.38A — part of the Ghoti supervised agent systems trial sequence.
