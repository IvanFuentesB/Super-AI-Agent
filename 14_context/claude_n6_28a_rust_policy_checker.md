# N+6.28A Rust Runtime Policy Checker Prototype

## Status

- Branch: `feat/ghoti-agent-claude-n6-28a-rust-policy-checker`
- Base: `origin/main` at `1bedd9ed14a23da9d7e489620844001af1ee8022`
- Implementation verdict: `READY_TO_PUSH`
- Dependency truth: N+6.27A is not merged, so no swarm-launcher files were edited.

## What Was Added

- A standalone Rust JSON policy checker under `rust/ghoti_policy_checker/`.
- Default-deny validation for proposed dry-run swarm plans.
- Denials for live launch, browser/computer-use, MCP, accounts, money,
  mass messaging, secrets, unknown capabilities, and plans that do not require
  human approval.
- Rust unit tests, Python integration tests, and operator documentation.

## Runtime Boundary

The checker reads one local JSON file or evaluates its built-in default-deny
check. It prints JSON only. It does not launch agents, execute commands, use
the network, write files, integrate with MCP, control a browser, access
accounts, or submit actions.

## Validation

Validation results are recorded after implementation:

- `rustc --version`: `rustc 1.95.0 (59807616e 2026-04-14)`
- `cargo --version`: `cargo 1.95.0 (f2d3ce0bd 2026-03-21)`
- `cargo test`: 4 passed, 0 failed
- `cargo run ... -- --check`: passed; built-in plan denied by default
- N+6.28A Python tests: 10 passed, 0 failed
- Public repository security audit: 150 checks, 0 failed, 8 baseline warnings
- Ghoti launcher status: passed; localhost-only and no external API/live account actions

Windows Controlled Folder Access refused Cargo's temporary build files under
`Documents`, so validation directed only `CARGO_TARGET_DIR` to the operating
system temp directory. Source, manifest, and lockfile remain repo-local; no
machine-specific path is committed.

## Next Step

Codex audit target:
`audit/ghoti-agent-codex-n6-28a-rust-policy-checker`
