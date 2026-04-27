# CUA Sandbox Profile Plan

Status label: `sandbox_profile_plan / example_only / not_runtime_wired`
Date: 2026-04-27
Branch: `feat/ghoti-visible-operator-stack`
Milestone: N+3.4

---

## Purpose

The sandbox profile (`23_configs/cua_sandbox_profile.example.json`) defines the safety envelope for any future CUA (Computer-Use Agent) integration in Ghoti. It is an example profile only — no CUA runtime is installed or wired.

The profile exists so that:
1. The operator can review the exact safety constraints before any CUA approval is requested.
2. The runtime can validate any future CUA action against a known, approved profile.
3. No accidental expansion of permissions occurs when CUA evaluation begins.

---

## Profile Fields

| Field | Value | Meaning |
|-------|-------|---------|
| `status_label` | `example_profile / sandbox_only / not_runtime_wired` | This profile is not active |
| `enabled` | `false` | CUA is disabled; this profile cannot trigger any action |
| `mode` | `sandbox_only` | Only isolated/sandboxed targets are allowed |
| `require_action_intent` | `true` | Every CUA action must have a pre-approved ActionIntent |
| `require_human_approval_per_action` | `true` | Operator approves each action individually |
| `require_payload_hash_match` | `true` | Approved payload hash must match consumed intent |
| `allow_screenshots` | `true` | Observe-only screenshot is the first safe step |
| `allow_click` | `false` | Clicks disabled until separate approval |
| `allow_type` | `false` | Typing disabled until separate approval |
| `allow_shell` | `false` | Shell execution disabled; never enabled in sandbox |
| `allow_file_upload` | `false` | File upload disabled |
| `allow_live_accounts` | `false` | Live accounts forbidden in sandbox mode |
| `retention_days` | `3` | Screenshot/log retention capped at 3 days |
| `allowed_windows` | `["example.com test page", "local dashboard"]` | Only these windows are valid targets |
| `forbidden_targets` | banking, password manager, 2FA, email, social, trading, payments | Hard-blocked targets |
| `audit_log` | `05_logs/cua_action_audit.jsonl` | Per-action audit trail path |

---

## First Test Scope

The first CUA sandbox test must be observe-only:
- Target: a local test page (e.g., `http://localhost:3210` dashboard or `https://example.com`)
- Action: screenshot only (`allow_screenshots: true`)
- Click: disabled (`allow_click: false`)
- Type: disabled (`allow_type: false`)
- No live account, no credential, no browser session with real data

This observe-only test establishes that the CUA driver can:
1. Connect to the sandbox target
2. Capture a screenshot
3. Write an audit entry to `05_logs/cua_action_audit.jsonl`

Without producing any side effects on the host desktop or real services.

---

## Expanding Permissions

Each capability expansion (click, type, broader windows) requires:
1. A new explicit operator approval in the session
2. An updated profile or new profile file (do not silently mutate the example)
3. An ActionIntent with `adapter_id=cua-driver-reference`, `risk_level=high`, and a human-approved payload

---

## What This Profile Does NOT Allow

- Autonomy: no action executes without human approval per action
- Live accounts: no banking, email, social, trading, payment, or 2FA screens
- Credential entry: typing is disabled in sandbox mode
- Stealth: no anti-detection or anti-bot bypass
- Background operation: every step is operator-initiated
- Permanent storage: retention capped at 3 days; old screenshots auto-deleted

---

## Relation to ActionIntent Contract

Any CUA action flowing through Ghoti must:
1. Be created as an `ActionIntent` with `adapter_id=cua-driver-reference`
2. Pass the `classify_action` check in `action_intent.py` (no forbidden types)
3. Receive explicit approval in the approval inbox before execution
4. Have its payload hash verified at consumption time
5. Write an audit entry to `05_logs/cua_action_audit.jsonl`

No CUA action can bypass this chain.
