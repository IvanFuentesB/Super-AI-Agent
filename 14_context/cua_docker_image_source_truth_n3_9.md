# CUA Docker Image / Source Truth — N+3.9

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.9
Status: source_inspected / no_build / no_pull / no_execution / blocked_until_daemon_running

---

## CUA Repo Identity

| Field | Value |
|---|---|
| CUA repo path | `21_repos/third_party/evals/cua` |
| CUA HEAD hash | `46dbcb47802e2c712c87e9a34d4d5b06829a2932` |
| Remote URL | `https://github.com/trycua/cua.git` |
| License | MIT (Cua AI, Inc. 2025) |
| Clone depth | 1 (shallow) |

---

## Files Inspected (Read-Only)

| File | Purpose |
|---|---|
| `libs/kasm/Dockerfile` | Primary Docker image definition for Ubuntu/Kasm path |
| `libs/kasm/README.md` | Kasm container documentation pointer |
| `Dockerfile` (root) | Python/ARM-oriented image — references lume (macOS only) |
| `blog/ubuntu-docker-support.md` | Official blog describing Kasm/Ubuntu Docker path |
| `14_context/cua_trycua_isolated_clone_audit_n3_5.md` | Prior clone inspection results |
| `14_context/cua_docker_ubuntu_sandbox_path_n3_6.md` | Prior Windows Docker path analysis |

---

## Recommended Docker Path for Windows

### Image

| Field | Value |
|---|---|
| Pre-built image | `trycua/cua-ubuntu:latest` (Docker Hub) |
| Base | `kasmweb/core-ubuntu-jammy:1.17.0` |
| Desktop environment | Ubuntu 22.04 (Jammy) + Xfce + KasmVNC |
| Web viewer port | `8006` (per blog) / `6901` (Kasm VNC default) |
| Computer server | boots automatically on startup |

### Pull Command (NOT to be run until daemon is running and image is approved)

```bash
# DO NOT RUN YET — daemon not running, image not approved
docker pull --platform=linux/amd64 trycua/cua-ubuntu:latest
```

### Minimum Safe Run Shape (NOT to be run — plan only)

```bash
# DO NOT RUN YET — plan only; daemon not running; no CUA smoke approval
docker run --rm \
  --name cua-smoke-01 \
  --shm-size=512m \
  -p 127.0.0.1:6901:6901 \
  trycua/cua-ubuntu:latest
```

### Local Build Alternative (NOT recommended for first smoke)

```bash
# DO NOT RUN YET — requires Docker daemon, separate approval for image tag
cd 21_repos/third_party/evals/cua/libs/kasm
docker build -t cua-ubuntu:local .
```

---

## Safety Inspection Results

| Safety Check | Result |
|---|---|
| Privileged mode required | NO — Dockerfile does not use `--privileged`; Kasm desktop runs as non-root user 1000 |
| Broad host mounts required | NO — basic run does not require `-v` mounts |
| KVM/nested virt required | NO — Kasm/VNC path avoids KVM (explicitly documented in blog) |
| Network required (pull) | YES — Docker Hub pull requires internet access; must be explicitly approved before any pull |
| Network required (runtime) | MINIMAL — container serves localhost VNC only; no external network needed for screenshot smoke |
| Port exposure | `6901` (or `8006`) bound to `127.0.0.1` only — localhost only |
| Browser/VNC opened | YES — desktop served at `http://localhost:6901` in browser; screenshot smoke views only |
| API keys required | NO — screenshot/observe mode does not require LLM API keys |
| Live accounts required | NO — local desktop, no credentials |
| Agent auto-actions | NO — screenshot-only smoke disables click/type at ActionIntent level |
| Supply chain risk | MEDIUM — `trycua/cua-ubuntu:latest` is an official project image; should be pinned to a specific digest before any smoke run |

---

## Source Language Summary

| Layer | Language |
|---|---|
| Kasm base | Ubuntu 22.04 + Xfce (Docker container) |
| Computer server | Python 3.12 (cua-computer-server package) |
| Agent layer | Python 3.12 (cua-agent package) |
| Web VNC layer | KasmVNC (C++/JavaScript — embedded in base image) |
| Browser inside container | Firefox (installed by Dockerfile) |
| Root Dockerfile | Python 3.12-slim + lume reference (macOS only, not for Windows) |

---

## What Must Change Before Safe Smoke Use

| Requirement | Status |
|---|---|
| Docker daemon must be running | NOT MET — daemon not running; operator must launch Docker Desktop |
| WSL2 must be installed | NOT MET — will install on first Docker Desktop launch |
| Image tag must be pinned to exact digest | NOT MET — `latest` tag must be resolved to `sha256:...` and approved before pull |
| Separate operator approval for CUA smoke | NOT MET — no smoke approval present in this milestone |
| ActionIntent created with exact payload | NOT MET — plan only; no ActionIntent created yet |
| Payload hash computed | NOT MET — requires ActionIntent to exist first |
| Audit log pre-created | NOT MET — will be created at smoke execution time |

---

## Final Verdict

**`blocked_until_docker_daemon_running`**

The Kasm/Ubuntu image and run shape are safe for a screenshot-only smoke given:
- No privileged mode
- No host mounts
- Localhost-only port exposure
- Non-root container user

However, the smoke cannot proceed until Docker daemon is running, WSL2 is installed, the image tag is pinned and approved, and a separate explicit smoke approval is obtained.
