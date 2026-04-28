# N+3.13 Codex CUA Smoke Execution Risk Review

Status: codex_parallel_audit / smoke_risk_review / no_pull / no_run / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Digest Recheck

Read-only command run:

```powershell
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' manifest inspect trycua/cua-ubuntu:latest
```

Result: linux/amd64 digest still matches the approved/pinned digest.

```text
sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a
```

`latest` remains mutable. The digest is the approval boundary, not the tag.

## Approval State

User provided:

```text
APPROVE CUA IMAGE DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a FOR SCREENSHOT-ONLY SMOKE
```

This is sufficient for the image digest gate. It should allow Claude Code to pull only the pinned digest if Docker is ready in Claude's execution shell.

Existing N+3.12 payload gate requires a second approval phrase for execution:

```text
APPROVE CUA SCREENSHOT-ONLY SMOKE WITH DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a AND PAYLOAD 69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4
```

That exact second phrase was not present in this Codex prompt.

## ActionIntent / Payload Hash Truth

Files read:

- `05_logs/cua_smoke_runs/n3_12_20260428_1300/action_intent.json`
- `05_logs/cua_smoke_runs/n3_12_20260428_1300/payload_hash.txt`

Codex recomputed the SHA-256 hash from `action_intent.json` payload using sorted keys and compact separators.

| Field | Truth |
| --- | --- |
| Expected payload hash | `69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4` |
| Recomputed hash | `69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4` |
| Hash matches | YES |
| Action type | `computer.observe_screenshot` |
| Adapter | `cua-docker-ubuntu-screenshot-only` |
| Image | `trycua/cua-ubuntu@sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a` |
| Click allowed | false |
| Type allowed | false |
| Live accounts allowed | false |
| Host mounts allowed | false |
| Privileged allowed | false |
| Stop after seconds | 120 |
| Cleanup required | true |

## Risk Verdict

| Gate | Verdict |
| --- | --- |
| Image digest | GO for approved pinned digest only |
| Docker pull | GO only in Claude shell if `docker info` works and pull uses exact digest |
| Docker run / smoke execution | NO-GO until exact payload-hash approval is provided |
| Click/type | BLOCKED |
| Live accounts | BLOCKED |
| Host mounts | BLOCKED |
| Privileged container | BLOCKED |
| Runtime adapter promotion | BLOCKED |

## Runtime Constraints If Claude Executes Later

- Use pinned digest only.
- Bind localhost only.
- No host mounts.
- No privileged mode.
- No click/type.
- No live accounts.
- Stop/remove container after test.
- Log output under `05_logs/cua_smoke_runs/n3_13_<timestamp>/`.
- Do not stage screenshot files unless the operator explicitly asks for a proof artifact.
- Keep the adapter descriptor-only after the smoke.

## GO / NO-GO

```text
GO for image digest pull only, if Docker works in Claude shell.
NO-GO for screenshot smoke execution until exact payload hash approval is given.
```

Codex did not pull, run, build, execute CUA, capture screenshots, click/type, or start Screenpipe.
