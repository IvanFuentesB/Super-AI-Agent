# GHOTI N+6.31A — Rust Runtime Base Scaffold

## Overview

N+6.31A creates the Rust workspace base for future Ghoti runtime components.
It does not implement any long-running service, file watcher, scheduler, IPC,
network, or process launcher. It establishes the workspace structure and the
canonical data types that all future Rust runtime crates will share.

**Base main:** `ca90fbd` (N+6.28B Rust policy checker merged)
**Branch:** `feat/ghoti-agent-claude-n6-31a-rust-runtime-base`

## Dependency State

| Branch | Status |
|--------|--------|
| N+6.27B swarm_launcher | merged |
| N+6.28B Rust policy checker | merged |
| N+6.29B computer_use_adapter | merged — those files untouched by N+6.31A |
| N+6.30B plug-and-play intake | merged — planning-only files untouched by N+6.31A |

---

## 1. Workspace Structure

```
rust/
  Cargo.toml                     <- workspace root (NEW)
  ghoti_policy_checker/          <- existing (N+6.28B, unchanged)
    Cargo.toml
    src/main.rs
  ghoti_runtime_core/            <- NEW
    Cargo.toml
    src/
      lib.rs
      policy.rs
      events.rs
```

The workspace uses `resolver = "2"` and `edition = "2024"`. Each crate keeps
its own `Cargo.toml`; the workspace root is additive only.

---

## 2. ghoti_runtime_core — Data Structures

### policy.rs

| Type | Purpose |
|------|---------|
| `PolicyVerdict` | `Allow` or `Deny` — result of a policy check |
| `PolicyDecision` | Full result: verdict + reasons + blocked/unknown capabilities |
| `KillSwitchState` | `Inactive`, `Armed`, `Triggered` |
| `KillSwitchStatus` | Kill switch state + optional reason string |
| `RuntimeCapability` | Enum of every capability the runtime recognises |

`RuntimeCapability::is_blocked()` returns `true` for: Browser, ComputerUse, Mcp,
Account, Money, MassMessage, Secrets, LiveLaunch, Docker, AutoSubmit, ExternalNav.

### events.rs

| Type | Purpose |
|------|---------|
| `AgentRole` | Builder, Auditor, Planner, Explorer, Observer |
| `EventKind` | 11 event kinds (PlanSubmitted through ApprovalDenied) |
| `RuntimeEvent` | Structured event with kind, plan_id, role, wave, message, dry_run, live |

`RuntimeEvent::dry()` constructs an event with `dry_run: true, live: false` — the
only constructor available until a live execution milestone is approved.

---

## 3. Invariants

- No `unsafe` blocks anywhere in `ghoti_runtime_core`.
- No network calls (`std::net`, `tokio`, `reqwest`, etc. are not dependencies).
- No process spawning (`std::process::Command` not used in lib).
- No file I/O in the library crate (only in `ghoti_policy_checker/src/main.rs`).
- `live: false` is the only value constructable via the public API until a future
  milestone explicitly adds a live-execution path with an approval gate.
- All serialization uses `serde` with `rename_all = "snake_case"` for JSON interop.

---

## 4. Test Coverage

| Crate | Tests | Status |
|-------|-------|--------|
| `ghoti_policy_checker` | 4 | pass |
| `ghoti_runtime_core` | 15 (8 unit + 7 integration in lib.rs) | pass |
| **Total** | **19** | **pass** |

---

## 5. What Remains Disabled

Same as N+6.28B and N+6.30A — no new surfaces opened:

| Surface | Gate Required |
|---------|-------------|
| Live agent launching | Kill-switch + approval token milestone |
| File watcher | Dedicated milestone |
| Scheduler | Dedicated milestone |
| IPC | Dedicated milestone |
| Network (any) | Dedicated milestone with review |
| Process launching | Dedicated milestone |
| Rust bridge to computer_use_adapter | Future audited integration lane |

---

## 6. Next Integration Steps

1. **Future audited integration lane:** wire `ghoti_policy_checker` output into
   `ghoti_computer_use_adapter.py` via the Rust bridge.
   Use `PolicyDecision` from `ghoti_runtime_core::policy` as the shared type
   definition for documentation and cross-language contract clarity.

2. **Future crates (each a dedicated milestone):**
   - `ghoti_file_watcher` — local file-change events feeding the runtime event bus
   - `ghoti_scheduler` — approval-gated task queue
   - `ghoti_kill_switch` — monitors `KillSwitchStatus`; halts agents on `Triggered`
   - `ghoti_trace_collector` — structured log collector for agent turn traces

3. **Agent Arena integration:** `RuntimeEvent` is the target wire format for arena
   status blocks once the launcher and adapter emit structured events.

---

## Files Added

| File | Purpose |
|------|---------|
| `rust/Cargo.toml` | Workspace root |
| `rust/ghoti_runtime_core/Cargo.toml` | Runtime core crate manifest |
| `rust/ghoti_runtime_core/src/lib.rs` | Crate root + integration tests |
| `rust/ghoti_runtime_core/src/policy.rs` | PolicyDecision, KillSwitchStatus, RuntimeCapability |
| `rust/ghoti_runtime_core/src/events.rs` | RuntimeEvent, AgentRole, EventKind |
| `docs/GHOTI_N6_31A_RUST_RUNTIME_BASE.md` | This document |
| `01_projects/runtime_mvp/tests/test_n6_31a_rust_runtime_base.py` | Structural tests |
| `14_context/claude_n6_31a_rust_runtime_base.md` | Context snapshot |

## Codex Audit Target

`audit/ghoti-agent-codex-n6-31a-rust-runtime-base`
