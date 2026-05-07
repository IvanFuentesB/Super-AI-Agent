# CUA Screenshot-Only Smoke — Exact Plan (N+3.9)

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.9
Status: plan_only / not_executed / blocked_until_docker_daemon_running

This is a PLAN ONLY. Do not execute until all preconditions are verified and a separate explicit smoke approval is present.

---

## Preconditions (ALL must be true before any smoke action)

- [ ] Docker Desktop launched manually; daemon running (`docker info` shows Server section)
- [ ] WSL2 installed and active (`wsl --status` returns success, no "not installed" error)
- [ ] Image tag pinned: `trycua/cua-ubuntu@sha256:<digest>` — resolved and operator-approved before any `docker pull`
- [ ] Operator provides separate explicit approval for this CUA screenshot-only smoke
- [ ] ActionIntent created with `computer.observe_screenshot` action type
- [ ] Payload hash computed (SHA-256 of exact payload JSON) and recorded in ActionIntent before execution
- [ ] Audit log file ready: `05_logs/cua_action_audit.jsonl`
- [ ] Output directory pre-created: `05_logs/cua_smoke_runs/<run_id>/`

---

## ActionIntent Shape (required before any execution)

```json
{
  "action_type": "computer.observe_screenshot",
  "adapter_id": "cua-driver-reference",
  "target": "localhost_test_page",
  "payload": {
    "url": "http://localhost:<dashboard_port>",
    "screenshot_only": true,
    "click_allowed": false,
    "type_allowed": false,
    "live_accounts_allowed": false,
    "host_mounts_allowed": false,
    "privileged_container_allowed": false,
    "retention_days": 3
  },
  "requires_human_approval": true,
  "payload_hash": "<sha256-of-exact-payload-json-computed-before-approval>"
}
```

Fallback target if local dashboard is not running:
```json
"url": "https://example.com"
```

No other external URLs are permitted.

---

## Approval Gate

- Operator must approve the exact ActionIntent including payload hash in the dashboard approval inbox
- Approval is per-intent, per-run — not blanket permission
- Payload hash must match at approval time and again at execution time
- Hash mismatch → immediate stop

---

## Docker Image

| Field | Value |
|---|---|
| Pre-built image | `trycua/cua-ubuntu:latest` (Docker Hub) |
| Required before pull | Pin to exact `sha256:` digest; obtain separate operator approval for that digest |
| Base | `kasmweb/core-ubuntu-jammy:1.17.0` |
| Web viewer | `http://localhost:6901` |
| Non-root user | Yes — kasm-user (uid 1000) |
| Privileged mode | NOT required |
| Host mounts | NOT required |

---

## Smoke Workflow (NOT to be executed until preconditions met)

1. Operator launches Docker Desktop; verifies `docker info` shows daemon connected
2. Operator verifies `wsl --status` shows WSL2 installed
3. Resolve `trycua/cua-ubuntu:latest` to exact `sha256:` digest via `docker manifest inspect`
4. Operator approves exact image digest (separate approval item)
5. Create ActionIntent with `computer.observe_screenshot` type and exact payload
6. Compute payload hash; record in ActionIntent before any approval request
7. Operator approves ActionIntent payload hash in approval inbox
8. Pull approved image only (by exact digest, not `latest` tag):
   ```bash
   # DO NOT RUN YET — approval required first
   docker pull trycua/cua-ubuntu@sha256:<approved-digest>
   ```
9. Run isolated container (localhost-only, no host mounts, no privileged):
   ```bash
   # DO NOT RUN YET — approval required first
   docker run --rm \
     --name cua-smoke-01 \
     --shm-size=512m \
     -p 127.0.0.1:6901:6901 \
     trycua/cua-ubuntu@sha256:<approved-digest>
   ```
10. Open `http://localhost:6901` in local browser; wait for desktop to load
11. Verify payload hash still matches approved intent before any screenshot action
12. Write pre-action audit event to `05_logs/cua_action_audit.jsonl`
13. Observe/screenshot only — record result in ActionIntent output
14. Write post-action audit event to `05_logs/cua_action_audit.jsonl`
15. Store artifacts under `05_logs/cua_smoke_runs/<run_id>/`:
    - `action_intent.json`
    - `audit_events.jsonl`
    - `smoke_result.md`
    - screenshot file (if produced, NOT staged in git, 3-day retention)
16. Stop and remove container:
    ```bash
    docker stop cua-smoke-01
    docker rm cua-smoke-01
    ```
17. Confirm no screenshot files staged in git

---

## Allowed Output

| Output | Allowed |
|---|---|
| `05_logs/cua_smoke_runs/<run_id>/action_intent.json` | YES |
| `05_logs/cua_smoke_runs/<run_id>/audit_events.jsonl` | YES |
| `05_logs/cua_smoke_runs/<run_id>/smoke_result.md` | YES |
| Screenshot file (local only, 3-day retention) | YES — if produced by approved smoke only; NOT staged in git |

---

## Stop Conditions

Stop immediately if any of the following occur:

| Condition | Action |
|---|---|
| Docker daemon unreachable | STOP — do not attempt container run |
| WSL2 setup incomplete | STOP — do not attempt container run |
| Image pull fails or digest mismatch | STOP — record failure; do not retry without new approval |
| Container requests `--privileged` mode | STOP — reject run |
| Container requests broad host mount (`-v`) | STOP — reject run |
| Payload hash mismatch between approval and execution | STOP — do not execute action |
| Target URL is not localhost or `example.com` | STOP — reject immediately |
| Browser/VNC navigates away from approved target | STOP |
| Any credential, live account, private document target appears | STOP |
| Click or type action is requested | STOP — not permitted in screenshot-only smoke |
| Docker daemon disconnects during run | STOP — record state; do not retry without operator instruction |
| Any WSL error or instability | STOP — record state |
| Hidden background service behavior observed | STOP — record and report |
| Audit log write fails | STOP — do not proceed without audit trail |

---

## Explicit Non-Goals

- No click
- No type
- No live accounts
- No credentials
- No browsing personal or third-party sites beyond `example.com`
- No stealth or anti-detection behavior
- No scraping
- No autonomous loop
- No privileged container mode
- No broad host filesystem mounts
- No external API calls from agent
- No LLM inference during smoke (observe-only)
- No screenshot staged in git

---

## Approval Requirements Summary

| Approval Item | Type | Status |
|---|---|---|
| Docker daemon running (post-launch verification) | external_result | NOT MET |
| WSL2 installed and active | external_result | NOT MET |
| Image digest approved | user_approval | NOT MET |
| CUA screenshot smoke explicit approval | user_approval | NOT MET |
| ActionIntent payload hash approved | user_approval | NOT MET |

---

## Current Status

Docker Desktop: INSTALLED (4.70.0) — daemon NOT running
WSL2: NOT installed — will install on first Docker Desktop launch
CUA smoke: NOT executed — blocked on all preconditions above
