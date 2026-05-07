# Codex CUA Sandbox Adapter Review - N+3.4

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: ad022a0
Status label: parallel_audit_only / adapter_review / sandbox_first / not_runtime_wired

## Reviewed Architecture

Intended architecture:

```text
Task request
  -> Ghoti planner
  -> ActionIntent
  -> approval gate
  -> payload hash check
  -> CUA adapter descriptor
  -> audit log
  -> dashboard status
```

This is the right shape. The next milestone should not jump directly to click/type execution. The first adapter should be descriptor-only, then observe-only, then screenshot-only in a sandbox, and only later click/type.

## Contract Review

### ActionIntent

ActionIntent is the right boundary because it models the proposed action before execution. CUA actions should be represented as proposed intents even when execution is disabled.

Required fields for CUA-related intents:

- `intent_id`
- `adapter_id`
- `action_type`
- `target`
- `payload`
- `payload_hash`
- `risk_level`
- `requires_approval`
- `approval_id`
- `status`
- `reason`

### Approval Gate

The approval gate must be action-bound and payload-bound. Approval of "use CUA" is not enough. Each consequential action must have a specific approved payload.

### Payload Hash

The payload hash should cover:

- adapter id
- action type
- target
- coordinates or selector if present
- text to type if present
- no-autosubmit flag
- screenshot/capture scope
- allowed window/app/domain

Any mismatch must stop execution and write an audit event.

### Audit Log

Audit log must record:

- intent proposed
- approval requested
- approval accepted/rejected
- consume attempted
- payload hash result
- adapter result
- screenshot path if created
- error/mismatch/replay

### CUA Adapter Descriptor

The first CUA descriptor should be `descriptor_only`, not executable.

Recommended descriptor fields:

- `adapter_id`
- `display_name`
- `status`
- `can_execute`
- `supported_actions`
- `allowed_targets`
- `forbidden_targets`
- `required_approval_level`
- `audit_path`
- `screenshot_retention_days`
- `sandbox_required`
- `host_desktop_allowed`
- `network_allowed`
- `credentials_allowed`
- `last_health_check_at_utc`
- `last_error`

Initial values should include:

- `can_execute: false`
- `sandbox_required: true`
- `host_desktop_allowed: false`
- `credentials_allowed: false`
- `screenshot_retention_days: 3`

## Screenshot Retention

CUA screenshots must use a short retention policy:

- default: 3 days
- local-only
- explicit capture root
- dry-run cleanup before deletion
- no deletion outside approved capture roots
- never store screenshots in git

## Test Ladder

### Phase 1: Descriptor Only

- Create a CUA CapabilityAdapterDescriptor.
- Expose status as disabled/not installed.
- No screenshot.
- No click/type.
- No external adapter process.

### Phase 2: Observe-Only Proposal

- Create an ActionIntent for "observe sandbox target".
- Do not execute it.
- Verify approval-required metadata and audit entry.

### Phase 3: Screenshot-Only Sandbox Smoke

- Sandbox/VM only.
- No live accounts.
- Screenshot one test window.
- Store under local ignored capture/log root.
- Audit trace records path and retention policy.

### Phase 4: Click/Type Later

- Separate milestone.
- One action at a time.
- No auto-submit.
- Only local test UI.
- Stop on mismatch/replay/wrong target.

## Safety Review

Required boundaries:

- no live accounts
- no passwords
- no 2FA
- no banking/email/social/legal/finance apps
- no host desktop control at first
- no click/type at first
- no external websites at first
- no stealth/evasion
- no provider cap bypass
- no background autonomous loop

## Practicality Review

The plan is practical if the project keeps the first implementation boring:

- descriptor-only status first
- then proposal-only ActionIntent
- then screenshot-only sandbox test
- then manual review of audit trail

It becomes unsafe if the next milestone tries to install Cua, launch a driver, and click/type in one jump.

## Recommendation

First adapter should be descriptor-only.

First real test should be screenshot/observe only in a sandbox.

Click/type should be a separate later milestone after the project proves:

- source trust
- sandbox path
- screenshot retention
- ActionIntent approval binding
- dashboard visibility
- replay/mismatch blocking

## Verdict

CUA sandbox adapter plan is safe and practical only if implemented as a staged, sandbox-first, approval-bound ladder. Do not wire execution yet.
