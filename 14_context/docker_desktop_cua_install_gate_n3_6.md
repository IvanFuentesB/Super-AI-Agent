# Docker Desktop CUA Install Gate — N+3.6

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Status label: install_gate / operator_approval_required / not_installed / not_runtime_wired

---

## Current Blocker Truth

| Check | Result |
|---|---|
| `docker --version` | FAIL — docker not found on PATH |
| `docker compose version` | FAIL — docker not found on PATH |
| `docker info` | FAIL — docker not found on PATH |
| WSL status | WSL executable present at `C:\Windows\system32\wsl.exe`; subsystem not installed |
| Windows edition | Windows 11 Home Single Language |
| Windows Sandbox | BLOCKED — requires Windows Pro or Enterprise |
| CUA macOS (Lume/Apple Virtualization) | BLOCKED — macOS/Apple Silicon only |
| Hypervisor present | True (WSL2/Docker Desktop could use it if installed) |
| Docker daemon reachable | NO |

All local CUA execution paths are currently blocked on this machine.

---

## Why Docker Desktop Is the Practical Unlocker

1. The canonical CUA repo (`github.com/trycua/cua`) includes a Docker/Ubuntu/Kasm path that works cross-platform when Docker is available.
2. The macOS Cua Driver path (Lume/Apple Virtualization) requires Apple Silicon — not applicable here.
3. Windows Sandbox (native container sandbox) requires Windows Pro or Enterprise — this host is Home edition.
4. Docker Desktop on Windows 11 Home can run Linux containers via WSL2 backend.
5. The Kasm/Ubuntu lightweight container path in the CUA clone (`libs/kasm`) does not require KVM or privileged mode for its first smoke test.
6. Docker Desktop also unblocks AutoBrowser Docker Compose path for future milestones.

---

## Approval Required

To proceed with Docker Desktop install, the operator must type exactly:

```
APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX
```

Do not install Docker Desktop without this explicit approval.

---

## What Happens Only After Approval

1. Install Docker Desktop (admin install on Windows 11 Home).
2. Verify `docker --version`, `docker compose version`, `docker info`.
3. Verify WSL2 backend is active: `wsl --status`.
4. Inspect Docker Desktop settings — confirm resource limits and no unexpected shared drives.
5. Do NOT run any CUA container yet.
6. Report Docker/WSL truth and update wait/resume items.
7. Only after Docker is verified: request CUA sandbox profile approval and plan screenshot-only smoke.

---

## Risk Table

| Risk | Why it matters | Required control |
|---|---|---|
| Admin install | Docker Desktop requires elevated installer and system changes | explicit operator approval before install |
| Virtualization / WSL2 backend | Enables new subsystem; may require reboot | document machine state before and after |
| Background services | Docker Desktop runs daemon and services at login | check services after install; confirm stop instructions |
| Network access | Image pulls contact Docker Hub and other registries | approve exact image/tag before any pull |
| Disk usage | Images and containers consume GBs of space | check free disk before pull; set cleanup plan |
| Container permissions | Containers can mount host dirs or expose ports | no host mounts by default; localhost-only ports |
| Supply chain | Images may include unknown packages | prefer official or source-reviewed images only |
| Data leakage | Screenshots and logs may contain sensitive content | sandbox-only; no live accounts; 3-day retention |

---

## Non-Negotiable Constraints After Docker Install

- No live accounts in any container.
- No click/type actions in first smoke test.
- Screenshot and observe only for the first CUA test.
- ActionIntent gate required before every future CUA action.
- Audit event written to `05_logs/cua_action_audit.jsonl` per action.
- Screenshot and capture retention capped at 3 days per `23_configs/cua_sandbox_profile.example.json`.
- No privileged mode containers without explicit second approval.
- No broad host directory mounts.

---

## Final Verdict

Docker Desktop install gate is the recommended next step if the operator wants the fastest path toward autonomous computer use on this Windows 11 Home machine.

The gate must not be crossed until the operator provides explicit approval:

```
APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX
```

If the operator prefers to avoid installs, the alternative is the Screenpipe dashboard route and Obsidian vault sync — see `14_context/n3_6_execution_decision.md`.
