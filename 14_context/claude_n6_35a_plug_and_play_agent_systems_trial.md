# Context Snapshot — N+6.35A Plug-and-Play Agent Systems Trial

**Milestone:** N+6.35A
**Date:** 2026-06-08
**Branch:** `feat/ghoti-agent-claude-n6-35a-plug-and-play-agent-systems-trial`
**Base:** `main` (N+6.29B, N+6.30A, N+6.31A, N+6.32A, N+6.33A, N+6.33B, N+6.34A all merged)
**Status:** IMPLEMENTED_AND_PUSHED — awaiting Codex audit

---

## What this milestone does

Clones, statically inspects, and classifies 7 plug-and-play agent / swarm repos
into the gitignored runtime sandbox. Builds a Ghoti-native dry-run trial planner
that selects a candidate engine, routes to the correct model tier, and validates
plans through the N+6.33A dual gate — without launching any third-party code.

No CUA files from N+6.34A were modified.

## Design

- `_select_engine()` maps task_type → preferred engine; falls back to lowest trial_order
  among MOST_READY / SECOND_READY / CLI_ONLY. Globally-blocked engines never selected.
- `_route_model()` maps complexity / task_type → model tier
  (Opus/Sonnet/Codex/Hermes/DeepSeek).
- `_build_execution_plan()` emits a 4-step dry-run plan; all actions `dry_run=true`.
- `_validate_plan()` runs pre-filter + N+6.33A dual gate.
- `_check_hooks_blocked()` denies hooks/PreToolUse/PreToolWrite before selector.
- Every result carries `safety_block: { simulation: true, live_execution: false, … }`.

## Repo verdicts

| Repo | Commit | Verdict |
|------|--------|---------|
| claude_swarm | 9b1c556115 | MOST_READY |
| am_will_swarms | 110268148a | SECOND_READY (no license) |
| clawteam | 01198332ef | CLI_ONLY |
| ruflo | d065b15927 | ADAPT_LATER |
| ecc | 90dfd9505d | GOVERNANCE_PATTERNS_ONLY |
| paperclip | 76c88e5855 | ADAPT_LATER |
| hermes_paperclip_adapter | 937ea71a34 | ADAPT_LATER |

## Files

- `03_scripts/agent_systems_trial/ghoti_agent_systems_trial.py`
- `03_scripts/agent_systems_trial/check_agent_systems_trial.ps1`
- `14_context/agent_systems_trial/agent_systems_inventory_n6_35a.json`
- `14_context/agent_systems_trial/README.md`
- `docs/GHOTI_N6_35A_PLUG_AND_PLAY_AGENT_SYSTEMS_TRIAL.md`
- `01_projects/runtime_mvp/tests/test_n6_35a_plug_and_play_agent_systems_trial.py`
- `14_context/claude_n6_35a_plug_and_play_agent_systems_trial.md`

## Validation results (this session)

- `ghoti_agent_systems_trial.py --check --json` → `ok: true`
- `test_n6_35a_*` → 52 pass
- `test_n6_34a_*` → not present on branch (N+6.34A PR #9 not yet merged to main)
- `test_n6_33a_*` → 23 pass (Rust bridge preserved)
- `test_n6_29a_*` → 56 pass (adapter baseline preserved)
- `public_repo_security_audit.py --run --json` → `blocking_findings: []`
- `ghoti_product_launcher.py --status --json` → `ok: true`
- `git diff --check` → clean

## Hard rules honored

No live computer-use. No hooks. No MCP. No Docker. No ECC install.
No third-party code committed or imported. No secrets committed.
Feature branch only. No AI attribution.

## Codex audit target

`audit/ghoti-agent-codex-n6-35a-plug-and-play-agent-systems-trial`
