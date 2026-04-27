# N+3.8 Codex Next Execution Plan

Status: codex_execution_plan / no_runtime_changes / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack

## If Docker Install Succeeds

Recommended next milestone:

```text
N+3.9 CUA screenshot-only sandbox smoke
```

Claude Code should:

1. Re-verify Docker/Compose/WSL with explicit command output.
2. Re-read CUA Kasm/Docker docs in the local clone.
3. Propose the exact Docker image/tag or build path before pulling/building.
4. Create one screenshot-only ActionIntent.
5. Create one operator approval tied to the payload hash.
6. Run only a screenshot/observe smoke after approval.
7. Write audit artifacts under `05_logs/cua_smoke_runs/<run_id>/`.
8. Stop before click/type.

Codex should:

1. Review the exact proposed Docker command before execution if possible.
2. Crosscheck that no host mounts, privileged flags, live accounts, or click/type are present.
3. Review the audit artifact after the smoke.

User must approve:

- Exact image/tag or build path.
- Exact screenshot-only ActionIntent.
- Any retained screenshot proof artifact.

## If Docker Install Fails Or Reboot Is Required

Recommended next milestone:

```text
N+3.8a Docker post-reboot verification
```

Claude Code should stop at the failed/reboot-required state and report exact commands/output. Do not try to work around Docker failure with unsafe host automation.

Codex should audit post-reboot Docker/WSL state and confirm whether the CUA path is still blocked.

## If Docker Is Rejected Later

Recommended fallback:

```text
N+3.9 Screenpipe route UI card + Obsidian vault sync workflow
```

Use no-install progress:

- Read-only Screenpipe dashboard status.
- Vault note sync/update runbook.
- Wait/resume card visibility.
- AutoBrowser and Obscura remain research-only until explicitly approved.

## Exact Recommended Claude Code Next Task

If Docker is verified:

```text
Implement N+3.9 CUA screenshot-only smoke: one local sandbox observe action, one ActionIntent, one approval, payload hash check, one audit artifact, no click/type.
```

If Docker is not verified:

```text
Implement N+3.8a Docker post-reboot verification or fallback to Screenpipe status UI + Obsidian sync.
```

## Exact Recommended Codex Next Task

```text
N+3.9-CODEX Review CUA screenshot-only smoke command, artifact, and audit trail.
```

## What Remains Forbidden

- Runtime wiring without approval.
- Click/type in the first smoke.
- Live accounts.
- Host desktop control.
- Host mounts.
- Privileged containers.
- Background autonomy.
- Stealth/evasion.
- Cap/quota bypass.
- External posting, scraping, outreach, purchases, trades, or legal/tax filings.

## Runtime Wiring Truth

This plan adds no runtime wiring and performs no installation or CUA execution. It exists only to keep the Docker install gate and next CUA smoke safe, small, auditable, and approval-bound.
