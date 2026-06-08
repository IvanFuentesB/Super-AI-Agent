# GHOTI N+6.33A — Rust Policy Bridge ↔ Computer-Use Dry-Run Adapter

## Overview

N+6.33A connects two pieces that already exist on `main` but were not yet wired
together:

- the **computer-use dry-run adapter** (`ghoti_computer_use_adapter.py`, N+6.29A/B), and
- the **Rust policy checker** (`rust/ghoti_policy_checker`, N+6.28B).

The result is a **dual-gate** dry-run flow. A proposed computer-use plan is only
`accepted` when **both** gates allow it:

1. **Gate 1 — Python adapter:** target / URL / action-type / secret / capability checks.
2. **Gate 2 — policy checker:** the `ghoti_policy_checker` decision for the same plan.

Nothing here enables live computer-use. Everything stays dry-run.

**Builds on:** N+6.29A/B (adapter), N+6.28B (policy checker), N+6.31A (Rust runtime base).

---

## What the bridge does

The bridge is **opt-in**. Default behavior of the adapter is unchanged, so the
N+6.29A contract and its 56 tests are untouched.

| Mode | Flag | Behavior |
|------|------|----------|
| Baseline | (none) | N+6.29A dry-run contract; `rust_policy_bridge_ready: false` |
| Bridge (mirror) | `--rust-bridge` | Second gate via a deterministic Python mirror of the checker |
| Bridge + cargo | `--rust-bridge --rust-cargo` | Also cross-checks the real `cargo` binary (read-only) |

### How a plan maps to the checker

`_plan_to_swarm_plan()` translates a computer-use plan into the policy checker's
plan shape (`plan_id`, `dry_run`, `live_launch`, `requires_human_approval`,
`capabilities`):

- `dry_run` is always `true` — this adapter is dry-run only.
- A blocked action type (`real_click`, `navigate_url`, `login`, …) or an unsafe
  `target_url` sets `live_launch: true`.
- Requested computer-use capabilities, blocked actions, an unsafe URL, and any
  secret-bearing action are translated into policy-checker capabilities
  (`browser`, `computer_use`, `account`, `secrets`, `money`, `mass_message`, …).
- Anything outside the checker's allow-list lands in its `unknown` bucket, which
  is also a deny — default-deny holds.

### The mirror

`_mirror_rust_policy_decision()` reimplements `rust/ghoti_policy_checker/src/main.rs`
`evaluate()` exactly (same allowed/blocked capability sets, same normalization,
same reason strings). It needs no toolchain, so the dual-gate decision is
deterministic in CI and on machines without Rust. When `--rust-cargo` is passed,
the real binary is invoked as a **read-only** cross-check
(`cargo run -- --input <tmp>`); the binary's own safety block reports
`network_used: false, writes_files: false, launches_agents: false`. The mirror
remains authoritative for the `accepted` decision; on any cargo failure the
cross-check degrades to `available: false` and the mirror still stands.

---

## Proof cases (tests)

`01_projects/runtime_mvp/tests/test_n6_33a_rust_policy_bridge_computer_use.py`
(21 tests) proves, for dry-run plans:

| # | Plan | Gate 1 (adapter) | Gate 2 (policy) | `accepted` |
|---|------|------------------|-----------------|------------|
| 1 | safe local dry-run | allowed | allow | **true** |
| 2 | live launch (`real_click`) | blocked | deny (`live_launch_requested`) | false |
| 3 | external URL | blocked | deny (`browser` blocked) | false |
| 4 | secret input | blocked | deny (`secrets` blocked) | false |
| 5 | `file://` authority | blocked | deny (`browser` blocked) | false |

Additional tests cover: the bridge being opt-in (baseline preserved), the
plan→swarm-plan mapping, mirror semantics + capability normalization, the dry-run
safety invariants surviving acceptance, and an optional `cargo` cross-check that
asserts the real binary agrees with the mirror for all five cases (skipped when
Rust is absent).

---

## Files

| File | Change |
|------|--------|
| `03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py` | Added opt-in bridge: mapping, mirror, optional cargo cross-check, CLI flags |
| `01_projects/runtime_mvp/tests/test_n6_33a_rust_policy_bridge_computer_use.py` | 21 tests |
| `docs/GHOTI_N6_33A_RUST_POLICY_BRIDGE_COMPUTER_USE.md` | This document |
| `14_context/claude_n6_33a_rust_policy_bridge_computer_use.md` | Context snapshot |
| `14_context/tool_intake/real_repo_trial_plan_n6_33a.md` | Concrete repo trial plan + DeepSeek routing plan |
| `14_context/hermes_status/hermes_desktop_migration_plan_n6_33a.md` | Hermes Desktop migration note |

No third-party code is committed. The five referenced repos (CUA, UI-TARS,
Ruflo, am-will/swarms, claude-swarm, ECC) are referenced by URL / prior static
inspection only.

---

## Hard rules honored

- No live computer-use. No real OS click/type. No browser account login.
- No MCP setup. No hooks enabled. No auto-submit. No Docker.
- No secrets / tokens / cookies committed.
- No third-party code committed.
- The optional `cargo` cross-check is local and read-only; it neither installs
  nor launches anything.
- Feature branch only; no push to `main`.

---

## Validation

```
$env:CARGO_TARGET_DIR = "$env:TEMP\ghoti_rust_target"
cargo test --manifest-path rust/Cargo.toml
cargo test --manifest-path rust/ghoti_policy_checker/Cargo.toml
cargo run --manifest-path rust/ghoti_policy_checker/Cargo.toml -- --check
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_33a_*.py" -v
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_29a_*.py" -v
python 03_scripts/public_repo_security_audit.py --run --json
python 03_scripts/ghoti_product_launcher.py --status --json
git diff --check
git show --check --stat HEAD
```

---

## Codex Audit Target

`audit/ghoti-agent-codex-n6-33a-rust-policy-bridge-computer-use`
