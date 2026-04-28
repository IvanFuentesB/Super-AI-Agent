# N+3.10 Codex Image Digest Gate Review

Status: codex_parallel_audit / digest_gate / no_pull / no_build / no_run / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Image Candidate

Proposed image from existing N+3.9 CUA docs:

```text
trycua/cua-ubuntu:latest
```

Known base image confirmed from local source:

```text
kasmweb/core-ubuntu-jammy:1.17.0
```

Source evidence:

- `21_repos/third_party/evals/cua/blog/ubuntu-docker-support.md:55` shows `docker pull --platform=linux/amd64 trycua/cua-ubuntu:latest`.
- `21_repos/third_party/evals/cua/blog/ubuntu-docker-support.md:70` and `:132` show `image="trycua/cua-ubuntu:latest"`.
- `21_repos/third_party/evals/cua/blog/ubuntu-docker-support.md:91` says the container lands on Ubuntu 22.04 + Xfce and exposes a web viewer at `http://localhost:8006`.
- `21_repos/third_party/evals/cua/blog/ubuntu-docker-support.md:97` notes KasmVNC, non-root `kasm-user`, isolated filesystem unless volumes are mounted, and local-dev SSL behavior.
- `21_repos/third_party/evals/cua/libs/kasm/Dockerfile:1` uses `FROM kasmweb/core-ubuntu-jammy:1.17.0`.
- `21_repos/third_party/evals/cua/examples/sandboxes/test_linux_local_container.py:47` asserts screenshot bytes begin with PNG signature.

## Why `latest` Is Not Enough

`latest` is mutable. It can change between review and execution, which breaks approval-bound behavior. For Ghoti, approval must bind to an exact artifact, not a moving tag.

The first smoke must pin the image digest and approval must reference that exact digest.

## Required Approval Format

Before any pull/build/run:

```text
APPROVE CUA IMAGE DIGEST sha256:<digest> FOR SCREENSHOT-ONLY SMOKE
```

This approval does not authorize click/type, live accounts, privileged containers, broad host mounts, external automation, or runtime adapter promotion.

## Future Digest Commands

Only if Docker daemon is running and the operator approves digest inspection/pull:

```powershell
docker pull trycua/cua-ubuntu:latest
docker image inspect trycua/cua-ubuntu:latest --format '{{json .RepoDigests}}'
```

Codex did not run these commands. Docker daemon is currently not reachable, and this lane is docs-only.

## Must Not Happen Before Digest Approval

- No `docker pull`.
- No `docker build`.
- No `docker run`.
- No CUA container.
- No CUA example execution.
- No Screenpipe capture.
- No click/type.
- No live accounts.
- No host mounts.
- No privileged mode.

## What Claude Code Should Do After Digest Approval

1. Record the exact digest in the smoke plan.
2. Create a screenshot-only ActionIntent.
3. Compute the exact payload hash.
4. Request per-payload operator approval.
5. Pull/run only the approved digest.
6. Bind ports to localhost.
7. Avoid host mounts and privileged mode.
8. Write audit events and stop/remove the container.

## Cleanup / Rollback Notes

Only with explicit cleanup approval later:

```powershell
docker image rm <image-or-digest>
docker system df
```

Do not run `docker system prune` without explicit operator approval because it can delete unrelated Docker artifacts.

## Verdict

```text
digest_not_pinned
blocked_until_daemon
```

Image source is understood well enough to plan, but not enough to execute. The exact digest must be pinned and approved after Docker daemon readiness is proven.
