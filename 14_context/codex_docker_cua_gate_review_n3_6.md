# Codex Docker / CUA Gate Review - N+3.6

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 2e9ffec
Status label: codex_review / docker_gate / no_install / not_runtime_wired

## Scope

This Codex lane reviewed whether Docker Desktop is the next practical unlocker for CUA/TryCUA on this Windows machine. No install, Docker run, CUA run, Screenpipe run, capture, or runtime wiring occurred.

## Current Docker Truth

Commands run:

- `docker --version`
- `docker compose version`
- `docker info`
- `wsl --status`
- `Get-Command docker`
- `Get-Command wsl`
- `Get-ComputerInfo | Select-Object WindowsProductName,WindowsVersion,OsHardwareAbstractionLayer,HyperVisorPresent`

Observed results:

| Check | Result |
|---|---|
| `docker --version` | FAIL: `docker` is not recognized |
| `docker compose version` | FAIL: `docker` is not recognized |
| `docker info` | FAIL: `docker` is not recognized |
| `Get-Command docker` | no command found |
| `Get-Command wsl` | `C:\Windows\system32\wsl.exe` exists |
| `wsl --status` | reports Windows Subsystem for Linux is not installed |
| Windows product | `Windows 10 Home Single Language` |
| Hypervisor present | `True` |
| Optional feature query | attempted, but requires elevation |

Interpretation:

- Docker Desktop is not installed or not on PATH.
- WSL executable exists, but WSL itself reports not installed.
- The machine is a Home edition Windows install, which aligns with prior docs that Windows Sandbox is blocked for this host class.
- Hypervisor presence alone does not mean Docker/WSL is ready.

## Is Docker Desktop Needed?

Yes, Docker Desktop appears to be the practical local unlocker for CUA on this machine.

Reasons:

- Cua Driver itself is macOS-focused and not applicable to this Windows host.
- Windows Sandbox path is blocked by Windows Home edition constraints.
- The CUA Linux local container path explicitly requires Docker.
- CUA docs and cloned source include Docker/Kasm/Ubuntu paths that are cross-platform when Docker is available.
- WSL is not currently installed, so Docker Desktop/WSL2 setup is a real prerequisite.

## Windows Sandbox Status

Current practical status: blocked/not usable for this lane.

Evidence:

- Prior CUA audit says Windows Sandbox requires Windows Pro/Enterprise.
- Current machine reports Windows Home edition.
- Optional-feature query could not be completed without elevation.

Do not plan the first CUA smoke around Windows Sandbox unless the operator upgrades/enables the required Windows edition/features later.

## Operator Approval Required Before Docker Install

Recommended approval phrase:

`APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX`

Operator must approve:

- Docker Desktop install.
- WSL2/backend enablement.
- Any reboot required.
- Disk usage for images.
- Network access for Docker image pulls.
- Any future `docker pull`, `docker build`, or `docker run`.
- Any container port exposure.
- Any mounted host directories.

## What Must Not Happen Automatically

- No Docker Desktop install without explicit approval.
- No WSL install without explicit approval.
- No Docker image pull.
- No Docker build.
- No Docker run.
- No CUA container start.
- No CUA agent/example run.
- No host filesystem mount.
- No live account access.
- No click/type automation.
- No screenshot/capture start.

## Risk Table

| Risk | Why it matters | Required control |
|---|---|---|
| Admin install | Docker Desktop may require elevated installer and system changes | explicit operator approval |
| Virtualization / WSL2 backend | Enables a new subsystem and may require reboot | document state before/after |
| Network access | Image pulls contact registries | approve exact images first |
| Disk usage | Images/containers can consume GBs | set cleanup plan and check free disk |
| Background services | Docker Desktop runs daemon/services | visible status and stop instructions |
| Container permissions | Containers may mount host dirs or expose ports | no mounts by default; localhost-only ports |
| Supply chain | Images may include unknown packages | prefer official/source-reviewed images |
| Data leakage | Screenshots/logs may contain sensitive data | sandbox-only, no live accounts, retention limits |

## Final Verdict

Docker Desktop install gate is reasonable only after explicit operator approval.

Recommended next if speed toward CUA is the priority: request `APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX`, then install Docker Desktop and validate Docker/WSL readiness before any CUA container run.

Recommended next if avoiding installs: implement the Screenpipe read-only retention/status route or Obsidian vault sync first.
