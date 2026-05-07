# N+3.9 Codex Next Execution Review

Status: codex_execution_review / docker_blocked / no_runtime_changes / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack

## What Claude Should Do Next

Because Docker CLI binaries exist but the daemon and WSL are not ready, Claude should not run CUA yet.

Recommended next Claude milestone:

```text
N+3.9a Docker Desktop post-launch/reboot verification
```

Claude should:

1. Ask the operator to manually launch Docker Desktop.
2. Wait for Docker Desktop first-run/WSL prompts to complete.
3. Reboot only if Docker Desktop or WSL asks for it and the operator agrees.
4. Re-run:

```powershell
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' --version
& 'C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe' version
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' info
wsl --status
wsl --list --verbose
Get-Process 'Docker Desktop' -ErrorAction SilentlyContinue
```

5. Stop after verification.
6. Do not run containers in the post-launch verification milestone.

## What Codex Should Avoid

- Installing Docker/WSL.
- Running Docker containers.
- Running CUA examples.
- Running screen capture.
- Editing runtime/dashboard files in the parallel lane.
- Staging third-party repo contents.
- Treating Docker CLI presence as daemon readiness.

## If Daemon Becomes Ready

Recommended next milestone:

```text
N+4.0 CUA screenshot-only smoke
```

Requirements:

- Exact image/tag or build path approval.
- One screenshot-only ActionIntent.
- One operator approval tied to payload hash.
- One audit trail.
- Output under `05_logs/cua_smoke_runs/<run_id>/`.
- No click/type.

## If Daemon Is Not Ready

Recommended next milestone:

```text
N+3.9a Docker Desktop post-launch/reboot verification
```

If Docker Desktop cannot complete WSL setup, continue with safer no-install work:

- Screenpipe status UI card.
- Obsidian vault sync workflow.
- Wait/resume dashboard visibility.
- AutoBrowser/CUA docs-only planning.

## Exact User Approval Needed Next

Before any future CUA pull/build/run:

```text
APPROVE CUA SCREENSHOT-ONLY SMOKE WITH EXACT IMAGE/TAG
```

The actual image/tag or build path must be included with the approval request. This approval should not include click/type, live accounts, broad host mounts, privileged containers, or external automation.

## Runtime Wiring Truth

This Codex N+3.9 audit added no runtime wiring. It did not install anything, run Docker, build images, run containers, execute CUA, start capture, browse, click, type, or use live accounts.
