# CUA Screenshot Smoke Readiness — N+3.10

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.10
Status: NO-GO

---

## CUA Smoke Readiness Table

| Precondition | Status | Notes |
|---|---|---|
| Docker daemon running | **NO** | Engine returning HTTP 503; "unable to start"; WSL2 not installed |
| WSL2 ready | **NO** | Not installed; exit code 50; will install via Docker Desktop GUI |
| Image digest pinned | **NO** | Cannot pin until daemon is running and `docker manifest inspect` can run |
| Image digest approved | **NO** | Requires separate operator approval after digest is resolved |
| ActionIntent created | **NO** | Requires daemon ready and digest approval first |
| Payload hash approved | **NO** | Requires ActionIntent creation first |
| Audit path ready | **NO** | `05_logs/cua_action_audit.jsonl` not yet pre-created |
| click/type disabled | YES | Hardcoded in smoke plan: `click_allowed=false, type_allowed=false` |
| live accounts disabled | YES | Hardcoded in smoke plan: `live_accounts_allowed=false` |
| host mounts disabled | YES | Hardcoded in smoke plan: `host_mounts_allowed=false` |
| privileged disabled | YES | Hardcoded in smoke plan: `privileged_container_allowed=false` |

---

## GO/NO-GO Verdict

**NO-GO**

---

## Missing Preconditions (exact list)

1. **Docker daemon not running** — Docker Desktop GUI launched but engine cannot start; WSL2 not installed
2. **WSL2 not installed** — operator must interact with Docker Desktop window to trigger WSL2 setup; reboot likely required
3. **GUI interaction incomplete** — Docker Desktop window is open showing Docker Hub login/signup; operator must navigate this before engine starts
4. **Image digest not pinned** — `docker manifest inspect trycua/cua-ubuntu:latest` cannot run until daemon is ready
5. **Image digest not approved** — requires separate approval after digest resolved
6. **ActionIntent not created** — blocked on daemon + digest
7. **Payload hash not approved** — blocked on ActionIntent
8. **Audit path not pre-created** — minor; can be done once daemon is ready

---

## Next Steps to Reach GO State

In order:

1. **Operator interacts with Docker Desktop window** (currently open on screen):
   - Sign in or skip Docker Hub login
   - Accept WSL2 install prompt when shown
   - Wait for "Docker Engine running" status
   - Reboot if prompted; relaunch Docker Desktop after reboot

2. **Verify daemon running** in a new terminal:
   - `docker info` — must show Server section
   - `wsl --status` — must show WSL2 installed

3. **Pin image digest** (next milestone, after daemon verified):
   - `docker manifest inspect trycua/cua-ubuntu:latest` → extract `sha256:` digest
   - Record exact digest in a new doc

4. **Separate operator approval for image digest**

5. **Create ActionIntent** with `computer.observe_screenshot` type and exact payload

6. **Compute payload hash** (SHA-256 of payload JSON)

7. **Separate operator approval for CUA smoke** (ActionIntent + payload hash both approved)

8. **Pre-create audit path**: `05_logs/cua_action_audit.jsonl`

9. **Execute smoke** only after all above are met

---

## Reference Plans

- CUA screenshot smoke exact plan: `14_context/cua_screenshot_smoke_exact_plan_n3_9.md`
- Docker Desktop post-launch verification: `14_context/docker_desktop_post_launch_verification_n3_10.md`
- CUA image/source truth: `14_context/cua_docker_image_source_truth_n3_9.md`
- CUA sandbox profile: `23_configs/cua_sandbox_profile.example.json`

---

## Summary Statement

**CUA screenshot smoke is still NO-GO.** Docker Desktop process IS now running (new since N+3.9), but the engine cannot start because WSL2 is not installed. The operator must complete GUI interaction with the Docker Desktop window (currently open on screen) to trigger WSL2 setup. A reboot is likely required. Once the daemon is verified running and WSL2 is confirmed installed, a separate milestone must resolve the image digest and obtain explicit smoke approval before any container is run.

This prompt does NOT authorize CUA smoke execution. Ready state requires a separate explicit approval prompt.
