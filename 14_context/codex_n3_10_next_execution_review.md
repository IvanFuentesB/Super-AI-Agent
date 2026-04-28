# N+3.10 Codex Next Execution Review

Status: codex_parallel_audit / next_execution_review / no_runtime_changes / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## If Docker Daemon Is Ready Later

Recommended next milestone:

```text
N+3.11 image digest pin + ActionIntent smoke gate
```

Claude Code should:

1. Verify `docker info` and `wsl --status`.
2. Pin `trycua/cua-ubuntu:latest` to a digest.
3. Ask for exact digest approval.
4. Create one screenshot-only ActionIntent.
5. Compute payload hash.
6. Ask for exact payload approval.
7. Pull/run only the approved digest.
8. Produce only metadata, audit logs, and optional local screenshot proof.
9. Stop/remove container.
10. Keep `cua-driver-reference` descriptor-only after smoke.

## If Docker Daemon Is Still Blocked

Recommended next milestone:

```text
N+3.10a Docker Desktop manual launch / reboot verification
```

Claude Code should:

1. Ask the user to manually launch Docker Desktop.
2. Let Docker Desktop complete WSL2 setup.
3. Reboot only if prompted and operator agrees.
4. Re-run Docker/WSL checks in a new terminal.
5. Stop before image pull/build/run.

## What Codex Should Avoid

- Installing Docker/WSL.
- Launching Docker Desktop.
- Pulling/building/running images.
- Running CUA examples.
- Editing runtime or dashboard code in this audit lane.
- Staging third-party clone contents.
- Treating Docker CLI presence as daemon readiness.

## Fast Finish Recommendation

Fastest safe path:

1. User manually launches Docker Desktop and completes WSL2 setup.
2. Claude verifies daemon + WSL.
3. Claude pins image digest and requests exact approval.
4. Claude creates ActionIntent and requests exact payload approval.
5. Only then run one screenshot-only smoke.

Fallback if Docker remains blocked:

1. Continue Screenpipe read-only status/dashboard visibility.
2. Continue Obsidian vault token-saving workflow.
3. Keep AutoBrowser/Obscura as research only.
4. Do not jump to browser/desktop automation as a workaround.

## Risk List

- Docker daemon/background services.
- WSL2 install/reboot complexity.
- Image supply chain.
- Mutable `latest` tag.
- Screenshot privacy.
- Accidental click/type escalation.
- Host mounts or privileged containers.
- Live account exposure.
- Adapter promotion too early.
- Runtime drift between plan and approval payload.

## Recommended Next Claude Code Milestone

Current state says Docker remains blocked. Therefore:

```text
N+3.10a Docker Desktop manual launch / reboot verification
```

If the operator launches Docker Desktop and WSL2 completes before Claude starts, then switch to:

```text
N+3.11 image digest pin + ActionIntent smoke gate
```

## Runtime Wiring Truth

This Codex audit does not wire CUA, start capture, run Docker, run containers, execute screenshots, click/type, browse, or use live accounts.
