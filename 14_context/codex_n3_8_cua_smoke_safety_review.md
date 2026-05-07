# N+3.8 Codex CUA Smoke Safety Review

Status: codex_safety_review / next_milestone_only / screenshot_observe_only / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack

## Scope

This review defines the next CUA smoke milestone after Docker Desktop and WSL2 are verified. It does not approve, install, run, or wire CUA in N+3.8.

## First Allowed CUA Smoke

The first CUA smoke must be:

- Screenshot/observe only.
- Targeted only at a local test page, local Ghoti dashboard page, or `https://example.com`.
- No click.
- No type.
- No credentials.
- No live accounts.
- No stealth or anti-bot behavior.
- No third-party browsing beyond the allowed URL.
- No autonomous loop.
- One ActionIntent only.
- One approval item only.
- Payload hash checked before execution.
- Audit event written before and after the attempt.
- Output artifact under `05_logs/cua_smoke_runs/<run_id>/` in a later milestone.

## Required Gate Chain

The first smoke must pass this chain:

1. CUA sandbox descriptor says screenshot-only is allowed.
2. ActionIntent is created with click/type disabled.
3. Payload hash is computed.
4. Operator approval is created for that exact payload.
5. Approval is consumed once.
6. Payload hash is rechecked.
7. Screenshot/observe action runs once.
8. Audit log records result.
9. Container or sandbox is stopped/left idle according to explicit operator instruction.

## Required Output Artifact Shape

Future run artifact directory:

```text
05_logs/cua_smoke_runs/<run_id>/
```

Suggested files:

- `intent.json`
- `approval.json`
- `adapter_result.json`
- `audit_summary.md`
- optional screenshot metadata

Any screenshot file should follow the configured retention policy and must not be staged unless the operator explicitly asks for a small proof artifact.

## Stop Conditions

Stop immediately if:

- Container asks for credentials.
- Docker network or permission behavior is unexpected.
- Browser target is not the approved local page or `example.com`.
- Any component requests click/type.
- Any broad host folder mount is needed.
- Any privileged container flag is requested.
- Any hidden background process appears.
- Any live account, email, social, banking, payment, trading, 2FA, password manager, or private document target appears.
- Payload hash differs from the approved intent.
- Approval cannot be consumed cleanly.

## What Must Stay Blocked

- Click/type.
- Login.
- Live account browsing.
- Posting, outreach, scraping, buying, selling, trading, legal/tax filing, or payment.
- Provider quota or cap bypass.
- Host desktop control.
- External service connection unless separately approved.

## Verdict

The first CUA smoke is safe enough only if it is screenshot/observe-only, sandboxed, approval-bound, payload-hash-bound, and audit-logged. Click/type should be a separate later milestone after screenshot-only proof succeeds.
