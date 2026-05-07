# Ghoti N+3.58A — Language Truth, Rust Readiness, Merge Assistant

## Summary

N+3.58A is a hardening milestone that closes the language-truth / Rust-readiness / merge-readiness gap.
It does not pretend Java or Rust are present when they are not.

## What This Milestone Adds

| Deliverable | File | Purpose |
|-------------|------|---------|
| Repo language inventory | `03_scripts/repo_language_inventory.py` | Truthfully inspect tracked language files; explain GitHub discrepancy |
| Rust readiness probe | `03_scripts/rust_readiness_probe.py` | Check if Rust tools exist; produce readiness plan |
| Merge assistant | `03_scripts/ghoti_merge_assistant.py` | Generate safe merge commands; dry-run-first |
| Dashboard language truth | `03_scripts/ghoti_dashboard.py` | Added `language_truth` section to status/JSON/card |
| Router new routes | `03_scripts/local_worker_router.py` | Three new routes: language inventory, Rust readiness, merge assistant |
| Configs | `23_configs/` | Example configs for all three new scripts + updated routing config |
| Docs | `14_context/tooling/` | Four new tooling doc files |

## Language Truth

- **Tracked Java: NONE** — `git ls-files | grep .java` returns nothing.
- **Tracked Rust: NONE** — `git ls-files | grep .rs` returns nothing. No Cargo.toml tracked.
- GitHub may show Java due to: untracked files in `21_repos/third_party/`, generated output, workspace files, or stale language cache.
- `git ls-files` is the authoritative source of truth for tracked file languages.

## Rust Truth

- Rust is NOT in the Ghoti runtime.
- Rust toolchain (rustc/cargo/rustup) may or may not be installed locally — this is operator-specific.
- Do not rewrite Python/Node MVP into Rust now.
- Introduce Rust later for stable core components only (approval gate engine, durable job runner, plugin sandbox, file watcher, desktop daemon).
- Do not add unused Rust to affect GitHub language stats.

## Current Runtime Stack (Truthful)

- **Python** — primary scripts, orchestration, CLI
- **Node.js / JavaScript** — dashboard MVP server and frontend
- **PowerShell** — Windows operator scripts
- **Rust** — NOT present; future stable-core option only
- **Java** — NOT present; not planned

## Project Completion Bands

| State | Estimated Band |
|-------|---------------|
| main before N+3.58 merge | ~74–76% |
| N+3.51/N+3.56 branch after clean Codex audit | ~90–94% |
| After N+3.58 language truth + merge assistant | ~92–95% |
| 100% requires | Actual end-to-end supervised workflows, not just scaffolding |

## Safety Constraints (Preserved)

- No live actions. No Ruflo runtime wiring. No automatic CC/Codex control.
- No CC/Codex automatic. Bridge remains local/manual file handoff.
- No secrets, credentials, .env, tokens, API keys touched.
- No global package installs.
- Merge assistant generates commands only — operator executes manually.
- Do not merge if Codex says BLOCKED.

## Next Codex Recommendation

Run Codex audit on this branch (`feat/ghoti-agent-claude-n3-58-language-truth-rust-readiness-merge-assistant`).
Expected result: PASS (language truth is explicit, no fake Rust/Java, merge assistant is safe commands-only).
After PASS: operator may merge N+3.56-FIX + N+3.58 into main via the merge assistant plan.
