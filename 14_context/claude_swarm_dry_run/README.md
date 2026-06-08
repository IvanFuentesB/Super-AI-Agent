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

## Wrapper modes

- `--check`: Safety status, documents dry-run block reason
- `--probe`: `--version` check only (no API call)
- `--demo-mode`: Runs `--demo --no-ui` in temp scratch dir (no API key)

## Start condition gap

N+6.35B and N+6.36B are not yet merged to main at the time of this milestone.
PRs #10 and #11 are drafts awaiting Codex audit. This is documented in the
wrapper's `start_conditions` field and should be resolved before any live run.

## Next step

N+6.38A (proposed): After N+6.36B merges, run `claude-swarm --demo --no-ui`
in a fully isolated scratch profile to prove the TUI runs safely without API keys.
Then propose a gated path for eventually providing a real API key in an
isolated environment for a true `--dry-run` trial.
