# Context Snapshot  --  N+6.37A Claude Swarm Isolated Dry Run

**Milestone:** N+6.37A (static-only hardening fix)
**Date:** 2026-06-08
**Branch:** `feat/ghoti-agent-claude-n6-37a-claude-swarm-isolated-dry-run`
**Base:** `origin/main` (N+6.36B)
**Status:** IMPLEMENTED_AND_PUSHED  --  awaiting Codex N+6.37B re-audit

## N+6.37A fix (this update)

Codex BLOCKED N+6.37B: the wrapper's `--probe` and `--demo-mode` could execute
the third-party claude-swarm CLI via a process-spawn call, and the PowerShell
checker invoked `--probe`. Fixed by making the wrapper fully static-only:

- Removed all `subprocess` import/use; no process spawn; no shell.
- `--probe` -> static metadata / PATH inspection only; reports external CLI blocked.
- `--demo-mode` -> hardcoded static simulated plan; never spawns the CLI.
- `--check` -> source scan proving no process-spawn primitives in wrapper or PS1.
- PowerShell checker calls only static-safe modes.
- Explicit fields on every result: `external_cli_executed=false`,
  `subprocess_used=false`, `provider_called=false`, `api_key_used=false`,
  `agents_launched=false`, `live_execution=false`, `simulation=true`.
- Added `TestStaticOnlyNoSubprocess` (subprocess-refusal tests). 48 tests pass.

---

## Critical finding

`claude-swarm --dry-run "task"` is **BLOCKED**. Source inspection of `cli.py`:
- Checks for `ANTHROPIC_API_KEY` and exits if absent (line 79-83)
- Calls `decompose_task()` via Claude API (Phase 1) BEFORE the dry-run skip
- `--dry-run` is NOT a true no-op

This milestone builds the Ghoti safety wrapper, documents the block honestly,
and identifies the safe path forward (`--demo` in isolated scratch, then gated
`--dry-run` with API key in future audited milestone).

## Start condition gap

N+6.35B and N+6.36B not on main when milestone ran (PRs #10 and #11 were drafts).
PR #10 (N+6.35A) merged during this session. Wrapper's `start_conditions` field
documents the gap.

## What was actually run

- File reads: `cli.py`, `demo.py` from claude_swarm sandbox (text only)
- `ghoti_claude_swarm_dry_run.py --check --json` -> `ok: true`
- `ghoti_claude_swarm_dry_run.py --probe --json` -> `execution_status: not_installed`
- No API calls. No agents. No API key.

## What stayed disabled

`--dry-run` (BLOCKED), live agents, hooks, MCP, Docker, browser, API keys, secrets.

## Files

- `03_scripts/claude_swarm_dry_run/ghoti_claude_swarm_dry_run.py`
- `03_scripts/claude_swarm_dry_run/check_claude_swarm_dry_run.ps1`
- `14_context/claude_swarm_dry_run/claude_swarm_dry_run_status_schema.json`
- `14_context/claude_swarm_dry_run/README.md`
- `docs/GHOTI_N6_37A_CLAUDE_SWARM_ISOLATED_DRY_RUN.md`
- `01_projects/runtime_mvp/tests/test_n6_37a_claude_swarm_isolated_dry_run.py`
- `14_context/claude_n6_37a_claude_swarm_isolated_dry_run.md`

## Validation results (this session)

- `test_n6_37a_*` -> all pass
- `ghoti_claude_swarm_dry_run.py --check --json` -> `ok: true`
- `ghoti_claude_swarm_dry_run.py --probe --json` -> `execution_status: not_installed`
- `public_repo_security_audit.py --run --json` -> `blocking_findings: []`
- `ghoti_product_launcher.py --status --json` -> `ok: true`
- `git diff --check` -> clean

## Next step

N+6.38A: `claude-swarm --demo --no-ui` in a fully isolated scratch profile
(no API key needed). Then gated `--dry-run` with API key requires separate
audited milestone + human approval.

## Codex audit target

`audit/ghoti-agent-codex-n6-37a-claude-swarm-isolated-dry-run`
