# Context Snapshot — N+6.34A CUA Isolated Dry-Run / Observation Adapter

**Milestone:** N+6.34A
**Date:** 2026-06-08
**Branch:** `feat/ghoti-agent-claude-n6-34a-cua-real-repo-trial`
**Base:** `main` (N+6.33B merged — `d074566`)
**Status:** IMPLEMENTED_AND_PUSHED — awaiting Codex audit

---

## What this milestone does

First real plug-and-play repo trial: TryCUA/CUA is cloned into the gitignored
sandbox, its metadata is read from the live clone, a dry-run observation plan is
generated and validated through the N+6.33A dual gate (Python adapter + Rust policy
checker).

## CUA sandbox

- **Path:** `21_repos/third_party_runtime_sandbox/cua` (gitignored, `.gitignore:149`)
- **Clone commit:** `2925b491c20595ae850e3e4a05d6fea188e8f40a`
- **License:** MIT (Copyright 2025 Cua AI, Inc.) — verified from live `LICENSE.md`
- **Package:** `cua-workspace` — Python >=3.12, websocket-client, aiohttp, pillow,
  pydantic, cua-core (posthog telemetry fires on import)
- **Shell scripts:** 175 in sandbox (risk surface metric — none executed)
- **Runtime requirements:** Docker/QEMU/Lume VM + live OS websocket — not used here
- **CUA code imported:** false. **CUA code executed:** false.

## Adapter design

Three gates:
- **Gate 0:** CUA trial pre-filter — denies docker, lume, qemu, kasm, mcp,
  vm_launch, shell_execution, telemetry_upload, computer_use before reaching bridge.
- **Gate 1:** N+6.29A Python adapter — target/URL/action/secret/capability checks.
- **Gate 2:** N+6.33A Rust policy checker mirror — default-deny; unknown caps denied.

`accepted = Gate 1 allowed AND Gate 2 allowed`.

## Dry-run trial plan (4 actions)

| Action | Type | Target |
|--------|------|--------|
| cua_a1_check_sandbox | check_state | 21_repos/third_party_runtime_sandbox/cua |
| cua_a2_read_license | read_fixture | .../LICENSE.md |
| cua_a3_read_manifest | read_fixture | .../pyproject.toml |
| cua_a4_generate_report | generate_report | 14_context/cua_trial/ |

Result: adapter allowed ✓, Rust policy allowed ✓, **accepted ✓**.

## Files

- `03_scripts/cua_trial/ghoti_cua_trial_adapter.py`
- `03_scripts/cua_trial/check_cua_trial.ps1`
- `14_context/cua_trial/cua_trial_status_schema.json`
- `14_context/cua_trial/README.md`
- `docs/GHOTI_N6_34A_CUA_REAL_REPO_TRIAL.md`
- `01_projects/runtime_mvp/tests/test_n6_34a_cua_real_repo_trial.py`
- `14_context/claude_n6_34a_cua_real_repo_trial.md`

## Validation results (this session)

- `cargo test --manifest-path rust/Cargo.toml` → 4 + 15 + 0 pass
- `cargo run ... -- --check` → `deny` (default-deny holds)
- `test_n6_34a_*` → **44 pass**
- `test_n6_33a_*` → 22 pass (baseline preserved)
- `test_n6_32a_*` attribution guard → 9 pass
- `public_repo_security_audit.py --run --json` → `blocking_findings: []`, `ok: true`
- `ghoti_product_launcher.py --status --json` → `ok: true`
- `git diff --check` → clean

## What was actually run

- `git clone --depth=1 --no-tags --template="" https://github.com/trycua/cua`
  → sandbox (gitignored; not staged)
- Read `LICENSE.md`, `pyproject.toml`, `Development.md` from sandbox (no execution)
- Ran adapter `--check` and `--trial` in Python (no CUA code imported)
- Ran dual gate (Python mirror + cargo cross-check) on observation plan

## What stayed disabled

No live OS input. No Docker/VM. No MCP. No browser. No account login. No secrets.
No telemetry triggered. No CUA code imported or executed. No shell scripts run.
No real computer-use performed.

## Next step

An actual CUA sandbox execution trial — separate audited milestone, human approval,
isolated OS profile/VM, no Ghoti repo access, no real accounts, no secrets.

## Hard rules honored

Push feature branch only. No main push. No live OS action. No Docker/VM. No MCP.
No account login. No secrets committed. No third-party code committed. No AI
attribution. Author + committer: IvanFuentesB only.

## Codex audit target

`audit/ghoti-agent-codex-n6-34a-cua-real-repo-trial`
