# Docker Desktop Install Verification — N+3.8

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.8

---

## Install Summary

| Field | Value |
|---|---|
| install attempted | YES |
| install command | `winget install --id Docker.DockerDesktop -e --accept-package-agreements --accept-source-agreements` |
| winget version | v1.28.240 |
| install result | Instalado correctamente (Installed successfully) |
| Docker Desktop version installed | 4.70.0 |
| admin/elevation needed | NO — winget handled install without UAC prompt in this shell |
| GUI/manual action needed | YES — Docker Desktop must be opened manually from Start menu to start daemon |
| reboot required | UNKNOWN — no reboot prompt was shown; a reboot may be needed if WSL2 install fails on first Docker Desktop launch |

---

## Docker CLI Truth

| Field | Value |
|---|---|
| Docker CLI path | `C:\Program Files\Docker\Docker\resources\bin\docker.exe` |
| Docker version | 29.4.0, build 9d7ad9f |
| Docker Compose path | `C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe` |
| Docker Compose version | v5.1.2 |
| Docker daemon reachable | NO — daemon not running; Docker Desktop not yet launched |
| Docker on bash PATH | NO — PATH not updated in current shell session; will be available after Docker Desktop is launched and in new shell sessions |

---

## Docker info result summary

Docker client info returned correctly (plugins, version, context). Server block returned error:

```
failed to connect to the docker API at npipe:////./pipe/docker_engine;
check if the path is correct and if the daemon is running:
open //./pipe/docker_engine: The system cannot find the file specified.
```

This is expected behavior when Docker Desktop has been installed but not yet launched.

---

## WSL Status Summary

| Field | Value |
|---|---|
| wsl.exe path | `C:\Windows\system32\wsl.exe` |
| WSL subsystem | NOT installed — "El Subsistema de Windows para Linux no está instalado" |
| WSL list | ERROR — subsystem not installed |
| Expected behavior | Docker Desktop will attempt to install WSL2 on first launch; a reboot may be required |

---

## Windows System Truth

| Field | Value |
|---|---|
| Windows edition | Windows 10 Home Single Language |
| Hypervisor | Detected — "Se detectó un hipervisor" |
| Virtualization | Available (Hyper-V/WSL2 path should be unlocked) |

---

## Docker Desktop Application

| Field | Value |
|---|---|
| Docker Desktop.exe | `C:\Program Files\Docker\Docker\Docker Desktop.exe` — EXISTS |
| Docker CLI executable | `C:\Program Files\Docker\Docker\resources\bin\docker.exe` — EXISTS |
| Docker Compose executable | `C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe` — EXISTS |

---

## Required Manual Action

**The operator must open Docker Desktop manually:**

1. Open Start menu → search "Docker Desktop" → launch it
2. Accept any WSL2 install prompts that appear on first launch
3. Wait for Docker Desktop to show "Docker is running" (green status in system tray)
4. If a reboot is required, reboot and relaunch Docker Desktop
5. After Docker is running: verify with `docker --version` and `docker info` in a new terminal

Docker Desktop will also install WSL2 on first launch if not already present.

---

## CUA Smoke Unlock Status

| Field | Value |
|---|---|
| Docker CLI installed | YES (not on PATH yet in current shell) |
| Docker daemon running | NO — requires manual Docker Desktop launch |
| WSL2 installed | NO — will be installed by Docker Desktop on first launch |
| CUA Docker smoke unlocked | PARTIAL — Docker installed but daemon not yet running; unlock completes after Docker Desktop is launched and daemon is verified |
| CUA container run | NO |
| Runtime wiring changed | NO |

---

## Strict Next Step

CUA screenshot-only smoke is the next milestone after the operator:
1. Launches Docker Desktop manually
2. Verifies `docker info` shows daemon running
3. Confirms WSL2 is installed (`wsl --status`)
4. Provides explicit approval for the CUA screenshot-only smoke (separate milestone)

---

## Explicit Safety Confirmations

- CUA container: NOT run in this milestone
- Runtime wiring: NOT changed in this milestone
- Live accounts: NOT used
- Screenpipe capture: NOT started
- Click/type automation: NOT executed
- Third-party repo contents: NOT staged
