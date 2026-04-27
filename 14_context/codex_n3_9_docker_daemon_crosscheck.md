# N+3.9 Codex Docker Daemon Crosscheck

Status: codex_crosscheck / daemon_verification / no_container_run / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting local HEAD observed: 45335fa
Origin HEAD observed before this Codex commit: 88f0368

## Repo/Branch Truth

Local branch was `feat/ghoti-visible-operator-stack`.

Local HEAD included Claude N+3.8:

```text
45335fa feat/ghoti milestone N+3.8 — verify Docker Desktop gate for CUA sandbox
```

Origin was still at Codex N+3.8 before this commit:

```text
88f0368 docs/analysis milestone N+3.8 — crosscheck Docker CUA install gate
```

No staged files were present before this Codex audit.

## Docker CLI Truth

| Check | Result |
| --- | --- |
| `docker --version` | FAIL: `docker` is not on PATH in this shell. |
| Explicit path `C:\Program Files\Docker\Docker\resources\bin\docker.exe --version` | PASS: Docker version 29.4.0, build 9d7ad9f. |
| `docker compose version` | FAIL: `docker` is not on PATH in this shell. |
| Explicit path `C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe version` | PASS: Docker Compose version v5.1.2. |

Docker CLI binaries exist, but PATH for this shell has not picked up Docker.

## Docker Daemon Truth

Explicit path `docker.exe info` returned client/plugin details but failed in the server block:

```text
failed to connect to the docker API at npipe:////./pipe/docker_engine;
check if the path is correct and if the daemon is running:
open //./pipe/docker_engine: The system cannot find the file specified.
```

Verdict: Docker daemon running = NO.

## WSL Truth

| Check | Result |
| --- | --- |
| `wsl --status` | FAIL: Windows Subsystem for Linux is not installed. |
| `wsl --list --verbose` | FAIL: Windows Subsystem for Linux is not installed. |

Verdict: WSL installed = NO.

## Docker Desktop Process Truth

`Get-Process 'Docker Desktop'` returned no process rows.

Verdict: Docker Desktop process running = NO.

## Current Unlock State

| Gate | State |
| --- | --- |
| Docker Desktop installed | YES, based on explicit CLI path and Claude N+3.8 install verification. |
| Docker CLI available on current PATH | NO. |
| Docker daemon reachable | NO. |
| WSL installed/usable | NO. |
| Docker Desktop running | NO. |
| CUA screenshot smoke unlocked | NO-GO. |

## Manual Action Still Needed

The operator likely still needs to:

1. Launch Docker Desktop from the Start menu.
2. Accept any first-run prompts.
3. Allow WSL2 setup if prompted.
4. Reboot if Docker Desktop or WSL asks for it.
5. Open a new shell and verify Docker/WSL again.

## What Codex Did Not Do

- No install.
- No Docker container run.
- No Docker image pull/build.
- No CUA execution.
- No screen capture.
- No runtime wiring.
- No third-party repo staging.

## Verdict

CUA screenshot-only smoke is still blocked. Docker Desktop appears installed, but the daemon is not running, Docker is not on PATH in this shell, Docker Desktop is not running as a process, and WSL is not installed.
