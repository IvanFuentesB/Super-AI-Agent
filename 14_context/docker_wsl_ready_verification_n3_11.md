# Docker/WSL Ready Verification -- N+3.11

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.11
Starting HEAD: b63cc52

---

## Commands Run and Exact Outputs

### Test-Path checks

Test-Path C:\Program Files\Docker\Docker\resources\bin\docker.exe        -> True
Test-Path C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe -> True
Test-Path C:\Program Files\Docker\Docker\Docker Desktop.exe              -> True

### Docker CLI version (explicit path)

docker.exe --version -> Docker version 29.4.0, build 9d7ad9f

### Docker Compose version (explicit path)

docker-compose.exe version -> Docker Compose version v5.1.2

### Docker Desktop process

Get-Process 'Docker Desktop' -> 4 processes running:
  Docker Desktop  39312  28/04/2026 12:14:49 p.m.
  Docker Desktop  39852  28/04/2026 12:14:50 p.m.
  Docker Desktop  57560  28/04/2026 12:15:55 p.m.
  Docker Desktop  63028  28/04/2026 12:14:50 p.m.

### WSL status

wsl --status
-> Default distribution: docker-desktop
-> Default version: 2
-> WSL 1 not compatible with current machine configuration.

### WSL list --verbose

wsl --list --verbose
-> NAME                  STATE    VERSION
-> * docker-desktop      Running  2

### Docker context

docker context ls
-> NAME              DESCRIPTION             DOCKER ENDPOINT
-> default           DOCKER_HOST based       npipe:////./pipe/docker_engine
-> desktop-linux *   Docker Desktop          npipe:////./pipe/dockerDesktopLinuxEngine

Active context: desktop-linux (*)

### Docker info (server section confirmed)

Client:
  Version:    29.4.0
  Context:    desktop-linux

Server:
  Containers: 0 (Running: 0, Paused: 0, Stopped: 0)
  Images: 0
  Server Version: 29.4.0
  Storage Driver: overlayfs
  Cgroup Driver: cgroupfs / Cgroup Version: 2
  Kernel Version: 6.6.87.2-microsoft-standard-WSL2
  Operating System: Docker Desktop
  OSType: linux
  Architecture: x86_64
  CPUs: 16
  Total Memory: 15.27GiB
  Name: docker-desktop
  ID: 31ce13fe-e301-4d80-b9b7-41fffe399907

---

## Verification Table

| Field | Value |
|---|---|
| Starting HEAD | b63cc52 |
| Docker CLI version | 29.4.0, build 9d7ad9f |
| Docker Compose version | v5.1.2 |
| Docker Desktop.exe | EXISTS |
| Docker Desktop process | RUNNING - 4 PIDs |
| Docker context | desktop-linux (active) |
| Docker daemon reachable | YES - Server section returned |
| Server Version | 29.4.0 |
| Architecture | x86_64 |
| CPUs | 16 |
| Total Memory | 15.27 GiB |
| WSL default distribution | docker-desktop |
| WSL default version | 2 |
| docker-desktop WSL state | Running |
| WSL2 installed | YES |
| Kernel | 6.6.87.2-microsoft-standard-WSL2 |

---

## Success Criteria Check

| Criterion | Result |
|---|---|
| Docker Desktop process running | PASS |
| wsl --list --verbose includes docker-desktop Running 2 | PASS |
| docker info via explicit path includes Server: section | PASS |
| Docker context is desktop-linux | PASS |

---

## Final Verdict

**docker_wsl_ready**

- docker_daemon_ready: YES
- docker_desktop_process_running: YES
- wsl2_installed: YES
- wsl_docker_desktop_running: YES
- docker_context: desktop-linux
- server_version: 29.4.0
- cpus: 16
- memory_gib: 15.27

---

## Safety Confirmations

- CUA container: NOT run
- Docker pull: NOT executed
- Docker build: NOT executed
- Runtime wiring: NOT changed
- Live accounts: NOT used
- Screenpipe capture: NOT started
- Click/type automation: NOT executed
