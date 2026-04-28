# Docker/WSL Ready Verification -- N+3.12

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.12
Starting HEAD: 0bb4d63

---

## Commands Run and Exact Outputs

### Docker CLI version (explicit path)

docker.exe --version -> Docker version 29.4.1, build 055a478

### Docker Compose version (explicit path)

docker-compose.exe version -> Docker Compose version v5.1.3

### Docker Desktop process

Get-Process 'Docker Desktop' -> 3 processes running:
  Docker Desktop  40512  28/04/2026 12:52:56 p.m.
  Docker Desktop  51752  28/04/2026 12:52:55 p.m.
  Docker Desktop  66980  28/04/2026 12:52:56 p.m.

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
  Version:    29.4.1
  Context:    desktop-linux

Server:
  Containers: 0 (Running: 0, Paused: 0, Stopped: 0)
  Images: 0
  Server Version: 29.4.1
  Storage Driver: overlayfs
  Cgroup Driver: cgroupfs / Cgroup Version: 2
  Kernel Version: (WSL2 kernel)
  Operating System: Docker Desktop
  OSType: linux
  Architecture: x86_64
  CPUs: 16
  Total Memory: ~15.27 GiB

---

## Verification Table

| Field | Value |
|---|---|
| Starting HEAD | 0bb4d63 |
| Docker CLI version | 29.4.1, build 055a478 |
| Docker Compose version | v5.1.3 |
| Docker Desktop process | RUNNING - 3 PIDs |
| Docker context | desktop-linux (active) |
| Docker daemon reachable | YES - Server section returned |
| Server Version | 29.4.1 |
| Architecture | x86_64 |
| CPUs | 16 |
| WSL default distribution | docker-desktop |
| WSL default version | 2 |
| docker-desktop WSL state | Running |
| WSL2 installed | YES |

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

**GO**

- docker_daemon_ready: YES
- docker_desktop_process_running: YES
- wsl2_installed: YES
- wsl_docker_desktop_running: YES
- docker_context: desktop-linux
- server_version: 29.4.1
- cpus: 16

---

## Safety Confirmations

- CUA container: NOT run
- Docker pull: NOT executed
- Docker build: NOT executed
- Runtime wiring: NOT changed
- Live accounts: NOT used
- Screenpipe capture: NOT started
- Click/type automation: NOT executed
