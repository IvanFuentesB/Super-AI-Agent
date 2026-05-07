# Codex CUA Docker / Ubuntu Path Review - N+3.6

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 2e9ffec
Status label: codex_review / cua_docker_ubuntu_path / inspect_only / not_runtime_wired

## Scope

This Codex lane inspected the already-cloned CUA repo at `21_repos/third_party/evals/cua`. No install, container run, CUA example run, screen capture, or runtime wiring occurred. Third-party contents were not staged.

## Clone Truth

| Field | Value |
|---|---|
| Path exists | YES |
| Path | `21_repos/third_party/evals/cua` |
| Git repo | YES |
| HEAD | `46dbcb47802e...` |
| Remote URL | `https://github.com/trycua/cua.git` |
| Runtime wired | NO |
| Third-party contents staged | NO |

HEAD and remote were read from `.git/HEAD`, `.git/refs/heads/main`, and `.git/config` directly. No nested repo Git mutation was performed.

## Key Files Found

| Item | Present | Notes |
|---|---:|---|
| `README.md` | YES | Describes Cua Driver, Cua sandbox, Cua Bench, and installation paths |
| `LICENSE.md` | YES | MIT license, copyright 2025 Cua AI, Inc. |
| `Dockerfile` | YES | Python 3.12 slim image for workspace/development build |
| `docker-compose.yml` | NO | No top-level compose file found |
| `compose.yaml` | NO | No top-level compose file found |
| `pyproject.toml` | YES | Python workspace; requires Python `>=3.12,<3.14`; deps include OpenAI/Anthropic |
| `package.json` | YES | Formatting/dev package file |
| `Makefile` | YES | Workspace build shortcuts |
| `libs/qemu-docker/linux` | implied by docs/listing | QEMU Docker Linux path exists in docs/source tree |
| `libs/kasm` | YES | Kasm/Ubuntu desktop container path |
| `examples/sandboxes/test_linux_local_container.py` | YES | Local Docker container example |
| Docker/Kasm docs | YES | Ubuntu Docker support and linux-container docs present |

## Docker / Ubuntu Path Findings

The cloned CUA docs/source show two relevant local Linux paths:

1. Lightweight Linux container path:
   - Docker-based.
   - Ubuntu/Xfce/KasmVNC style environment.
   - Exposes browser/VNC UI and computer-server API ports.
   - Does not require a cloud API key for local container examples.

2. QEMU Linux VM inside Docker:
   - Requires Linux host with KVM support.
   - Uses `--device=/dev/kvm` and `--cap-add NET_ADMIN` in docs.
   - Less suitable as the first Windows/Docker Desktop smoke because KVM availability under Windows/WSL is more complex.

The best first future path is the lightweight Docker/Kasm Ubuntu container path, not QEMU/KVM.

## API Keys

Current read-only finding:

- Local container sandbox examples do not require a CUA cloud key.
- Agent examples may require model provider keys depending on the loop.
- `pyproject.toml` includes OpenAI and Anthropic dependencies.
- Cloud container/VM docs mention `CUA_API_KEY`.

Ghoti first smoke should avoid agent/provider keys entirely. Use screenshot/observe only through local sandbox status or a dry-run adapter if CUA is not installed.

## Privileged Docker / Host Mounts

Read-only source findings:

- `cua_sandbox/runtime/docker.py` supports a `privileged` flag, but the constructor default is `False`.
- The Docker runtime supports volume mounts, devices, platform flags, and extra exposed ports.
- QEMU Linux docs require `/dev/kvm` device and `NET_ADMIN`.
- Kasm/Linux container docs show a simpler `docker run` with `--shm-size`, port mappings, and environment variable `VNCOPTIONS`, not full privileged mode.
- Kasm docs mention optional persistent/shared folder mount points.

Safety recommendation:

- First test must use no host mounts.
- First test must not use privileged mode.
- First test should avoid QEMU/KVM path.
- First test should expose only localhost ports needed for viewing/status.

## Local-Only Screenshot / Observe Feasibility

Feasible after Docker Desktop is installed and verified.

Likely local test shape:

- Pull or build approved Ubuntu/Kasm CUA image.
- Start container without host mounts.
- Open VNC/browser UI locally.
- Capture screenshot/observe of safe local container desktop or `example.com`.
- No click/type.
- No login.
- No provider keys.

Not feasible right now because:

- Docker CLI is absent.
- WSL reports not installed.
- No Docker daemon is reachable.

## Can It Be Tested With `example.com` Or A Local Static Page?

Yes, after Docker is approved and working.

Preferred first targets:

- a local static page served inside the test environment
- `example.com`

Avoid:

- real accounts
- login pages
- social sites
- banking/payment/trading
- private docs

## Recommended Future Command Sequence If Docker Is Approved Later

This is a future plan only. Do not run now.

1. Verify Docker:
   - `docker --version`
   - `docker compose version`
   - `docker info`
2. Verify WSL/backend:
   - `wsl --status`
3. Re-read CUA Docker docs and choose lightweight Linux container path.
4. Approve exact image pull/build command.
5. Run container with:
   - no host mounts
   - no privileged mode
   - localhost-only ports
   - no provider keys
6. Capture screenshot/observe only.
7. Write audit event.
8. Stop/remove container.
9. Confirm no screenshots/traces are staged.

## Verdict

CUA Docker/Ubuntu path is real in the cloned source and looks like the practical route for this Windows machine, but it is blocked on Docker Desktop/WSL installation. No install or runtime wiring should happen until the operator explicitly approves Docker.
