# N+3.7 Codex CUA Screenshot-Only Smoke Spec

Status: smoke_spec / screenshot_observe_only / no_click_type / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack

## Purpose

Define the first safe CUA/TryCUA smoke test after the Docker install gate is explicitly approved and verified. This spec is intentionally observe-only. It does not authorize click, type, login, external browsing, or autonomous loops.

## Preconditions

- Docker Desktop installed only after operator approval.
- CUA/TryCUA sandbox path verified without live accounts.
- Ghoti ActionIntent contract exists before the smoke.
- Human approval exists for the specific screenshot/observe intent.
- Payload hash is computed before execution and must match at execution time.
- Audit trail is ready to record the proposed action, approval, adapter response, and result.

## Allowed First Targets

- Localhost Ghoti dashboard or a local static test page.
- `https://example.com` only if an external public page is needed for the minimal smoke.

No other third-party browsing is allowed in the first smoke.

## Required ActionIntent Shape

The first intent should describe only a screenshot/observe request:

```json
{
  "type": "computer.observe_screenshot",
  "target": "localhost_or_example_com",
  "adapter": "cua_sandbox",
  "requires_human_approval": true,
  "click_type_allowed": false,
  "live_accounts_allowed": false
}
```

The exact payload must be hash-bound before approval and rechecked before execution.

## Smoke Workflow

1. Start only the approved sandbox.
2. Propose one screenshot-only ActionIntent.
3. Require human approval for that exact payload hash.
4. Execute observe/screenshot only if the hash matches.
5. Write an audit event before and after the attempt.
6. Store only the minimal screenshot/metadata needed for proof.
7. Stop the sandbox or leave it idle as directed by the operator.

## Pass Criteria

- One approved screenshot/observe action runs in the sandbox.
- No click/type action is available or executed.
- No credentials or live accounts appear in the target.
- Audit trail records the attempt and result.
- Dashboard/read model can report the latest CUA adapter status if implemented.
- Any retained screenshot follows the configured retention policy.

## Fail Criteria

- Payload hash mismatch.
- Missing approval.
- Adapter attempts click/type.
- Target is not localhost or `example.com`.
- Live account, credential, private document, payment, trading, email, or social target appears.
- Container requests privileged mode or broad host mounts.

## Explicitly Blocked Until Later Milestones

- Click/type.
- Login or credential entry.
- Multi-step browsing.
- Autonomous loops.
- External posting, outreach, scraping, purchases, trades, legal filings, or payment actions.
- Native desktop control outside a sandbox.

## Current Truth

Docker is not currently available from this shell and WSL is not installed. This smoke spec is therefore future-facing and must not be treated as a completed or runtime-wired capability.
