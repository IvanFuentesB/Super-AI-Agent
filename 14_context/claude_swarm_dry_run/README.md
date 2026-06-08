# Claude Swarm Dry Run Context (N+6.37A)

## Key finding

`claude-swarm --dry-run "task"` is **BLOCKED** in the Ghoti environment.

Source-code inspection of `cli.py` reveals:
1. The CLI checks for `ANTHROPIC_API_KEY` and exits if not set (line 79–83).
2. `--dry-run` calls `decompose_task()` via the Claude API (Phase 1) BEFORE applying the dry-run skip.
3. Only AFTER the API decomposition call does it check `if dry_run: return`.

So `--dry-run` is NOT a true no-op — it makes Claude API calls.

## Safe alternatives

| Command | Status | Notes |
|---------|--------|-------|
| `claude-swarm --version` | SAFE | No API call, no agents |
| `claude-swarm --demo --no-ui` | CONDITIONALLY SAFE | No API key needed; writes to `~/.claude-swarm/sessions/`; use isolated scratch only |
| `claude-swarm --dry-run "task"` | **BLOCKED** | Requires API key + makes Claude API calls |
| `claude-swarm "task"` | **BLOCKED** | Launches real agents |

## Wrapper modes (STATIC-ONLY)

The wrapper is fully static-only: it never imports `subprocess`, never spawns a
process, and never executes the external `claude-swarm` CLI.

- `--check`: Safety status + source scan (proves no process-spawn primitives in
  the wrapper or the PowerShell checker); documents the dry-run block reason
- `--probe`: Static metadata / PATH inspection only — reports tool presence
  without executing it (`probe_result` is always `null`)
- `--demo-mode`: Emits a hardcoded static simulated plan; never spawns the CLI

Every result carries explicit proof fields: `external_cli_executed=false`,
`subprocess_used=false`, `provider_called=false`, `api_key_used=false`,
`agents_launched=false`, `live_execution=false`, `simulation=true`.

## Static-only hardening (N+6.37A fix)

Codex BLOCKED N+6.37B because the earlier wrapper could execute the third-party
CLI through a process-spawn call in `--probe` / `--demo-mode`, and the checker
invoked `--probe`. The wrapper is now static-only and the checker only calls
static-safe modes. This unblocks the N+6.37B re-audit.

## Start condition status

N+6.35B and N+6.36B are merged to main. The wrapper documents the current status
in its `start_conditions` field.

## Next step

N+6.38A (provider-free fixture replay) is the safe path forward. An isolated
`claude-swarm --demo --no-ui` run remains gated behind a separate audited
milestone and is NOT performed by this wrapper.
