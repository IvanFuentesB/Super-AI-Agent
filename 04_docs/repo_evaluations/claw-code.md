# Claw Code Evaluation

Last updated: 2026-04-05

Repo:

- Local: `C:\Users\ai_sandbox\AI_Workspace\21_repos\core\claw-code`
- Remote: `https://github.com/ultraworkers/claw-code.git`

Location note:

- `AI_Managed_Only` is the permanent workspace root.
- This Claw Code checkout is temporary and remains outside that root until explicitly approved for relocation or re-clone.

## Short verdict

Claw Code is worth studying, but not worth centering this sandbox around yet.

## What the repo claims

- The active Rust workspace lives in `rust/`.
- The repo is a claw-native coding harness.
- The same README also says the main source tree is Python-first.

## What the local tree shows

- top-level dirs: `.claude`, `.github`, `assets`, `rust`, `src`, `tests`
- Rust workspace:
  - 9 crates
  - `Cargo.toml`
  - `USAGE.md`
  - parity harness docs and scripts
- Python workspace:
  - large `src/` tree
  - only one top-level Python test file
- CI:
  - `.github/workflows/rust-ci.yml`
  - no visible Python CI at repo root

## Evidence that Rust is currently more active

- latest local commit touched `rust/crates/runtime/src/file_ops.rs`
- `USAGE.md` is centered on building and running the Rust `claw` binary
- `rust/README.md` is a more concrete product surface than the Python README sections
- the only visible CI workflow is Rust-focused

## Evidence that the docs are internally inconsistent

- top README says active Rust workspace now lives in `rust/`
- later README sections describe the repo as Python-first
- top-level `PARITY.md` and `rust/PARITY.md` do not tell exactly the same story

## Practical interpretation

This repo is mixed, but the current working center looks Rust-first, with Python still present as a parallel or legacy porting surface.

That matters because:

- it is not a clean foundation repo yet
- the docs require manual interpretation
- it is still useful as a design reference for harness ideas

## Useful ideas to borrow later

- structured permissions
- machine-readable status and parity thinking
- task/team/cron registries
- MCP lifecycle hardening
- event and recovery concepts

## What not to do

- do not assume the README headline tells the full truth
- do not treat star count as validation
- do not build your assistant plan around this repo before the baseline sandbox is stable

## Recommendation

- Use as reference: yes
- Use as first foundation: no
- Re-evaluate later after Python, GitHub, local model runtime, and workspace hygiene are in place
