# CUA ActionIntent + Payload Hash Gate -- N+3.12

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.12
Status: action_intent_created / payload_hash_computed / AWAITING_BOTH_APPROVALS

---

## Summary

The ActionIntent and payload hash have been created for the N+3.12 screenshot-only CUA smoke run.
No execution has occurred. Both approval phrases are still required before any docker pull or run.

---

## Smoke Run Directory

05_logs/cua_smoke_runs/n3_12_20260428_1300/

---

## ActionIntent File

05_logs/cua_smoke_runs/n3_12_20260428_1300/action_intent.json

### Key Fields

| Field | Value |
|---|---|
| intent_id | intent-n3-12-cua-smoke-20260428-1300 |
| created_at_utc | 2026-04-28T13:00:00Z |
| action_type | computer.observe_screenshot |
| adapter_id | cua-docker-ubuntu-screenshot-only |
| target | local container web UI / screenshot-only |
| image | trycua/cua-ubuntu@sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a |
| allow_click | false |
| allow_type | false |
| allow_live_accounts | false |
| allow_host_mounts | false |
| allow_privileged | false |
| allowed_network | docker_pull_only + localhost_access_only |
| stop_after_seconds | 120 |
| cleanup_required | true |
| execution_status | NOT_EXECUTED |

---

## Payload Hash

Canonical payload JSON (sorted keys, compact separators):
{"allow_click":false,"allow_host_mounts":false,"allow_live_accounts":false,"allow_privileged":false,"allow_type":false,"allowed_network":"docker_pull_only + localhost_access_only","cleanup_required":true,"image":"trycua/cua-ubuntu@sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a","output_dir":"05_logs/cua_smoke_runs/n3_12_20260428_1300","stop_after_seconds":120}

Hash algorithm: sha256
Hash: 69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4

Payload hash file: 05_logs/cua_smoke_runs/n3_12_20260428_1300/payload_hash.txt

---

## Approval Gate Status

### Approval 1 — Image Digest (required first)

Status: NOT PROVIDED
Required phrase:
  APPROVE CUA IMAGE DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a FOR SCREENSHOT-ONLY SMOKE

### Approval 2 — Smoke Execution (required after Approval 1)

Status: NOT PROVIDED
Required phrase (use exact payload hash above):
  APPROVE CUA SCREENSHOT-ONLY SMOKE WITH DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a AND PAYLOAD 69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4

Both approvals must be present before any docker pull or docker run.

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
