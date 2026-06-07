# Ghoti N+6.28A Rust Policy Checker

## Purpose

N+6.28A introduces Ghoti's first concrete Rust runtime-safety component: a
small, deterministic policy checker for proposed swarm-plan JSON. It is a
dry-run prototype. It does not launch agents, execute commands, use the
network, or modify files.

N+6.27A is not merged, so this milestone deliberately does not edit or create
the Python swarm launcher. A future audited milestone may connect this binary
to the Python launcher as a required preflight gate.

## Policy

The checker is default-deny. A plan is allowed only when all of these are true:

- `dry_run` is `true`.
- `live_launch` is `false`.
- `requires_human_approval` is `true`.
- Every requested capability is on the narrow local read/render allowlist.

The checker denies browser or computer use, MCP, account operations, money
operations, mass messaging, secrets handling, unknown capabilities, and any
request for live launch.

## Commands

```powershell
cargo test --manifest-path rust/ghoti_policy_checker/Cargo.toml
cargo run --manifest-path rust/ghoti_policy_checker/Cargo.toml -- --check
cargo run --manifest-path rust/ghoti_policy_checker/Cargo.toml -- --input <plan.json>
```

All decisions are emitted as JSON. An `allow` result means only that the
submitted plan fits this prototype's dry-run policy. It is not permission to
launch anything.

## Future Integration

The next integration step is an audited Python launcher preflight that invokes
the checker before rendering a controlled swarm plan. Live execution remains
disabled until a later human-approved milestone adds and audits a separate
execution surface.
