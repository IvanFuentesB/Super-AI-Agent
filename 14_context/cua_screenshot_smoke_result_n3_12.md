# CUA Screenshot Smoke Result -- N+3.12

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.12
Status: NOT_EXECUTED_APPROVAL_REQUIRED

---

## Execution Status

NOT_EXECUTED_APPROVAL_REQUIRED

The CUA screenshot-only smoke was NOT executed in N+3.12.

Reason: Neither required approval phrase was provided by the operator in this session.

---

## Required Approvals (both still pending)

### Approval 1 — Image Digest

Provide this exact phrase before any docker pull or run:

  APPROVE CUA IMAGE DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a FOR SCREENSHOT-ONLY SMOKE

### Approval 2 — Smoke Execution with Payload Hash

Provide this exact phrase after Approval 1 (note: payload hash is specific to this ActionIntent):

  APPROVE CUA SCREENSHOT-ONLY SMOKE WITH DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a AND PAYLOAD 69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4

---

## Readiness Summary (as of N+3.12)

| Precondition | Status |
|---|---|
| Docker daemon running | GO |
| WSL2 docker-desktop Running 2 | GO |
| Docker context desktop-linux | GO |
| Image digest pinned and verified | GO (sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a) |
| Digest unchanged from N+3.11 | YES |
| ActionIntent created | YES (intent-n3-12-cua-smoke-20260428-1300) |
| Payload hash computed | YES (69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4) |
| Approval 1 (image digest) | NOT PROVIDED |
| Approval 2 (smoke + payload hash) | NOT PROVIDED |

---

## Smoke Artifacts

| Artifact | Path | Status |
|---|---|---|
| ActionIntent JSON | 05_logs/cua_smoke_runs/n3_12_20260428_1300/action_intent.json | CREATED |
| Payload hash | 05_logs/cua_smoke_runs/n3_12_20260428_1300/payload_hash.txt | CREATED |
| Audit events | 05_logs/cua_smoke_runs/n3_12_20260428_1300/audit_events.jsonl | NOT CREATED (smoke not executed) |
| Smoke result | 05_logs/cua_smoke_runs/n3_12_20260428_1300/smoke_result.md | NOT CREATED (smoke not executed) |
| Screenshot | 05_logs/cua_smoke_runs/n3_12_20260428_1300/screenshot_*.png | NOT CAPTURED |

---

## Safety Confirmations

- docker pull: NOT executed
- docker run: NOT executed
- No container started
- No host mounts
- No privileged mode
- No live accounts
- No click or type
- No Screenpipe capture
- No credentials used
