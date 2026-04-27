# Codex CUA Driver / TryCUA Audit - N+3.3

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Observed HEAD: bd6a76f
Status label: parallel_audit_only / sandbox_first / not_runtime_wired

## Scope

This is a Codex parallel audit for CUA Driver / TryCUA readiness. It does not clone, install, start, or wire any computer-use runtime. It exists to define the safest next path toward real computer use.

## Why CUA Driver / TryCUA Is Top Priority

CUA Driver / TryCUA is the top-priority computer-use direction because it appears aligned with a structured computer-use driver model instead of ad hoc desktop scripting. That matters for Ghoti because the project already has ActionIntent and CapabilityAdapter-style contracts. A driver with explicit actions, screenshots, and adapter state can be wrapped by Ghoti's approval gates more cleanly than a broad "agent controls my desktop" loop.

The priority is not "use it now." The priority is "evaluate it first as the likely best long-term sandbox path."

Current truth:

- Not installed by this Codex lane.
- Not cloned by this Codex lane.
- Not runtime-wired into Ghoti.
- Exact repo/source/version still needs verification before implementation.
- Must be tested in a sandbox/VM first.

## Expected Architecture

Target future architecture:

```text
ChatGPT brain
  -> Ghoti planner
  -> ActionIntent
  -> approval gate
  -> CUA adapter
  -> audit trace
  -> dashboard status
```

Important: observations, screenshots, and model descriptions must never authorize actions by themselves. Only an approved ActionIntent with an exact payload match may permit execution.

## First Safe Test Proposal

The first test should be deliberately boring:

- VM/sandbox only.
- No live accounts.
- No passwords.
- No 2FA.
- No banking, email, cloud admin, social media, legal, finance, or private docs.
- One approved action at a time.
- Screenshot only inside a controlled test window.
- Payload-hash-bound execution.
- Immediate stop on payload mismatch.
- Immediate stop on replay attempt.
- Immediate stop on unexpected foreground target.
- Immediate stop if adapter attempts an unapproved action.
- Audit trace records proposal, approval, consume attempt, adapter result, and any mismatch.

Suggested harmless target:

- A local static HTML test page.
- A local toy desktop window.
- A local text field that does not submit anywhere.

## Required Adapter Interface Fields

Minimum `CapabilityAdapterDescriptor` fields for a CUA adapter:

| Field | Purpose |
|---|---|
| `adapter_id` | Stable id, for example `cua_driver_sandbox` |
| `display_name` | Operator-readable name |
| `status` | `not_installed`, `sandbox_ready`, `disabled`, `error`, etc. |
| `can_execute` | Boolean; false until sandbox proof passes |
| `allowed_targets` | Explicit window/app/domain targets |
| `forbidden_targets` | Sensitive apps and domains |
| `required_approval_level` | Per-action approval level |
| `audit_path` | Repo-local audit output path |
| `screenshot_retention_days` | Default should be short, e.g. 3 |

Additional useful fields:

- `sandbox_root`
- `network_allowed`
- `credentials_allowed`
- `max_actions_per_run`
- `kill_switch`
- `last_health_check_at_utc`
- `last_error`

## ActionIntent Requirements

Every CUA action must include:

- action type, such as `screenshot`, `click`, `type_text`, `keypress`, or `read_ui_state`
- exact target
- exact payload
- payload hash
- risk level
- required approval flag
- approval id
- adapter id
- expected foreground target
- max execution window
- no-autosubmit flag where relevant

Actions that must always be blocked unless explicitly designed later:

- credentials/password entry
- 2FA entry
- submit/post/send
- purchase/payment
- trade/investment
- legal/tax filing
- file deletion outside capture cleanup policy
- account settings changes
- stealth browsing or TOS evasion

## Main Risks

### Full Desktop Control

Full desktop control has the widest blast radius. A bug can click the wrong thing, type into the wrong app, or interact with sensitive windows. The sandbox-first requirement is non-negotiable.

### Privacy / Screenshot Capture

Screenshots can expose credentials, private messages, documents, financial data, or personal information. Capture must be explicit, visible, local-only, and retention-limited.

### Credential Exposure

No password manager, browser credential store, 2FA app, banking app, email account, or cloud admin app should be visible during early tests.

### Accidental Real-World Action

Even a single click can submit a form, send a message, purchase something, or publish content. Every consequential action must require a separate ActionIntent and operator approval.

### Provider / TOS Boundaries

CUA tooling must not be used to bypass provider quotas, platform protections, login restrictions, CAPTCHAs, or usage limits.

## Required Dashboard Truth

If a CUA adapter is ever exposed in the dashboard, the dashboard must show:

- adapter status
- sandbox vs host truth
- current target
- last screenshot time
- last proposed action
- whether execution is enabled
- whether approval is required
- last audit event
- stop/kill-switch instructions

It must not say "autonomous computer use" unless the runtime actually supports safe supervised execution and the operator has explicitly enabled it.

## Verdict

Verdict: TOP PRIORITY / use soon after sandbox proof / no runtime wiring yet.

Next safe move: exact repo/source evaluation plus sandbox test plan only. Do not install or execute until the operator explicitly approves a sandbox-only milestone.
