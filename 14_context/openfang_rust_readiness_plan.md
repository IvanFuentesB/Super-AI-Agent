# OpenFang Rust Candidate Readiness Plan

**Status label:** `evaluation_plan / rust_candidate / not_runtime_wired`

---

## Source Truth

- **Exact repo:** `exact_repo_unknown / needs_search`
- The name "OpenFang" appears in tool-intake research as a Rust-based agent/operator stack candidate, but the canonical repository URL has not been verified in this session.
- Do not clone until exact repo is confirmed and operator explicitly approves.

---

## Why It May Matter

OpenFang is a Rust-based codebase that may represent an agent OS or operator stack candidate. Rust is relevant to Ghoti because:

- Memory-safe systems-level language suitable for low-level operator or supervisor loops.
- Potential for high-performance, low-overhead background agents or capture daemons.
- Rust binaries can ship as standalone executables without a Python/Node runtime dependency.

If OpenFang is a real, maintained, open-source operator stack in Rust, it could inform or augment the Ghoti CapabilityAdapter layer — particularly for desktop-level control, screen-state ingestion, or supervisor daemon patterns.

---

## Rust Toolchain Status

| Tool | Version | Available |
|------|---------|-----------|
| `rustc` | not found | NO |
| `cargo` | not found | NO |

Rust is **not installed** on this machine. Both `rustc` and `cargo` return command-not-found in the current shell and PowerShell sessions.

**Do not install Rust** unless the operator explicitly approves it in the current session.

---

## Future Safe Evaluation Steps

1. **Identify exact repo** — search GitHub/crates.io for "OpenFang" or related Rust agent-stack projects. Confirm license (MIT/Apache-2.0 preferred), active maintenance, and purpose.
2. **License check** — confirm the license is compatible with Ghoti's private-repo usage model.
3. **Dependency audit** — review `Cargo.toml` and `Cargo.lock` for external network calls, telemetry, or unsafe dependencies.
4. **Build script review** — read `build.rs` and any install scripts before running. No `cargo build` without review.
5. **Read-only evaluation** — use `cargo metadata --no-deps` (read-only) to inspect the dependency tree without building.
6. **Rust install gate** — operator must explicitly approve `rustup` installation before any build step.
7. **Isolated clone** — clone into `21_repos/third_party/openfang/` only after exact repo and license are confirmed and operator approves. Do not clone elsewhere.
8. **No runtime wiring** — OpenFang remains reference/evaluation only until a specific integration path is defined and approved.

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Unknown repo / wrong project | Confirm exact URL before any clone |
| Build scripts with network calls | Read `build.rs` before running `cargo build` |
| Rust install side effects | Operator approval required; use `rustup` official installer only |
| Wiring into runtime too early | Blocked by this plan — evaluation only until explicit approval |

---

## Wait/Resume Gate

A new wait item should be added to `runtime_data/wait_resume_items.json`:
- Title: `OpenFang exact repo identification and Rust install approval`
- Wait type: `user_approval`
- Risk level: `medium`
- Resume command: `(manual — identify repo URL, confirm license, then request operator approval for rustup install and isolated clone)`

---

## Verdict

**Research/evaluation only.** Not runtime-wired. Blocked on: exact repo identification + Rust toolchain install approval + license review.
