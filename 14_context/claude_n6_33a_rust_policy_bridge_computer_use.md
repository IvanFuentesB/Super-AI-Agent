# Context Snapshot — N+6.33A Rust Policy Bridge ↔ Computer-Use Adapter

**Milestone:** N+6.33A
**Date:** 2026-06-08
**Branch:** `feat/ghoti-agent-claude-n6-33a-rust-policy-bridge-computer-use`
**Base:** `main` (N+6.29B, N+6.30A, N+6.31A, N+6.32A all merged)
**Status:** IMPLEMENTED_AND_PUSHED — awaiting Codex audit

---

## What this milestone does

Wires the existing computer-use dry-run adapter (N+6.29A/B) to the existing Rust
policy checker (N+6.28B) as a **second gate**. A dry-run plan is `accepted` only
when the Python adapter AND the `ghoti_policy_checker` decision both allow it.
The bridge is opt-in (`--rust-bridge`), so the N+6.29A baseline is unchanged.
Everything stays dry-run; no live computer-use is enabled.

## Design

- `_plan_to_swarm_plan()` maps a computer-use plan into the checker's plan shape;
  blocked actions / unsafe URLs set `live_launch`, and capabilities / secrets /
  URLs translate into checker capabilities (unknown ⇒ deny).
- `_mirror_rust_policy_decision()` is an exact Python mirror of the Rust
  `evaluate()` — deterministic, no toolchain needed, authoritative for `accepted`.
- `_invoke_rust_policy_checker()` is an optional, read-only `cargo` cross-check
  (`--rust-cargo`); degrades safely to `available: false` if Rust is absent.
- `accepted = adapter_allowed AND rust_allowed`. When the bridge is engaged,
  `result["ok"]` reflects the combined decision.

## Files

- `03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py` — opt-in bridge
  (mapping, mirror, optional cargo cross-check, CLI flags `--rust-bridge`,
  `--rust-cargo`, `--rust-manifest`).
- `01_projects/runtime_mvp/tests/test_n6_33a_rust_policy_bridge_computer_use.py` —
  21 tests.
- `docs/GHOTI_N6_33A_RUST_POLICY_BRIDGE_COMPUTER_USE.md` — milestone doc.
- `14_context/tool_intake/real_repo_trial_plan_n6_33a.md` — CUA → swarm → Ruflo →
  ECC trial order + DeepSeek routing plan.
- `14_context/hermes_status/hermes_desktop_migration_plan_n6_33a.md` — Hermes
  Desktop migration note (backup `.hermes`; no risky tools first).

## Proof cases (dry-run)

| Plan | adapter | policy | accepted |
|------|---------|--------|----------|
| safe local | allowed | allow | true |
| live launch | blocked | deny | false |
| external URL | blocked | deny | false |
| secret input | blocked | deny | false |
| `file://` authority | blocked | deny | false |
| unknown capability | allowed | deny | false |

## Validation results (this session)

- `cargo test --manifest-path rust/Cargo.toml` → 4 + 15 pass.
- `cargo test --manifest-path rust/ghoti_policy_checker/Cargo.toml` → 4 pass.
- `cargo run ... -- --check` → `deny` (default-deny holds).
- `test_n6_33a_*` → 22 pass (incl. real cargo cross-check; unknown-capability case
  shows the Rust gate denying what the adapter alone would allow).
- `test_n6_29a_*` → 56 pass (baseline preserved).
- `public_repo_security_audit.py --run --json` → `blocking_findings: []`, `ok: true`.
- `ghoti_product_launcher.py --status --json` → `ok: true`.
- `git diff --check` → clean.

## Repo trial plan (summary)

CUA first (isolated computer-use engine), then am-will/swarms or claude-swarm
(Claude swarm), Ruflo later (after install-script review), ECC only in a separate
Claude profile (hooks never enabled in the working profile). All plan-only.

## Hermes Desktop note (summary)

Official NousResearch Hermes Desktop exists. Plan: back up `.hermes` first, keep
all risky tools off, keep the manual bridge authoritative during transition,
re-audit before enabling any capability. Nothing migrated here.

## DeepSeek note (summary)

Research-only routing lane: cheap long-context provider (DeepSeek) for background
summaries / wide passes, Claude for depth. No secrets / private content sent to
any provider until explicitly approved; no API keys committed.

## Hard rules honored

No live computer-use, no real OS input, no browser login, no MCP, no hooks, no
auto-submit, no Docker, no secrets committed, no third-party code committed, no
AI attribution. Feature branch only. The cargo cross-check is local + read-only.

## Codex audit target

`audit/ghoti-agent-codex-n6-33a-rust-policy-bridge-computer-use`
