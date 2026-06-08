# TryCUA / CUA + UI-TARS — Computer-Use Trial Plan (N+6.30A)

**Milestone:** N+6.30A
**Status:** plan only — no live computer-use, no Docker, no OS input
**Builds on:** N+6.12A static inspection, N+5.0A observation adapter,
N+6.13A sandbox harness, N+6.14A confined browser runner, N+6.29A adapter contract

## Current Computer-Use Stack in Ghoti

| Milestone | What it delivers | Status |
|-----------|-----------------|--------|
| N+5.0A | UI-TARS observation-only adapter | merged |
| N+6.12A | TryCUA/CUA static inspection; pattern extraction | merged |
| N+6.13A | Sandbox action planner + dry-run runner | merged |
| N+6.14A | Confined browser sandbox (real DOM, file:// only) | merged |
| N+6.29A | Repo-backed adapter contract; URL guard; Arena payload | merged (N+6.29B); remains dry-run |

**N+6.29B is merged. Any further computer-use milestone that changes
`03_scripts/computer_use_adapter/` or `14_context/computer_use_adapter/` still requires a separate audit.**

---

## TryCUA / CUA Driver

### What it is (from N+6.12A static inspection)
- **Source:** `https://github.com/trycua/cua` (MIT, commit `4c54f43`)
- **What:** live desktop control platform via Docker/QEMU/KASM sandboxes.
- **Scale:** 2185 files scanned; 189 shell scripts; Docker/QEMU runtime required.
- **Key pattern adapted:** action-intent payload with declared type, target, value;
  sandbox isolation boundary; capability declaration; approval gate; dry-run status payload.

### What is NOT used from TryCUA (hard rules)
- No Docker / QEMU / KASM runtime.
- No real OS input (click, type, key_press).
- No 189 shell scripts.
- No remote desktop protocols.

### Path to eventual real use in Ghoti
The N+6.29A adapter contract is the abstraction layer between Ghoti and TryCUA. The
planned progression (each requires an explicit audited milestone):

```
N+6.29A  → dry-run adapter contract (current)
Future audited lane → wire Rust policy checker bridge
N+6.31A  → confined Docker sandbox gate (Docker milestone, human-approved)
N+6.32A  → real CUA action in approved Docker sandbox (approval token required)
```

**None of these steps happen automatically.** Each requires Codex audit and human approval.

### Risk Matrix

| Risk | Current Gate | Future Gate |
|------|-------------|-------------|
| Real OS click/type | blocked in N+6.29A adapter | Docker sandbox perimeter |
| External URL navigation | blocked in N+6.29A URL guard | Domain allowlist |
| Account login | blocked in N+6.29A capability check | Never (out of scope) |
| Secrets/tokens | blocked in N+6.29A secret scanner | Vault, never in plan |
| Docker arbitrary command | not used | Approved image digest gate |
| Shell command execution | blocked in adapter | Allowlist per milestone |

---

## UI-TARS

### Current Status: source_needed

Multiple distinct upstream projects use the "UI-TARS" name:
- A vision-language model for GUI grounding (bytedance/UI-TARS)
- A desktop automation application
- Various SDKs and wrappers

**Rule:** do not clone or install from a guessed URL. The operator confirms the
exact upstream before any static inspection.

### What patterns are already in Ghoti (from N+5.0A and N+6.29A)
1. **Observation-only mode** — adapter can inspect/read state without performing real OS actions.
2. **Typed action contract** — each action is a typed record (click/type/read) with explicit fields.
3. **Blocked-action manifest** — canonical list of refused action types in every result.
4. **Arena status block** — `simulation: true` / `live_execution: false` for visualization.

These patterns were re-expressed from scratch in Ghoti-native code with attribution.
No UI-TARS code has been copied.

### Once the exact source is confirmed by the operator
1. Static clone into `21_repos/third_party_runtime_sandbox/ui_tars` (gitignored).
2. Read LICENSE (Apache-2.0 reported, verify).
3. Read README and architecture docs.
4. Identify: model size/requirements, runtime dependencies, OS API surface.
5. Record: minimum hardware, GPU requirement, inference latency.
6. Plan: whether a local-only vision model can replace or can be a future N+6.35+ milestone.
7. **Do not** download model weights, run inference, or launch desktop control.

### Model/Runtime Requirements (reported, unverified)
- Large vision-language model (reportedly 7B+ parameters).
- GPU recommended; Apple Silicon or CUDA.
- Real-time screenshot capture and action execution via OS accessibility APIs.
- These requirements make it a later milestone (post Docker sandbox gate, post N+6.32A).

---

## Computer-Use Safety Invariants (permanent)

These hold across all current and future computer-use milestones:

1. `real_action_performed` is always `false` until a dedicated real-action milestone.
2. `target_url` must pass `urlparse` hostname check (not `startswith`).
3. `ALLOWED_LOCAL_HOSTNAMES = {"localhost", "127.0.0.1", "::1"}` — no deceptive hostnames.
4. `auto_submit` must always be `false`.
5. `requires_human_approval` must always be `true`.
6. No secrets, tokens, cookies, or auth files in any action plan.
7. No Docker until a Docker milestone with approved image digest.
8. No external website navigation.
9. Rust policy checker bridge wired post N+6.28B merge (next milestone).
10. Every result includes `refused_live_actions` canonical list.

---

## Next Steps After This Intake

1. **Keep N+6.29B dry-run guarantees intact.**
2. **Wire Rust bridge in a separate audited lane** — extend `ghoti_computer_use_adapter.py --plan` to pipe
   validated plans to `cargo run --manifest-path rust/ghoti_policy_checker/Cargo.toml`.
3. **Extend adapter_result_schema** — add `rust_policy_result` block.
4. **Add regression test** for bridge handshake.
5. **Update `rust_policy_bridge_ready: true`** once wired and tested.
