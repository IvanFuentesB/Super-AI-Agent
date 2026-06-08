# Context Snapshot - N+6.31A Rust Runtime Base

**Milestone:** N+6.31A
**Date:** 2026-06-08
**Branch:** `feat/ghoti-agent-claude-n6-31a-rust-runtime-base`
**Base:** `ca90fbd` (N+6.28B Rust policy checker merged)
**Status:** IMPLEMENTED_AND_PUSHED - awaiting Codex audit

---

## What This Milestone Does

N+6.31A establishes the Rust workspace and adds `ghoti_runtime_core`, a pure
data-structure crate that defines the canonical types for future runtime
components: policy decisions, kill-switch state, agent roles, and runtime events.

No long-running service, file watcher, scheduler, IPC, network, or process
launcher is added. The workspace structure makes Rust a first-class part of
the project rather than a one-off checker.

---

## Dependency State

| Branch | Status |
|--------|--------|
| N+6.27B swarm_launcher | merged |
| N+6.28B Rust policy checker | merged |
| N+6.29B computer_use_adapter | merged - files untouched by N+6.31A |
| N+6.30B plug-and-play intake | merged - planning-only files untouched by N+6.31A |

---

## Files Added

| File | Purpose |
|------|---------|
| `rust/Cargo.toml` | Workspace root; members: policy_checker + runtime_core |
| `rust/ghoti_runtime_core/Cargo.toml` | Runtime core crate manifest |
| `rust/ghoti_runtime_core/src/lib.rs` | Crate root + 7 integration tests |
| `rust/ghoti_runtime_core/src/policy.rs` | PolicyDecision, KillSwitchStatus, RuntimeCapability |
| `rust/ghoti_runtime_core/src/events.rs` | RuntimeEvent, AgentRole, EventKind |
| `docs/GHOTI_N6_31A_RUST_RUNTIME_BASE.md` | Main milestone doc |
| `01_projects/runtime_mvp/tests/test_n6_31a_rust_runtime_base.py` | Structural tests |
| `14_context/claude_n6_31a_rust_runtime_base.md` | This file |

## Files Unchanged

| File | Note |
|------|------|
| `rust/ghoti_policy_checker/Cargo.toml` | Untouched; still builds |
| `rust/ghoti_policy_checker/src/main.rs` | Untouched; 4 tests still pass |

---

## Test Results

| Suite | Count | Result |
|-------|-------|--------|
| `cargo test --manifest-path rust/Cargo.toml` | 19 tests (4 + 15) | pass |
| `python -m unittest test_n6_31a_*` | structural tests | pass |

---

## Key Types Added

### policy.rs
- `PolicyVerdict` - Allow / Deny
- `PolicyDecision` - verdict + reasons + capability lists
- `KillSwitchState` - Inactive / Armed / Triggered
- `KillSwitchStatus` - state + optional reason; Default = Inactive
- `RuntimeCapability` - all known capabilities with `is_blocked()` predicate

### events.rs
- `AgentRole` - Builder / Auditor / Planner / Explorer / Observer
- `EventKind` - 11 variants (PlanSubmitted..ApprovalDenied)
- `RuntimeEvent` - structured event; `dry_run: true, live: false` always

---

## Safety Invariants

- No `unsafe` blocks in any `ghoti_runtime_core` source
- No network dependencies
- No process-spawning code
- No file I/O in the library crate
- `live: false` is the only constructable value until an approved milestone
- Blocked capabilities: Browser, ComputerUse, Mcp, Account, Money, MassMessage,
  Secrets, LiveLaunch, Docker, AutoSubmit, ExternalNav

---

## Immediate Next Steps

1. Codex audit: `audit/ghoti-agent-codex-n6-31a-rust-runtime-base`
2. Post N+6.29B merge: wire Rust bridge using `PolicyDecision` from `ghoti_runtime_core`
3. Future milestones: file_watcher, scheduler, kill_switch, trace_collector crates
