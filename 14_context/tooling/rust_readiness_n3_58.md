# Rust Readiness Probe — N+3.58A

Generated: 20260506T211637Z

## Current Rust Toolchain Status

| Tool   | Status | Version |
|--------|--------|---------|
| rustc  | NOT FOUND | N/A |
| cargo  | NOT FOUND | N/A |
| rustup | NOT FOUND | N/A |

Fully installed: NO

## Tracked Rust Code in Ghoti

Tracked .rs files: **NONE**
Tracked Cargo manifest files: NONE

## Recommendation

**Do not rewrite Python/Node MVP into Rust yet.**
**Introduce Rust later for stable runtime core only.**

## What Rust Is Good For in Ghoti (Future Use)

- approval gate engine — fast, safe, auditable decision logic
- durable job runner — reliable task execution with crash recovery
- safe plugin/tool sandbox boundary — memory-safe isolation for tool calls
- file watcher/event loop — efficient OS-level event monitoring
- future desktop/operator daemon — lightweight background service

## What NOT To Do

- do not rewrite ghoti_dashboard.py in Rust
- do not rewrite Python operators in Rust yet
- do not add unused Rust crate just to affect GitHub language stats
- do not introduce Rust before the Python MVP is stable

## Optional Future Install (Documentation Only — Do Not Execute Without Operator Approval)

```powershell
winget install Rustlang.Rustup
rustup default stable
rustc --version
cargo --version
```

## Current Runtime Stack (Truthful)

- Python — primary orchestration and scripts
- Node.js / JavaScript — dashboard MVP
- PowerShell — Windows operator scripts
- Rust — NOT present; future stable-core option only
