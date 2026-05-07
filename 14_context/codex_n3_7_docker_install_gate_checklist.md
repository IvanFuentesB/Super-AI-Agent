# N+3.7 Codex Docker/CUA Install Gate Checklist

Status: codex_audit / docker_install_gate / no_install / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Observed local/origin HEAD: b902dca

## Current Tool Truth

| Check | Result |
| --- | --- |
| Docker CLI | Not available from this shell. |
| Docker Compose | Not available from this shell. |
| WSL | Not installed. |
| Windows edition | Windows 10 Home Single Language, WindowsVersion 2009, OS HAL 10.0.26100.1. |
| CUA runtime | Not installed, not run, not wired. |

No Docker install, WSL install, CUA container run, or CUA execution was performed in this audit.

## Why Docker Desktop Is The Practical CUA Unlocker

CUA/TryCUA is still the strongest long-term sandbox-first computer-use direction, but the Windows path needs an isolated runtime before any smoke test. The prior CUA notes point toward Docker/Ubuntu/Kasm-style paths, while native Cua Driver support is not proven for this Windows host. Windows Home also makes Windows Sandbox an unreliable default path.

Docker Desktop is therefore the practical unlocker only if the operator explicitly approves the admin/system change. It should be treated as an install gate, not a background setup step.

## Approval Phrase

The operator must explicitly approve this exact phrase before any install work:

```text
APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX
```

Approval for Docker install is not approval to run CUA, click, type, mount host folders, connect live accounts, or start background autonomy.

## Risks To Review Before Approval

| Risk | Why It Matters | Required Control |
| --- | --- | --- |
| Admin install | Docker Desktop changes system services and virtualization settings. | Operator approval and manual awareness. |
| WSL2 backend | May install or enable WSL components. | Verify WSL status before and after. |
| Reboot required | Install may interrupt current work. | Schedule when safe. |
| Background services | Docker can run services after login. | Disable/limit as operator prefers. |
| Disk usage | Images/containers can grow quickly. | Inspect images/containers before cleanup. |
| Network access | Containers can reach network by default. | First tests must be local/sandbox-only. |
| Container permissions | Privileged containers or broad mounts increase risk. | Forbid privileged mode and host mounts initially. |

## Rollback Plan

1. Record pre-install Docker/WSL state.
2. If Docker Desktop causes issues, uninstall it through Windows Apps settings.
3. Run `wsl --shutdown` after uninstall if WSL was enabled.
4. Remove Docker images/containers only after listing them and confirming they are Docker artifacts.
5. Do not delete Ghoti repo files, third-party clones, runtime data, or screenshots as part of rollback.

## Forbidden Actions Until Separately Approved

- No CUA container run.
- No Docker image pull/build/run.
- No click/type automation.
- No live accounts.
- No passwords, 2FA, banking, email, social, trading, payment, or private document targets.
- No host filesystem mounts.
- No privileged container.
- No stealth/evasion behavior.
- No autonomous loop.
- No runtime wiring into Ghoti.

## Verdict

Docker Desktop is likely the necessary CUA unlock on this Windows host, but only after explicit operator approval. If Docker approval is not given, the safer near-term path is Screenpipe status visibility plus Obsidian vault sync, because both can improve observability and token efficiency without installs.
