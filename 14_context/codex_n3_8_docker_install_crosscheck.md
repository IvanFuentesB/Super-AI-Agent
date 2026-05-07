# N+3.8 Codex Docker Install Crosscheck

Status: codex_crosscheck / install_gate_review / no_install / no_container_run / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting local HEAD observed: eee0cc0
Origin HEAD observed before this Codex commit: faff2b5

## Approval Truth

The operator approved the Docker gate with:

```text
APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX
```

That approval authorizes Claude Code to proceed with the Docker Desktop install gate. It does not authorize Codex to install anything in this parallel lane, and it does not authorize running CUA containers, clicking, typing, live accounts, privileged containers, broad host mounts, or background autonomy.

## Current Verification From This Shell

| Check | Result |
| --- | --- |
| `docker --version` | FAIL: `docker` is not recognized. |
| `docker compose version` | FAIL: `docker` is not recognized. |
| `wsl --status` | FAIL: WSL reports the subsystem is not installed. |
| `wsl --list --verbose` | FAIL: WSL reports the subsystem is not installed. |

Codex did not install Docker, install WSL, run containers, or run CUA.

## Why Docker Desktop Is The Practical Unlocker

Project docs identify the canonical CUA source as `https://github.com/trycua/cua` and the local clone as `21_repos/third_party/evals/cua`. On this Windows Home path:

- Cua Driver and Lume are macOS/Apple Silicon oriented.
- Windows Sandbox is not the reliable route on Home edition.
- The CUA Docker/Ubuntu/Kasm path is the most practical local sandbox path once Docker Desktop and WSL2 are available.
- Docker also helps future AutoBrowser-style Docker evaluation.

Docker Desktop is therefore a reasonable install gate, but only as a prerequisite. The first real CUA smoke must be a later, separately approved screenshot-only milestone.

## Commands Claude Should Run For Install Verification

After any GUI/admin installer and reboot/manual action completes, Claude should verify:

```powershell
docker --version
docker compose version
docker info
wsl --status
wsl --list --verbose
```

Useful optional checks:

```powershell
Get-Command docker
Get-Service *docker* -ErrorAction SilentlyContinue
```

## Outputs That Prove Docker Is Installed

Passing evidence should include:

- `docker --version` prints a Docker version.
- `docker compose version` prints a Compose version.
- `docker info` returns daemon details instead of connection errors.
- Docker Desktop is installed and reachable from PowerShell.

If `docker --version` works but `docker info` fails, Docker CLI exists but the daemon is not ready.

## Outputs That Prove WSL2 Is Usable

Passing evidence should include:

- `wsl --status` reports WSL default version 2 or usable WSL status.
- `wsl --list --verbose` shows at least one installed distribution or Docker-managed WSL integration where expected.
- Docker Desktop reports a WSL2 backend or an equivalent working Linux container backend.

## Outputs That Mean Manual GUI/Reboot Is Still Required

- `docker` command not recognized.
- `docker info` cannot connect to daemon.
- WSL says the subsystem is not installed.
- Docker Desktop installer asks for logout/reboot.
- Docker Desktop starts but says WSL update, virtualization, or backend setup is incomplete.
- Docker Desktop UI is waiting on license/terms/resources confirmation.

## What Claude Must Not Do After Install

- Do not run a CUA container in the install milestone.
- Do not pull/build Docker images without a separate image/tag approval.
- Do not run `docker run`.
- Do not mount host folders.
- Do not use privileged containers.
- Do not connect live accounts.
- Do not click/type in any sandbox.
- Do not start screen capture.
- Do not wire CUA into Ghoti runtime.

## Verdict

Docker install gate is acceptable because the user approved it, but only if the N+3.8 install milestone stops at Docker/WSL verification. The first CUA screenshot-only smoke should be N+3.9 or later after Docker is proven healthy.
