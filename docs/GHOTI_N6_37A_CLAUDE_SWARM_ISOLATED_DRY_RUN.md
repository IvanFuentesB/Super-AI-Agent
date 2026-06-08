# GHOTI N+6.37A — Isolated claude-swarm dry-run execution trial

## Overview

N+6.37A attempts the first real external tool execution for the claude_swarm
candidate selected in N+6.36A. After source-code inspection of `cli.py`, the
planned `--dry-run` execution is **BLOCKED**: it requires `ANTHROPIC_API_KEY`
and makes Claude API calls before the dry-run skip applies. The wrapper is built,
tests pass, and the honest status is documented.

**Builds on:** N+6.36A (adapter), N+6.35A (inventory), N+6.33A (dual gate).

---

## Critical finding: --dry-run is NOT a true no-op

Source: `claude_swarm/cli.py`, `_run_swarm()`:

```python
# Line 79: API key check happens BEFORE any flag processing
if not os.environ.get("ANTHROPIC_API_KEY"):
    click.echo("Error: ANTHROPIC_API_KEY environment variable not set.")
    sys.exit(1)

# Phase 1: decompose_task() calls Claude API
plan = await decompose_task(prompt=task, cwd=cwd, model=model)

# ONLY THEN is the dry_run flag checked:
if dry_run:
    ui.console.print("[yellow]Dry run — not executing tasks[/yellow]")
    return
```

`--dry-run` calls the Claude API (Opus 4.6 for task decomposition) before returning.
It is not a no-op. Running it without an API key exits with code 1.

**Therefore: `claude-swarm --dry-run "task"` is BLOCKED in the Ghoti environment.**

---

## Command status table

| Command | Status | Reason |
|---------|--------|--------|
| `claude-swarm --version` | **SAFE** | No API call, no agents, no network |
| `claude-swarm --help` | **SAFE** | No execution |
| `claude-swarm --demo --no-ui` | **CONDITIONALLY SAFE** | No API key; writes to `~/.claude-swarm/sessions/`; isolated scratch only |
| `claude-swarm --dry-run "task"` | **BLOCKED** | Requires API key + makes Claude API calls |
| `claude-swarm "task"` | **BLOCKED** | Launches real agents |

---

## What the wrapper does

`03_scripts/claude_swarm_dry_run/ghoti_claude_swarm_dry_run.py`:

1. **`--check`** — Safety status, tool detection, documents the dry-run block reason and start condition gap.
2. **`--probe`** — Runs `claude-swarm --version` only (no API call). Reports tool availability without execution.
3. **`--demo-mode`** — Runs `claude-swarm --demo --no-ui` in a temp scratch directory with `HOME` redirected; cleans up after. Requires no API key. Blocked if any API key env var is set.

Guards enforced by the wrapper:
- Refuses any invocation with `ANTHROPIC_API_KEY` (or `CLAUDE_API_KEY`, `OPENAI_API_KEY`) set
- Refuses `--dry-run` flag (documents it requires API key)
- Refuses any output path inside the repo root
- Refuses blocked flags
- Requires an explicit safe mode flag (`--version`, `--demo`, `--help`)
- Emits Arena status: `simulation=true, live_execution=false, live_agent_launch=false`

---

## Start condition gap

N+6.35B and N+6.36B were not yet merged to main when this milestone ran.
PRs #10 (N+6.35A) and #11 (N+6.36A) are in the audit queue.
The wrapper documents this in its `start_conditions` field.
**Note: PR #10 (N+6.35A) merged during this session.**

---

## What was actually run

- Source-code inspection of `claude_swarm/cli.py` (text read only)
- `ghoti_claude_swarm_dry_run.py --check --json` — safety status, no external calls
- `ghoti_claude_swarm_dry_run.py --probe --json` — tool detection (not installed → `not_installed`)
- No claude_swarm code imported or executed
- No API calls. No API key used.
- No agents launched.
- No files written outside the Ghoti repo.

## What stayed disabled

- `claude-swarm --dry-run` (BLOCKED: requires API key + API calls)
- Live agent launch
- Hooks, MCP, Docker, browser, account actions, secrets
- Any claude_swarm import

---

## Files

| File | Change |
|------|--------|
| `03_scripts/claude_swarm_dry_run/ghoti_claude_swarm_dry_run.py` | Safety wrapper |
| `03_scripts/claude_swarm_dry_run/check_claude_swarm_dry_run.ps1` | PowerShell checker |
| `14_context/claude_swarm_dry_run/claude_swarm_dry_run_status_schema.json` | JSON Schema |
| `14_context/claude_swarm_dry_run/README.md` | Context README |
| `docs/GHOTI_N6_37A_CLAUDE_SWARM_ISOLATED_DRY_RUN.md` | This document |
| `01_projects/runtime_mvp/tests/test_n6_37a_claude_swarm_isolated_dry_run.py` | Tests |
| `14_context/claude_n6_37a_claude_swarm_isolated_dry_run.md` | Context snapshot |

No third-party code committed. claude_swarm referenced by sandbox path only.

---

## Validation

```powershell
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_37a_*.py" -v
python 03_scripts/claude_swarm_dry_run/ghoti_claude_swarm_dry_run.py --check --json
python 03_scripts/claude_swarm_dry_run/ghoti_claude_swarm_dry_run.py --probe --json
python 03_scripts/public_repo_security_audit.py --run --json
python 03_scripts/ghoti_product_launcher.py --status --json
git diff --check
```

---

## Next recommended step

**N+6.38A — claude-swarm --demo isolated trial:**

In a separate isolated profile (not the Ghoti working profile):
1. `pip install claude-swarm` in the isolated environment.
2. Run `claude-swarm --demo --no-ui` with `HOME` pointed at a temp scratch directory.
3. Capture session JSONL and feed through `ghoti_agent_system_adapter.py --smoke`.
4. Confirm no API calls, no agents launched, safe file writes only to scratch.

A separate gated milestone for `--dry-run` with API key requires:
- Isolated profile with no Ghoti repo access
- API key approved for that environment only
- Human approval + separate audited milestone
- Dual-gate green before any real task

---

## Hard rules honored

- No live agents. No API keys. No account login. No browser.
- No hooks, MCP, Docker, auto-submit.
- No third-party code committed or imported.
- No secrets committed. Feature branch only. No AI attribution.

---

## Codex Audit Target

`audit/ghoti-agent-codex-n6-37a-claude-swarm-isolated-dry-run`
