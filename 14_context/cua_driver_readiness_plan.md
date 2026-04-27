# CUA Driver / TryCUA Readiness Plan

**Status label:** `evaluation_plan / sandbox_first / not_runtime_wired`

---

## What CUA/TryCUA Is for Ghoti

CUA Driver (TryCUA) is a computer-use automation framework capable of driving UI interactions on a live desktop or inside a sandboxed/VM environment. For Ghoti it represents the next practical leap toward a real operator that can observe screen state and take precise actions — clicks, keystrokes, form fills — on behalf of an explicitly approved task.

It is the highest-priority external integration candidate for computer-use autonomy, but it is **not runtime-wired in this milestone**.

---

## Why It Matters

- Can eventually run UI actions (open app, fill form, read screen, click button) through a controlled, auditable driver.
- Removes the current limitation of desktop-bridge primitives that depend on hardcoded window titles and allowlists.
- Unlocks real multi-step operator recipes that adapt to screen state instead of assuming a fixed layout.

---

## Target Architecture

```
ChatGPT (architecture / task definition)
  └─► Claude / Codex (implementation, narrow prompt)
        └─► Ghoti ActionIntent (payload + approval gate)
              └─► CUA CapabilityAdapter (adapter descriptor)
                    └─► CUA Driver runtime (sandboxed)
                          └─► Audit JSONL + screenshot trace
                                └─► Dashboard status route
```

Every step after ActionIntent creation requires explicit operator approval before execution.

---

## First Safe Test Requirements

- Sandbox or controlled VM only — no live production desktop.
- No live accounts, no banking, no email, no social.
- No password entry, no 2FA screens.
- No background autonomy — one action at a time, operator-initiated.
- Screenshot allowed only in the test window/VM.
- Every action bound to an ActionIntent payload with `adapter=cua_driver`.
- ActionIntent must be approved before any CUA step executes.
- Audit JSONL entry written for every attempted action (approved or blocked).

---

## Required Future Files (not created yet)

| File | Purpose |
|------|---------|
| `23_configs/cua_driver_capability.json` | CapabilityAdapterDescriptor for CUA |
| `23_configs/cua_sandbox_profile.json` | Sandbox target config (VM path, resolution, allowed apps) |
| `23_configs/cua_window_allowlist.json` | Allowlisted app/window targets for CUA actions |
| `23_configs/cua_screenshot_retention.json` | Retention policy for CUA screenshots |
| `05_logs/cua_audit.jsonl` | Per-action audit trace (created at first run) |
| `01_projects/runtime_mvp/src/super_ai_agent/cua_adapter.py` | CapabilityAdapter implementation |

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Full desktop control | Sandbox/VM isolation; no live account targets in Phase 1 |
| Accidental live account action | Window allowlist enforced; no auto-submit without approval |
| Screenshot privacy | Screenshots retained only in local `output/screenpipe` or designated CUA log dir; 3-day retention |
| Credential capture | Blocked at ActionIntent level — password/2FA window targets forbidden |
| Provider/TOS boundaries | No cloud-based CUA services; local-only driver; no evasion of limits |
| Unintended broad automation | `approval_required=True`, `risk_level=high` on all CUA intents |

---

## Wait/Resume Gate

- Wait title: `TryCUA/CUA Driver evaluation — sandbox only, no live desktop`
- Status: `pending` (existing gate in `runtime_data/wait_resume_items.json`)
- Resume requires: operator approval + sandbox VM available + allowlist defined.

---

## Verdict

**TOP PRIORITY** for real computer-use capability. Not runtime-wired until:
1. Exact TryCUA repo identified and license reviewed.
2. Sandbox profile defined and approved by operator.
3. ActionIntent + CapabilityAdapter descriptor created.
4. At least one dry-run in isolated VM with audit trace.
5. Operator explicitly approves wiring into Ghoti runtime.
