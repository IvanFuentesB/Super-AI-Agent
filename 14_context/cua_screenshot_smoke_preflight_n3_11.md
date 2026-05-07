# CUA Screenshot Smoke Preflight Plan -- N+3.11

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.11
Status: ready_for_separate_smoke_approval

---

## IMPORTANT: This is a PLAN ONLY. Do NOT execute the smoke until:
1. Operator provides the image digest approval phrase.
2. Operator provides the smoke execution approval phrase (separate item).
3. ActionIntent is created with exact payload and payload hash.

---

## Prerequisites Checked

| Precondition | Status | Notes |
|---|---|---|
| Docker Desktop process running | PASS | 4 PIDs confirmed |
| WSL2 installed and active | PASS | docker-desktop Running version 2 |
| Docker daemon reachable | PASS | docker info returns Server section; 16 CPUs, 15.27 GiB |
| Docker context | PASS | desktop-linux |
| Docker CLI on PATH | PASS | docker 29.4.0 via PATH |
| Image digest pinned | PASS | sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a (amd64) |
| Image digest approved | NOT MET | Separate operator approval required |
| ActionIntent created | NOT MET | Blocked on digest approval |
| Payload hash computed | NOT MET | Blocked on ActionIntent creation |
| Smoke approval obtained | NOT MET | Separate approval required |
| Audit path pre-created | NOT MET | Minor; create at smoke time |

---

## Image Digest Gate Status

- Tag: trycua/cua-ubuntu:latest
- Pinned digest (linux/amd64, this host): sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a
- Tag is mutable: YES -- must reference by digest, not by latest tag
- Pull/run must reference: trycua/cua-ubuntu@sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a

---

## ActionIntent Fields for Future Screenshot-Only Smoke

{
  action_type: computer.observe_screenshot,
  adapter_id: cua-docker-ubuntu-reference,
  target: https://example.com (or http://localhost:<dashboard_port> if running),
  payload: {
    image_reference: trycua/cua-ubuntu@sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a,
    screenshot_only: true,
    click_allowed: false,
    type_allowed: false,
    live_accounts_allowed: false,
    host_mounts_allowed: false,
    privileged_allowed: false,
    network_allowed: true,
    allowed_network_targets: [docker pull registry, example.com],
    container_port: 127.0.0.1:6901:6901,
    shm_size: 512m,
    retention_days: 3
  },
  requires_human_approval: true,
  payload_hash: <sha256-of-exact-payload-json-computed-before-approval>
}

---

## Payload Hash Approval Requirement

Before any execution:
1. Serialize the exact ActionIntent payload JSON
2. Compute SHA-256 of the serialized payload
3. Record hash in ActionIntent before requesting approval
4. Operator approves the hash in the approval inbox
5. Re-verify hash matches at execution time -- mismatch -> immediate stop

---

## Audit Event Requirements

Before smoke run:
- Write pre_action audit event to 05_logs/cua_action_audit.jsonl
  Fields: timestamp, action_type, adapter_id, target, payload_hash, approval_status

After smoke run (pass or fail):
- Write post_action audit event to 05_logs/cua_action_audit.jsonl
  Fields: timestamp, action_type, result, artifacts_path, stop_reason (if any)

---

## Output Artifact Path

All smoke artifacts under: 05_logs/cua_smoke_runs/<run_id>/

| Artifact | Path |
|---|---|
| ActionIntent JSON | 05_logs/cua_smoke_runs/<run_id>/action_intent.json |
| Audit events | 05_logs/cua_smoke_runs/<run_id>/audit_events.jsonl |
| Smoke result | 05_logs/cua_smoke_runs/<run_id>/smoke_result.md |
| Screenshot (if captured) | 05_logs/cua_smoke_runs/<run_id>/screenshot_<ts>.png -- NOT staged in git, 3-day retention |

---

## Exact Approval Phrase Required

### Step 1 -- Image digest approval (provide before any pull/run):

  APPROVE CUA IMAGE DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a FOR SCREENSHOT-ONLY SMOKE

### Step 2 -- Smoke execution approval (provide after ActionIntent and payload hash are computed):

  APPROVE CUA SCREENSHOT-ONLY SMOKE WITH DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a AND PAYLOAD <payload_hash>

Both approvals are required. Step 2 cannot occur before Step 1.

---

## Stop Conditions (enforced at execution time)

| Condition | Action |
|---|---|
| Image digest mismatch vs approved | STOP |
| Payload hash mismatch | STOP |
| Container requests --privileged | STOP |
| Container requests broad host mount -v | STOP |
| Target URL other than localhost or example.com | STOP |
| Browser navigates away from approved target | STOP |
| Any credential or live account appears | STOP |
| Any click or type action requested | STOP |
| Docker daemon disconnects | STOP |
| Audit log write fails | STOP |

---

## Final Verdict

**ready_for_separate_smoke_approval**

- docker_daemon: READY
- wsl2: READY
- digest_pinned: YES (sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a)
- digest_approved: NOT YET -- awaiting operator approval phrase
- smoke_approved: NOT YET -- awaiting separate smoke approval phrase
- next_milestone: N+3.12 -- CUA screenshot-only smoke execution after explicit digest + payload approval
