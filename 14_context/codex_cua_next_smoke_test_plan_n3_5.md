# Codex CUA Next Smoke Test Plan - N+3.5

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: ca403cd
Status label: smoke_test_plan / screenshot_observe_only / not_runtime_wired

## Goal

Design the first future CUA smoke test so Claude Code can implement it later without broadening Ghoti into unsafe desktop automation.

This plan is for a future milestone only. This Codex lane did not execute CUA, capture screenshots, click, type, or modify runtime.

## Test Name

`cua_screenshot_observe_only_sandbox_smoke`

## Test Target

Preferred target:

- local static HTML test page served from Ghoti dashboard or a file-backed local page

Acceptable fallback:

- `https://example.com`

Not acceptable:

- live accounts
- logged-in browser sessions
- password managers
- email
- banking
- payments
- trading
- social posting
- private documents

## Test Contract

The smoke test must:

1. Create one ActionIntent.
2. Set `adapter_id` to a CUA sandbox descriptor, for example `cua_sandbox_screenshot`.
3. Set action type to `observe_screen` or `capture_screenshot`.
4. Set target to a local page or `example.com`.
5. Set `requires_approval=true`.
6. Bind exact payload hash.
7. Require human approval before consume.
8. Execute observe/screenshot only after approval.
9. Write audit event for proposed, approved, consumed, and result states.
10. Update dashboard read status only if a read route already exists or a future route is explicitly added.

## Required Payload Shape

Suggested payload:

```json
{
  "target_kind": "browser_page",
  "target": "local_dashboard_or_example_com",
  "allowed_url": "http://127.0.0.1:<port>/cua-test.html",
  "capture_mode": "screenshot_only",
  "allow_click": false,
  "allow_type": false,
  "allow_shell": false,
  "allow_live_accounts": false,
  "retention_days": 3
}
```

If using `example.com`, replace `allowed_url` with `https://example.com` and record that it is the IANA reference domain, not a login target.

## Expected Audit Events

Minimum audit event sequence:

- `cua_intent_proposed`
- `cua_approval_requested`
- `cua_approval_granted` or `cua_approval_rejected`
- `cua_payload_hash_verified`
- `cua_observe_started`
- `cua_observe_completed` or `cua_observe_failed`
- `cua_result_recorded`

If any mismatch occurs:

- `cua_payload_hash_mismatch`
- `cua_execution_blocked`

## Dashboard Read Status

If dashboard integration is included later, it should show:

- adapter id
- status
- sandbox-only truth
- action type
- target
- approval status
- last audit event
- last screenshot path, if any
- retention days
- `click_enabled=false`
- `type_enabled=false`
- `live_accounts_enabled=false`

## What Must Stay Disabled

- click
- type
- shell
- file upload
- live accounts
- credentials
- 2FA
- posting
- payment/purchase
- trading/investing
- legal/tax filing
- autonomous loop
- external account mutation

## Pass Criteria

The future smoke test passes only if:

- one ActionIntent is proposed
- human approval is required
- payload hash is checked
- no click/type/shell occurs
- screenshot/observe target is safe
- audit event is written
- status read model is honest
- screenshot/traces are not staged
- no third-party files are staged

## Fail Criteria

Fail immediately if:

- CUA attempts click/type
- CUA touches host desktop outside sandbox/test target
- target is not allowlisted
- live account or sensitive content is visible
- payload hash mismatches
- replay attempt is detected
- screenshot path escapes approved capture root
- any install/clone/run occurs without explicit operator approval

## Implementation Advice For Claude Code

Start with a fake/dry-run adapter if CUA is not installed:

- create descriptor
- create ActionIntent
- require approval
- simulate "observe blocked because CUA not installed"
- write audit event

This proves the Ghoti side before trusting any external driver.

## Verdict

Next smoke should be screenshot/observe-only, one ActionIntent, approved manually, payload-hash checked, local audit written, and dashboard-readable. Click/type belongs in a later milestone.
