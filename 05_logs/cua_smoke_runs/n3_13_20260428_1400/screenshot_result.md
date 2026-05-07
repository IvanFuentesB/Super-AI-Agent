# CUA Screenshot-Only Smoke Result — N+3.13

Date: 2026-04-28
Milestone: N+3.13
Run dir: 05_logs/cua_smoke_runs/n3_13_20260428_1400/
Status: PASS (container started, KasmVNC reachable, no auth performed)

---

## Execution Summary

| Step | Result |
|---|---|
| Preflight checks (Docker, WSL, digest, approvals) | PASS |
| docker pull (pinned digest) | PASS — 18.5 GB image pulled |
| docker run (safe constraints) | PASS — container started |
| Container status check (docker ps) | PASS — Up, port 127.0.0.1:6901->6901/tcp |
| Docker logs captured | PASS — KasmVNC initialized normally |
| Localhost probe http://127.0.0.1:6901 | PASS — HTTP 401 (KasmVNC auth prompt, expected) |
| No click / no type / no login | CONFIRMED |
| Container stop | PASS — stopped cleanly |
| Container removal (--rm) | PASS — no container remains |

---

## Screenshot Capture

No screenshot file captured. No Playwright, curl download, or screenshot tool was used.
The HTTP 401 response from KasmVNC confirms the web UI is running and accessible.
A real screenshot would require browser automation (not permitted in this smoke).

Observable evidence: HTTP 401 header from localhost:6901 = KasmVNC web UI running.

---

## Safety Confirmations

| Constraint | Status |
|---|---|
| No --privileged | CONFIRMED |
| No host volume mounts (-v) | CONFIRMED |
| localhost-only port (127.0.0.1:6901) | CONFIRMED |
| No click | CONFIRMED |
| No type | CONFIRMED |
| No live accounts | CONFIRMED |
| No external upload of evidence | CONFIRMED |
| One container only | CONFIRMED |
| Container stopped after test | CONFIRMED |
| Container removed (--rm) | CONFIRMED |
| Max 120 second runtime | CONFIRMED (stopped ~30s after start) |

---

## Digest Used

sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a

Matches approved digest in N+3.13 prompt.

---

## Runtime Wiring

- CUA is NOT wired into Ghoti runtime
- No autonomous execution enabled
- This was a manual operator-approved smoke test only
- brain_inference_ready: unchanged
- autonomous_execution_enabled: false
