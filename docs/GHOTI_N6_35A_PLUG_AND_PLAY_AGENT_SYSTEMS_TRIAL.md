# GHOTI N+6.35A — Plug-and-Play Agent Systems Trial

## Overview

N+6.35A extends the repo-trial programme (begun in N+6.34A with CUA) to seven
additional plug-and-play agent / swarm systems:

| Repo | Verdict |
|------|---------|
| `claude_swarm` | MOST_READY |
| `am_will_swarms` | SECOND_READY |
| `clawteam` | CLI_ONLY |
| `ruflo` | ADAPT_LATER |
| `ecc` | GOVERNANCE_PATTERNS_ONLY |
| `paperclip` | ADAPT_LATER |
| `hermes_paperclip_adapter` | ADAPT_LATER |

Each repo is cloned into the gitignored runtime sandbox
(`21_repos/third_party_runtime_sandbox/`), statically inspected, classified,
and recorded in the inventory JSON. A Ghoti-native dry-run trial planner
(`ghoti_agent_systems_trial.py`) reads the inventory, selects an engine, routes
to the correct model tier, and validates plans through the N+6.33A dual gate —
**without launching any third-party code**.

**Builds on:** N+6.34A (CUA trial), N+6.33A (Rust policy bridge), N+6.29A/B (adapter).

---

## What is real

- Repos cloned into the gitignored sandbox — real `git clone`, real commits.
- Static inspection of each repo: LICENSE, README, entrypoints, install surface, shell scripts.
- `ghoti_agent_systems_trial.py` reads the inventory and builds dry-run plans.
- Plans validated through the N+6.33A dual gate (Python adapter + Rust mirror).
- 56 tests passing after audit-gate fail-closed and source-verification hardening.

## What is NOT live

- No third-party agent, swarm, coordinator, or worker has been launched.
- No hooks are installed or enabled. No ECC install.
- No Docker container, VM, MCP server, or remote desktop is running.
- No CUA files from N+6.34A have been modified.
- No network calls. No secrets committed. No third-party code imported.

---

## Planner design

`03_scripts/agent_systems_trial/ghoti_agent_systems_trial.py`:

1. **Inventory loading** — reads `agent_systems_inventory_n6_35a.json`.
2. **Engine selection** — `_select_engine()` maps `task_type` to a preferred
   engine and falls back to the lowest `trial_order` among MOST_READY /
   SECOND_READY / CLI_ONLY. An engine may expose a blocked optional surface
   (for example ClawTeam MCP), but every generated plan remains dry-run and
   cannot request that blocked capability.
3. **Model routing** — `_route_model()` picks a model tier:
   - `high` complexity → Claude Opus Max
   - `low` / small fix → Claude Sonnet Max
   - `merge_gate` → Codex Extra High
   - `requires_coordination` → Hermes GPT-5.5 Medium
   - `summary` → DeepSeek (future only; no live calls in N+6.35A)
4. **Plan production** — `_build_execution_plan()` emits a 4-step dry-run plan (read_inventory, detect_sandbox_repo, render_coordinator_plan, validate_through_dual_gate). All steps: `dry_run: true`, `live_launch: false`.
5. **Validation** — `_validate_plan()` runs a two-stage gate:
   - Pre-filter: rejects any globally blocked capability or `live_launch: true`.
   - Dual gate: passes a CU-adapter-compatible plan to `_bridge._run_plan(rust_bridge=True)`.
6. **Hooks refusal** — `_check_hooks_blocked()` denies any task spec containing `hooks`, `enable_hooks`, `install_hooks`, `PreToolUse`, or `PreToolWrite` before reaching the engine selector.
7. **Arena status** — every result carries `safety_block: { simulation: true, live_execution: false, … }`.

---

## Repo verdicts (detail)

### claude_swarm (MOST_READY)
- Python ≥3.11, MIT, `claude-agent-sdk`-based, textual TUI.
- No Docker, no MCP, no hooks. Pure pip install.
- Coordinator/worker plan shape maps cleanly onto the policy checker.
- **Trial order 1.**

### am_will_swarms (SECOND_READY)
- Skills files only (swarm-planner, parallel-task, super-swarm). No install.
- **No license confirmed** — do not copy or import any code until verified.
- **Trial order 2.**

### clawteam (CLI_ONLY)
- Python ≥3.10, MIT, `typer/pydantic/rich`.
- Ships `clawteam-mcp` server — MCP must not be enabled in the Ghoti env.
- Use CLI only. **Trial order 3.**

### ruflo (ADAPT_LATER)
- TypeScript, MIT. `claude-flow` CLI, MCP server, 98+ agents, hooks daemon.
- Install scripts must be read line-by-line before any execution.
- Hooks daemon must never be enabled. **Trial order 4.**

### ecc (GOVERNANCE_PATTERNS_ONLY)
- TypeScript+Python, MIT. Ships `hooks.json` (PreToolUse/PreToolWrite) and `install.sh`.
- Governance/scanner patterns may inform Ghoti; no code imported.
- **Never install hooks.** Review in a separate Claude profile. **Trial order 5.**

### paperclip (ADAPT_LATER)
- TypeScript monorepo, MIT. Requires Docker.
- No live company / team launch. **Trial order 6.**

### hermes_paperclip_adapter (ADAPT_LATER)
- TypeScript, MIT. Runs Hermes as managed employee in Paperclip.
- Requires Hermes + Paperclip reviewed first. **Trial order 7.**

---

## Model routing

| Task | Model tier | Key |
|------|-----------|-----|
| High complexity / integration | Claude Opus Max | `complex_integration` |
| Small fix / low complexity | Claude Sonnet Max | `small_fix` |
| Merge gate / audit | Codex Extra High | `merge_gate` |
| Coordination (multi-agent) | Hermes GPT-5.5 Medium | `coordination` |
| Background summaries | DeepSeek | `summary` (future; no live calls) |

---

## Files

| File | Change |
|------|--------|
| `03_scripts/agent_systems_trial/ghoti_agent_systems_trial.py` | Dry-run trial planner |
| `03_scripts/agent_systems_trial/check_agent_systems_trial.ps1` | PowerShell status checker |
| `14_context/agent_systems_trial/agent_systems_inventory_n6_35a.json` | Repo inventory (7 repos) |
| `14_context/agent_systems_trial/README.md` | Context README |
| `docs/GHOTI_N6_35A_PLUG_AND_PLAY_AGENT_SYSTEMS_TRIAL.md` | This document |
| `01_projects/runtime_mvp/tests/test_n6_35a_plug_and_play_agent_systems_trial.py` | 56 tests |
| `14_context/claude_n6_35a_plug_and_play_agent_systems_trial.md` | Context snapshot |

No third-party code committed. All 7 repos referenced by URL / sandbox path only.

---

## Validation

```powershell
$env:PYTHONPATH = "03_scripts/agent_systems_trial"
python 03_scripts/agent_systems_trial/ghoti_agent_systems_trial.py --check --json
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_35a_*.py" -v
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_34a_*.py" -v
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_33a_*.py" -v
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_29a_*.py" -v
python 03_scripts/public_repo_security_audit.py --run --json
python 03_scripts/ghoti_product_launcher.py --status --json
git diff --check
```

---

## Hard rules honored

- No live computer-use. No real OS click/type. No browser account login.
- No hooks installed or enabled. No ECC install into Ghoti.
- No MCP server enabled. No Docker launched.
- No live Paperclip company launch. No live Ruflo automation.
- No third-party code committed or imported.
- No secrets / tokens / cookies committed.
- Feature branch only; no push to `main`.
- No AI attribution in commits.

---

## Codex Audit Target

`audit/ghoti-agent-codex-n6-35a-plug-and-play-agent-systems-trial`
