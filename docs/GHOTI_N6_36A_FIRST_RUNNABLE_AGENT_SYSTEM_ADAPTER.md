# GHOTI N+6.36A — First Runnable Plug-and-Play Agent System Adapter

## Overview

N+6.36A takes the next step toward actually running an external agent system.
Based on the N+6.35A inspection findings, **claude_swarm** is selected as the
first runnable adapter target. A Ghoti-native adapter reads its package metadata,
builds a no-op dry-run plan, and validates it through the N+6.33A dual gate —
**without installing, importing, or executing any code from claude_swarm**.

**Selected system:** `claude_swarm` — Python ≥3.11, MIT, native `--dry-run` flag.

**Builds on:** N+6.35A (agent systems inventory), N+6.34A (CUA adapter), N+6.33A (dual gate).

---

## Why claude_swarm was selected first

Selection order per the mission spec:
1. hermes-paperclip-adapter — requires Hermes + Paperclip reviewed first; no standalone no-op entrypoint → **deferred**
2. **claude_swarm** (selected) — Python, MIT, no Docker/MCP/hooks, native `--dry-run` flag

`claude_swarm` is the safest first adapter:
- Pure Python ≥3.11, MIT license, pip-installable with no system dependencies.
- Has a `--dry-run` flag (`claude-swarm --dry-run "task"`) that shows the decomposed task plan without launching any real agents. No API key needed to inspect the plan shape.
- Coordinator/worker plan shape (`SwarmTask`, `SwarmConfig`) maps cleanly onto the Ghoti policy checker's allowed capability set.
- No Docker container, no MCP server, no hooks daemon.

## Deferred systems

| System | Reason |
|--------|--------|
| `hermes_paperclip_adapter` | Needs Hermes + Paperclip reviewed first |
| `am_will_swarms` | SECOND_READY; no license confirmed — do not copy code |
| `clawteam` | Ships `clawteam-mcp` server — MCP must not be enabled |
| `ruflo` | MCP server + hooks daemon; install scripts need line-by-line review |
| `ecc` | Ships `hooks.json` (PreToolUse/PreToolWrite) — hooks must never be installed |
| `paperclip` | Requires Docker |

---

## What the adapter does

`03_scripts/agent_system_adapter/ghoti_agent_system_adapter.py`:

1. **Detection** — `_detect_target()` scans the gitignored sandbox for supported repos in priority order; returns the first match with a valid `.git/HEAD`.
2. **Metadata read** — `_read_metadata()` reads `pyproject.toml`, `README.md`, `LICENSE` as text. Extracts name, version, license, requires-python, CLI entry point, and `--dry-run` flag. **No code imported.**
3. **No-op plan** — `_build_noop_plan()` produces a 4-step dry-run plan (detect, read metadata, render plan, validate). `dry_run=true`, `live_launch=false`, `live_agent_launch=false`, `requires_human_approval=true`.
4. **Validation** — `_validate_plan()` runs a two-stage gate: pre-filter (globally blocked caps / live_launch flag) then the N+6.33A dual gate.
5. **Arena status** — every result carries `safety_block: { simulation: true, live_execution: false, live_agent_launch: false, … }`.

### Modes

| Flag | Behavior |
|------|----------|
| `--check` | Safety status; no sandbox required |
| `--smoke` | Metadata read + no-op plan + dual-gate validation |

---

## Safe vs. blocked commands

| Command | Status | Notes |
|---------|--------|-------|
| `claude-swarm --dry-run "task"` | **SAFE (isolated profile only)** | Shows plan; no agents launched; requires separate sandbox install |
| `claude-swarm "task"` | **BLOCKED** | Launches real agents; never in Ghoti environment |
| `claude-swarm --demo` | Requires investigation | Demo simulation; would need separate audited milestone |

---

## What is real

- `claude_swarm` repo is already in the gitignored sandbox (`21_repos/third_party_runtime_sandbox/claude_swarm/`).
- Adapter reads `pyproject.toml`, `README.md`, `LICENSE` as text files only.
- No-op plan built entirely from metadata; no code imported from claude_swarm.
- Plan validated through the N+6.33A dual gate (Python adapter + Rust mirror).
- The `--smoke` command runs end-to-end: detect → metadata → plan → validate → result.

## What is NOT live

- No claude_swarm code installed, imported, or executed.
- No real task submitted to any agent.
- No API calls. No API key required.
- No hooks, no MCP, no Docker, no browser.
- No third-party code committed or imported into the Ghoti repo.
- No secrets committed.
- No CUA files from N+6.34A modified.

---

## Files

| File | Change |
|------|--------|
| `03_scripts/agent_system_adapter/ghoti_agent_system_adapter.py` | Adapter (detect, metadata, plan, validate) |
| `03_scripts/agent_system_adapter/check_agent_system_adapter.ps1` | PowerShell status checker |
| `14_context/agent_system_adapter/agent_system_adapter_status_schema.json` | JSON Schema |
| `14_context/agent_system_adapter/README.md` | Context README |
| `docs/GHOTI_N6_36A_FIRST_RUNNABLE_AGENT_SYSTEM_ADAPTER.md` | This document |
| `01_projects/runtime_mvp/tests/test_n6_36a_first_runnable_agent_system_adapter.py` | Tests |
| `14_context/claude_n6_36a_first_runnable_agent_system_adapter.md` | Context snapshot |

No third-party code committed. claude_swarm referenced by sandbox path only.

---

## Validation

```powershell
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_36a_*.py" -v
python 03_scripts/agent_system_adapter/ghoti_agent_system_adapter.py --check --json
python 03_scripts/agent_system_adapter/ghoti_agent_system_adapter.py --smoke --json
python 03_scripts/public_repo_security_audit.py --run --json
python 03_scripts/ghoti_product_launcher.py --status --json
git diff --check
```

---

## Next recommended step (future milestone)

**N+6.37A — claude_swarm isolated dry-run trial:**

In a separate Claude profile / isolated sandbox (not the Ghoti working profile):
1. `pip install` claude_swarm into the isolated environment.
2. Run `claude-swarm --dry-run "inspect repo structure"` against a local fixture.
3. Capture the output plan JSON.
4. Feed it through `ghoti_agent_system_adapter.py --smoke` to confirm dual-gate acceptance.
5. Do NOT run without `--dry-run` until a separate audited milestone + human approval.

**Human approval gate required before any live run.**

---

## Hard rules honored

- No live computer-use. No real OS click/type. No browser account login.
- No hooks installed or enabled. No MCP server enabled. No Docker.
- No third-party code committed or imported.
- No secrets/tokens/cookies committed.
- Feature branch only; no push to main.
- No AI attribution in commits.

---

## Codex Audit Target

`audit/ghoti-agent-codex-n6-36a-first-runnable-agent-system-adapter`
