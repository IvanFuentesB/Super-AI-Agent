# GHOTI N+6.34A — CUA Isolated Dry-Run / Observation Adapter

## Overview

N+6.34A is the first real plug-and-play repo trial. It moves beyond plans and
static notes: TryCUA/CUA is cloned, its metadata is read from the live clone, a
dry-run observation plan is generated and validated through the N+6.33A dual gate,
and the results are recorded.

**What is real:** the CUA sandbox is present, the license is verified, the runtime
requirements are inspected, and a safe trial plan is accepted by both the Python
adapter and the Rust policy checker.

**What is NOT live:** CUA code is never imported or executed. No OS input. No Docker
/ VM. No MCP. No browser. No account. No telemetry triggered.

**Builds on:** N+6.33A (Rust policy bridge), N+6.29B (adapter), N+6.28B (policy checker).

---

## What is real in this milestone

| Item | Status |
|------|--------|
| TryCUA/CUA cloned into gitignored sandbox | Real — commit `2925b491`, depth=1, no hooks |
| LICENSE.md verified MIT | Real — "MIT License / Copyright (c) 2025 Cua AI, Inc." |
| Package metadata read from pyproject.toml | Real — `cua-workspace`, runtime requirements inspected |
| Shell-script count | Real — 175 `.sh` files in sandbox (risk surface metric) |
| Dry-run observation plan generated | Real — 4 read-only actions, no blocked capabilities |
| Dual gate (adapter + Rust policy) | Real — both gates allow the observation plan |
| Audit traceability (commit hash recorded) | Real — reported in `cua_sandbox_detection` |

---

## What is NOT live

- **No CUA code imported or executed.** `cua-computer` requires `websocket-client`,
  `aiohttp`, and live OS connections. `cua-core` fires PostHog telemetry on import.
  Neither is touched.
- **No Docker / QEMU / Lume / KASM VM** — the CUA sandbox requires these for any
  real desktop control. None are launched.
- **No MCP server** activation.
- **No real OS click / type / hotkey / mouse move.**
- **No live browser control.**
- **No account login or session management.**
- **No secrets / tokens / cookies.**
- **No auto-submit.**
- **No shell scripts run** inside the CUA sandbox.
- The sandbox is read-only from the adapter's perspective.

---

## Why CUA is first

The N+6.29A computer-use adapter contract was designed with CUA patterns in mind
(action-intent payload, sandbox isolation, capability declaration, approval gate,
dry-run status payload). CUA is the most direct match for the computer-use domain.

Its isolation boundary (Docker/Lume VM) is also the clearest: once an actual VM
trial is authorized, the hard boundary between guest and host is well-defined. This
makes it safer to enable than browser-automation tools with weaker isolation.

---

## How the other repos relate

| Repo | Role | Current status |
|------|------|---------------|
| TryCUA/CUA | First engine trial | Sandbox cloned; metadata only in N+6.34A |
| UI-TARS (bytedance) | Observation-only mode patterns | Static inspection (N+5.0A, N+6.12A) |
| Browser Harness | Local fixture / CDP isolation patterns | Static inspection (N+6.12A) |
| Vercel agent-browser | Capability gate / approval gate patterns | Static inspection (N+6.12A) |
| Ruflo | Coordinator/worker + declared-skill pattern | Static inspection; trial planned post-CUA |

---

## Adapter design

`03_scripts/cua_trial/ghoti_cua_trial_adapter.py` has three gates:

1. **Gate 0 — CUA trial pre-filter:** denies any plan that claims
   `computer_use`, `docker`, `lume`, `qemu`, `kasm`, `mcp`, `vm_launch`,
   `shell_execution`, `telemetry_upload`, or other live capabilities before it
   even reaches the N+6.29A adapter.
2. **Gate 1 — N+6.29A Python adapter:** target / URL / action-type / secret /
   capability checks.
3. **Gate 2 — N+6.33A Rust policy checker** (mirror): `ghoti_policy_checker`
   decision. Unknown capabilities are denied (default-deny holds).

`accepted = Gate 1 allowed AND Gate 2 allowed`. Gate 0 short-circuits to denied
before reaching the bridge.

The adapter has two modes:
- `--check` — system readiness; no CUA required.
- `--trial` — sandbox detection → metadata read → plan generation → dual-gate
  validation.

---

## Files

| File | Change |
|------|--------|
| `03_scripts/cua_trial/ghoti_cua_trial_adapter.py` | New — CUA trial adapter |
| `03_scripts/cua_trial/check_cua_trial.ps1` | New — PowerShell system check |
| `14_context/cua_trial/cua_trial_status_schema.json` | New — status output schema |
| `14_context/cua_trial/README.md` | New — context folder docs |
| `docs/GHOTI_N6_34A_CUA_REAL_REPO_TRIAL.md` | This document |
| `01_projects/runtime_mvp/tests/test_n6_34a_cua_real_repo_trial.py` | New — 44 tests |
| `14_context/claude_n6_34a_cua_real_repo_trial.md` | New — context snapshot |

No third-party code committed. CUA sandbox is in `21_repos/third_party_runtime_sandbox/cua`
(gitignored, `.gitignore:149`).

---

## Tests (44)

| Class | What it proves |
|-------|---------------|
| `TestSandboxIsolation` | Sandbox gitignored; no CUA code tracked; adapter source clean |
| `TestLiveActionRefusal` | docker/computer_use/mcp/vm_launch/real_click/telemetry/shell denied |
| `TestRustPolicyGate` | browser/account/money/secrets denied via policy gate |
| `TestExternalUrlBlocking` | external HTTPS/file-authority/account-login/navigate_url denied |
| `TestTrialPlanProduction` | plan structure; local-sandbox target; dual-gate accept; dry-run |
| `TestDockerVmMcpDenial` | docker/lume/qemu/kasm/mcp all denied |
| `TestMetadataSmoke` | commit hash; MIT license; package name; shell count; never imports CUA |
| `TestCheckMode` | check works without sandbox; all live flags false |
| `TestAdapterContract` | milestone constant; sandbox path; refused actions; blocked caps |

---

## Validation

```
$env:CARGO_TARGET_DIR = "$env:TEMP\ghoti_rust_target"
cargo test --manifest-path rust/Cargo.toml
cargo run --manifest-path rust/ghoti_policy_checker/Cargo.toml -- --check
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_34a_*.py" -v
python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_33a_*.py" -v
python 03_scripts/public_repo_security_audit.py --run --json
python 03_scripts/ghoti_product_launcher.py --status --json
git diff --check
git show --check --stat HEAD
```

---

## Next step after this

An actual CUA sandbox execution trial — a **future audited milestone** that
requires:
- Isolated OS profile / VM (no Ghoti repo access, no real accounts, no secrets).
- Human approval.
- The N+6.34A dual gate (and its Gate 0 pre-filter) green.
- Only a scratch repo with junk data.
- Docker/Lume isolation reviewed and scoped.

---

## Codex Audit Target

`audit/ghoti-agent-codex-n6-34a-cua-real-repo-trial`
