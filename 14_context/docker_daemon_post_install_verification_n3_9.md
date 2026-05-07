# Docker Daemon Post-Install Verification — N+3.9

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.9
Starting HEAD (original run): 45335fa
Re-verified at HEAD: 9850c46 (2026-04-27 re-run)

---

## Summary

Docker Desktop is installed but the daemon is **not running**. WSL2 is **not installed**.  
CUA smoke is **blocked** until the operator manually launches Docker Desktop and daemon starts.

---

## Commands Run and Exact Outputs

### Docker CLI version (explicit path)

```
powershell.exe -NoProfile -Command "& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' --version"
→ Docker version 29.4.0, build 9d7ad9f
```

### Docker Compose version (explicit path)

```
powershell.exe -NoProfile -Command "& 'C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe' version"
→ Docker Compose version v5.1.2
```

### Docker info (explicit path)

```
powershell.exe -NoProfile -Command "& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' info"

Client: OK (version 29.4.0; plugins: agent, ai, buildx, compose, debug, desktop, dhi, extension, init, mcp, model, offload, pass, sandbox, sbom, scout)

Server:
failed to connect to the docker API at npipe:////./pipe/docker_engine;
check if the path is correct and if the daemon is running:
open //./pipe/docker_engine: The system cannot find the file specified.
```

### Docker Desktop process check

```
powershell.exe -NoProfile -Command "Get-Process 'Docker Desktop' -ErrorAction SilentlyContinue | Select-Object ProcessName,Id,StartTime"
→ (empty — Docker Desktop process is NOT running)
```

### Docker Desktop install path check

```
powershell.exe -NoProfile -Command "Test-Path 'C:\Program Files\Docker\Docker\Docker Desktop.exe'"
→ True
```

### WSL status

```
wsl --status
→ Exit code 50
→ El Subsistema de Windows para Linux no está instalado. Para instalar, ejecute "wsl.exe --install".
```

---

## Verification Table

| Field | Value |
|---|---|
| Starting HEAD (original run) | 45335fa |
| Re-verified HEAD | 9850c46 |
| Docker CLI path | `C:\Program Files\Docker\Docker\resources\bin\docker.exe` |
| Docker CLI version | 29.4.0, build 9d7ad9f |
| Docker Compose path | `C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe` |
| Docker Compose version | v5.1.2 |
| Docker Desktop.exe | EXISTS — `C:\Program Files\Docker\Docker\Docker Desktop.exe` |
| Docker Desktop process | NOT RUNNING — Get-Process returned empty |
| Docker daemon reachable | NO — npipe://./pipe/docker_engine not found |
| WSL2 installed | NO — subsystem not installed |
| WSL2 status | Exit code 50; subsystem install required |
| Reboot required | UNKNOWN — no reboot prompt shown; may be required after Docker Desktop first launch installs WSL2 |
| Manual launch required | YES — operator must open Docker Desktop from Start menu |
| CUA smoke unlocked | NO — blocked until daemon running and WSL2 installed |

---

## Interpretation

Docker Desktop 4.70.0 was installed via winget in N+3.8. The CLI is present and returns correct version output. However:

- **Docker Desktop has not been launched yet** since install — daemon pipe does not exist.
- **WSL2 is not installed** — Docker Desktop will attempt to install it on first launch; a reboot may be required.
- The daemon unreachable error is expected before the first Docker Desktop GUI launch.

This is not an install failure. It is the normal state before first launch.

---

## Required Manual Operator Actions

1. Open Start menu → search "Docker Desktop" → click to launch
2. Accept any WSL2 install prompts that appear on first launch
3. Wait for Docker Desktop to show "Docker is running" (green icon in system tray)
4. If a reboot is required: reboot, then relaunch Docker Desktop
5. After daemon running: verify in a **new** terminal:
   - `docker --version`
   - `docker info` — must show Server section with daemon details
   - `wsl --status` — must show WSL default version 2 or installed state

---

## CUA Smoke Unlock Status

| Precondition | Status |
|---|---|
| Docker CLI installed | YES |
| Docker Desktop installed | YES |
| Docker daemon running | NO — manual launch required |
| WSL2 installed | NO — first Docker Desktop launch installs it |
| CUA smoke approved separately | NO — separate approval required |
| CUA smoke unlocked | BLOCKED |

---

## Explicit Safety Confirmations

- CUA container: NOT run
- Docker build: NOT run
- Docker pull: NOT run
- Runtime wiring: NOT changed
- Live accounts: NOT used
- Screenpipe capture: NOT started
- Click/type automation: NOT executed
- Third-party repo contents: NOT staged
- Prompt files: NOT staged

---

## Final Verdict

**`docker_installed_daemon_not_running` + `wsl_setup_required`**

CUA smoke plan exists but is blocked. No container work may proceed until:
1. Docker Desktop is launched manually
2. Daemon pipe is confirmed reachable (`docker info` shows server section)
3. WSL2 is confirmed installed (`wsl --status` returns success)
4. Operator provides separate explicit approval for CUA screenshot-only smoke
