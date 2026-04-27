# CUA Docker / Ubuntu Sandbox Path — N+3.6

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Status label: docker_path_plan / no_container_run / no_runtime_wiring

---

## Source Path

```
21_repos/third_party/evals/cua
```

---

## Source Truth

| Field | Value |
|---|---|
| Path exists | YES |
| Git repo | YES |
| HEAD hash | `46dbcb47802e2c712c87e9a34d4d5b06829a2932` |
| Remote URL | `https://github.com/trycua/cua.git` |
| License | MIT (trycua/cua — Cua AI, Inc. 2025) |
| CUA runtime wired | NO |
| Third-party contents staged | NO |

---

## Docker / Ubuntu Path Discovered in Repo

The cloned CUA source includes two Linux local container paths:

### 1. Lightweight Kasm/Ubuntu Docker Container (preferred first path)

- Lives under `libs/kasm` in the clone.
- Runs an Ubuntu + Xfce desktop environment inside Docker.
- Uses KasmVNC to expose a browser-accessible desktop UI.
- Exposes computer-server API on a local port.
- Does not require KVM, privileged mode, or cloud API key for local screenshot-only smoke.
- `examples/sandboxes/test_linux_local_container.py` demonstrates local usage.

### 2. QEMU Linux VM Inside Docker (not suitable for first Windows smoke)

- Uses `--device=/dev/kvm` and `--cap-add NET_ADMIN`.
- Requires Linux host with KVM support.
- Less suitable for first Windows/Docker Desktop smoke because KVM availability under WSL2 is more complex and machine-specific.

**The best first future path is the Kasm/Ubuntu lightweight container, not QEMU/KVM.**

---

## Why This May Be the Best Windows 11 Home Path

- Windows Sandbox requires Pro/Enterprise — blocked on this machine.
- Cua Driver (macOS Lume layer) requires Apple Silicon — blocked on this machine.
- Docker Desktop on Windows 11 Home runs Linux containers via WSL2 backend.
- The Kasm/Ubuntu path is explicitly designed for cross-platform Docker use.
- Local computer-server API is exposed only on localhost ports — no public exposure.
- Screenshot and observe do not require credentials or live accounts.

---

## Current Blockers

| Blocker | Status |
|---|---|
| Docker not installed | BLOCKED |
| WSL subsystem not installed | BLOCKED |
| No Docker daemon reachable | BLOCKED |
| No operator approval for Docker install | BLOCKED |

No CUA container run is possible until these are resolved.

---

## Future Smoke Test Plan (After Docker Approval)

**DO NOT RUN YET. These are future command placeholders only.**

### Step 1 — Verify Docker after install

```bash
# DO NOT RUN YET
docker --version
docker compose version
docker info
wsl --status
```

### Step 2 — Re-read CUA Docker docs

Read `21_repos/third_party/evals/cua/libs/kasm/README.md` and any updated Docker instructions to confirm exact image name and startup command.

### Step 3 — Approve exact image pull

Operator must approve the specific image and tag before any `docker pull` or `docker build`.

### Step 4 — Run isolated container (no host mounts, localhost only)

```bash
# DO NOT RUN YET — example shape only
docker run --rm \
  --name cua-smoke-test \
  --shm-size=512m \
  -p 127.0.0.1:6901:6901 \
  <approved-kasm-image>:<approved-tag>
```

Constraints:
- No `--privileged` flag.
- No `-v` host mounts.
- Ports bound to `127.0.0.1` only (localhost).
- No provider API keys in environment.

### Step 5 — Screenshot / observe only

- Open `http://localhost:6901` in local browser.
- Screenshot the container desktop or navigate to `example.com` inside container.
- No click, no type, no login, no real account.

### Step 6 — Write audit log

```python
# DO NOT RUN YET
# Write one audit entry to 05_logs/cua_action_audit.jsonl per action
```

### Step 7 — Shut down container

```bash
# DO NOT RUN YET
docker stop cua-smoke-test
docker rm cua-smoke-test
```

### Step 8 — Confirm no screenshots staged

Confirm no screenshot files are under git-tracked paths or staged.

---

## Forbidden in All Future CUA Tests

- Live accounts, real credentials, banking, email, social, 2FA screens
- Typing or clicking in first smoke test
- Stealth or anti-bot bypass
- Scraping third-party sites with real data
- Broad host directory mounts
- Privileged container mode (without explicit second approval)
- Any CUA action without a pre-approved ActionIntent in the approval inbox
- Any action without an audit log entry
