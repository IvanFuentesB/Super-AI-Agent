# N+3.10 Codex CUA Smoke Readiness Audit

Status: codex_parallel_audit / smoke_readiness / no_go / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Readiness Table

| Requirement | Status | Evidence / Note |
| --- | --- | --- |
| Docker daemon reachable | NO | Explicit `docker.exe info` cannot connect to `npipe:////./pipe/docker_engine`. |
| WSL2 installed | NO | `wsl --status` says Windows Subsystem for Linux is not installed. |
| CUA repo exists | YES | `21_repos/third_party/evals/cua` exists. |
| CUA HEAD hash | YES | `46dbcb47802e2c712c87e9a34d4d5b06829a2932` via read-only safe-directory command. |
| CUA image source understood | PARTIAL/YES | Docs mention `trycua/cua-ubuntu:latest`; `libs/kasm/Dockerfile` uses `kasmweb/core-ubuntu-jammy:1.17.0`. |
| Image digest pinned | NO | No digest resolved; no network pull/manifest inspection done by Codex. |
| Image digest approved | NO | Required approval phrase has not been provided. |
| ActionIntent exists for smoke | NO | Plan only; no smoke intent created. |
| Payload hash approved | NO | Requires exact ActionIntent first. |
| Audit output path planned | YES | `05_logs/cua_smoke_runs/<run_id>/` in N+3.9 plan. |
| Host mounts disabled | YES in plan | Smoke plan forbids broad host mounts. |
| Privileged disabled | YES in plan | Smoke plan forbids privileged containers. |
| Live accounts disabled | YES in plan/profile | Sandbox profile has `allow_live_accounts=false`. |
| Click/type disabled | YES in plan/profile | Sandbox profile has `allow_click=false`, `allow_type=false`. |
| Screenshot-only confirmed | YES in plan/profile | Sandbox profile allows screenshots only; smoke plan is observe-only. |
| Localhost/example.com only | YES in plan | No other URLs permitted. |
| Runtime adapter promotion | NO | `cua-driver-reference` remains descriptor-only/can_execute=false. |

## Verdict

NO-GO.

Every required safety and environment item must be green before CUA smoke. The current blockers are:

1. Docker daemon unreachable.
2. WSL2 not installed/usable.
3. Image digest not pinned.
4. Image digest not approved.
5. No ActionIntent created.
6. No payload hash approved.

## Future Safe Smoke Sequence

Only after Docker/WSL are ready:

1. Verify `docker info` shows a live Server section.
2. Verify `wsl --status` succeeds and WSL2 is usable.
3. Pin the image digest for `trycua/cua-ubuntu:latest`.
4. Ask the user to approve the exact digest.
5. Create one ActionIntent for screenshot-only observe.
6. Compute the exact payload hash.
7. Ask the user to approve the exact payload hash.
8. Run one screenshot-only observe test.
9. Write audit log and run summary under `05_logs/cua_smoke_runs/<run_id>/`.
10. Stop/remove the container.
11. Commit only small approved metadata/artifacts; do not commit screenshots unless explicitly requested.
12. Do not promote the adapter beyond descriptor-only until a later milestone.

## Must Remain Blocked

- Click/type.
- Live accounts.
- Credentials, 2FA, banking, email, social media, payments, trading.
- Broad host mounts.
- Privileged containers.
- Stealth/evasion.
- Cap/quota bypass.
- Screenpipe capture.
- Runtime CUA wiring.

## Summary

The plan is safe; the machine is not ready. Treat N+3.10 as post-launch verification still blocked, not as a smoke-execution milestone.
