# CUA Next Screenshot-Only Smoke — After Docker Verified (N+3.8)

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Status: smoke_plan / not_executed / awaiting_docker_daemon_and_separate_approval

---

## Purpose

This document defines the exact design for the first CUA screenshot-only smoke test.
It is a PLAN ONLY. Do not execute until:
1. Docker Desktop is running and `docker info` shows daemon connected.
2. WSL2 is installed and verified.
3. Operator provides explicit separate approval for this smoke.

---

## Preconditions (all must be true before smoke)

- [ ] Docker Desktop launched manually; daemon running (`docker info` succeeds)
- [ ] WSL2 installed and active (`wsl --status` shows no error)
- [ ] Operator provides separate explicit approval for the CUA smoke test
- [ ] ActionIntent created with `computer.observe_screenshot` type
- [ ] Payload hash computed and recorded before execution
- [ ] Audit log ready at `05_logs/cua_action_audit.jsonl`
- [ ] Output artifact directory pre-created: `05_logs/cua_smoke_runs/<run_id>/`

---

## Smoke Design

### Target

- Local-only: Ghoti dashboard at `http://localhost:<dashboard_port>` (preferred)
- Fallback external: `https://example.com` only — no other external URL allowed

### ActionIntent Shape (required before any execution)

```json
{
  "type": "computer.observe_screenshot",
  "target": "localhost_or_example_com",
  "adapter": "cua_sandbox",
  "requires_human_approval": true,
  "click_type_allowed": false,
  "live_accounts_allowed": false,
  "payload_hash": "<sha256-of-exact-payload-computed-before-execution>"
}
```

The payload hash must be computed before approval and rechecked at execution time.
Hash mismatch = immediate stop.

### Approval Gate

- Operator must approve the exact ActionIntent payload hash in the dashboard approval inbox
- Approval is per-intent, per-run — not blanket permission
- Replay consumption is rejected

---

## Smoke Workflow (NOT to be executed until above preconditions met)

1. Start Docker Desktop daemon (manual operator action)
2. Verify `docker info` shows server running
3. Read `21_repos/third_party/evals/cua/libs/kasm/README.md` to confirm exact image/tag
4. Operator approves specific image and tag (separate approval required before any `docker pull`)
5. Create ActionIntent for `computer.observe_screenshot`
6. Compute payload hash; record in ActionIntent
7. Operator approves ActionIntent payload hash in approval inbox
8. Pull approved image only (no other images)
9. Run isolated container:

```bash
# DO NOT RUN YET — shape only
docker run --rm \
  --name cua-smoke-01 \
  --shm-size=512m \
  -p 127.0.0.1:6901:6901 \
  <approved-kasm-image>:<approved-tag>
```

Constraints:
- No `--privileged` flag
- No `-v` host mounts
- Ports bound to `127.0.0.1` only
- No provider API keys in environment
- No live credentials

10. Open `http://localhost:6901` in local browser
11. Screenshot the container desktop or navigate to `example.com` inside container
12. Verify payload hash still matches before screenshot action
13. Write audit event to `05_logs/cua_action_audit.jsonl` (before and after attempt)
14. Store minimal screenshot/metadata under `05_logs/cua_smoke_runs/<run_id>/`
15. Stop container: `docker stop cua-smoke-01; docker rm cua-smoke-01`
16. Confirm no screenshot files staged in git

---

## Stop Conditions

Stop immediately if any of the following occur:
- Payload hash mismatch between approval and execution
- Missing ActionIntent approval in inbox
- Container requests `--privileged` mode
- Container requests broad host mounts (`-v`)
- Target is not localhost or `example.com`
- Live account, credentials, private document, payment, or social target appears
- Adapter attempts any click or type action
- Docker daemon disconnects
- Any WSL error or instability

---

## Output Artifacts

All output under: `05_logs/cua_smoke_runs/<run_id>/`
- `action_intent.json` — the approved intent record
- `audit_events.jsonl` — pre/post audit entries
- `smoke_result.md` — pass/fail summary
- Screenshots: stored locally, NOT staged in git, subject to 3-day retention policy

---

## What Is Explicitly Blocked

- Click or type actions (none permitted in first smoke)
- Login or credential entry
- Multi-step browsing
- Autonomous loops
- External posting, outreach, scraping, purchases
- Privileged container mode (without explicit second approval)
- Host filesystem mounts (without explicit second approval)
- Any CUA action without pre-approved ActionIntent
- Any action without audit log entry

---

## Current Status

Docker Desktop: INSTALLED (4.70.0) — daemon NOT yet running
WSL2: NOT installed yet — will be installed by Docker Desktop on first launch
CUA smoke: NOT executed — awaiting manual Docker Desktop launch + daemon verification + separate approval
