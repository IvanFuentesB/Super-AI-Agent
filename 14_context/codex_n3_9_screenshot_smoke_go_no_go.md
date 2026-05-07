# N+3.9 Codex Screenshot Smoke Go / No-Go Review

Status: codex_go_no_go / no_go / screenshot_smoke_blocked / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack

## Decision

NO-GO.

Reason:

- Docker daemon is not running.
- Docker is not on PATH in this shell.
- WSL is not installed.
- Docker Desktop process is not running.
- CUA image/build path is not yet separately approved.

## GO Conditions

The CUA screenshot-only smoke may become GO only if all are true:

- Docker daemon is running and `docker info` succeeds.
- WSL2 is installed/usable or Docker Desktop has an equivalent healthy Linux backend.
- Docker Desktop is running and stable.
- Exact image/tag or build path is reviewed and approved.
- ActionIntent exists for screenshot/observe only.
- Operator approval exists for the exact payload hash.
- Audit output path is ready.

## First Smoke Definition

The first allowed smoke must be:

- Screenshot/observe only.
- Target: localhost Ghoti dashboard/local test page or `https://example.com`.
- No click.
- No type.
- No credentials.
- No live accounts.
- No stealth or anti-bot behavior.
- No broad host mounts.
- No privileged containers.
- No autonomous loop.
- ActionIntent required.
- Payload hash required.
- Approval item required.
- Audit event required.
- Output only under `05_logs/cua_smoke_runs/<run_id>/`.

## Required Output Artifacts Later

Future smoke artifact directory:

```text
05_logs/cua_smoke_runs/<run_id>/
```

Suggested files:

- `action_intent.json`
- `approval_record.json`
- `payload_hash.txt`
- `adapter_result.json`
- `audit_events.jsonl`
- `smoke_result.md`

Screenshots should remain local, retention-limited, and unstaged unless the operator explicitly requests a small proof artifact.

## Stop Conditions

Stop immediately if:

- Docker daemon is unreachable.
- WSL reports missing or unhealthy state.
- Container requests credentials.
- Target changes away from localhost/local page or `example.com`.
- Click/type is requested.
- Privileged mode is requested.
- Broad host mount is requested.
- Any hidden background process appears.
- Any live account, private document, banking, email, social, trading, payment, password manager, or 2FA target appears.
- Payload hash does not match approval.
- Approval cannot be consumed once and only once.

## What Remains Forbidden

- CUA container run before daemon/WSL verification.
- Image pull/build/run before exact source approval.
- Click/type in first smoke.
- Provider API keys in first smoke.
- Live accounts.
- External posting, scraping, outreach, purchases, trades, or legal/tax filings.
- Stealth/evasion.
- Cap/quota bypass.

## Verdict

NO-GO for N+3.9 smoke execution. The next safe milestone is Docker Desktop post-launch/reboot verification, not CUA execution.
