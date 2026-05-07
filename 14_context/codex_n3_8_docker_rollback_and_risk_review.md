# N+3.8 Codex Docker Rollback And Risk Review

Status: codex_risk_review / rollback_plan / no_install / no_container_run / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack

## Docker Desktop Install Risks

| Risk | Why It Matters | Mitigation |
| --- | --- | --- |
| Admin install | Docker Desktop changes system-level components. | Operator-approved install only. |
| WSL2 backend | WSL may be installed/enabled and may need reboot. | Verify `wsl --status` before and after. |
| Virtualization | Requires virtualization support and can affect system resources. | Check Docker Desktop resource settings after install. |
| Background services | Docker daemon/Desktop may start with Windows. | Disable autostart if the operator wants manual startup only. |
| Disk usage | Images, layers, volumes, and containers can consume GBs. | Run image/container listing before cleanup. |
| Network access | Containers can reach the network unless constrained. | First smoke should bind localhost only and use no live accounts. |
| Host mounts | Broad mounts can expose repo or private files. | Forbid host mounts in first CUA smoke. |
| Privileged containers | Privileged mode weakens isolation. | Forbid privileged containers unless a future explicit approval exists. |

## Windows Home Limitations

Project docs identify Windows Home as a reason to prefer Docker Desktop/WSL2 over Windows Sandbox. If Docker Desktop cannot complete WSL2 setup, CUA local sandbox work remains blocked and Ghoti should fall back to Screenpipe status, Obsidian vault sync, and browser-only research.

## How To Disable Docker Desktop Autostart

After install, the operator can use Docker Desktop settings:

1. Open Docker Desktop.
2. Go to Settings.
3. Disable "Start Docker Desktop when you sign in" if desired.
4. Apply and restart Docker Desktop if prompted.

Codex did not change these settings.

## How To Uninstall Docker Desktop If Needed

1. Open Windows Settings.
2. Go to Apps.
3. Select Docker Desktop.
4. Choose Uninstall.
5. Reboot if prompted.
6. Run `wsl --shutdown` after uninstall if WSL remains active.

Do not manually delete repo folders, runtime logs, or third-party clones as part of Docker rollback.

## What Not To Delete From The Repo

- `21_repos/third_party/**`
- `01_projects/runtime_mvp/runtime_data/**`
- `01_projects/dashboard_mvp/.tmp-screenshots/**`
- `05_logs/**` unless a future cleanup milestone explicitly permits it.
- `14_context/**` project history docs.
- Current prompt/task files.

## What Not To Commit

- Docker-generated logs or screenshots.
- Container screenshots unless explicitly approved as tiny proof artifacts.
- Runtime data.
- `.tmp-screenshots`.
- Third-party repo contents.
- CV documents.
- Output folder artifacts.

## What To Check After Reboot

```powershell
docker --version
docker compose version
docker info
wsl --status
wsl --list --verbose
git status --short
```

`git status --short` should be reviewed to make sure no Docker/runtime artifacts became tracked or staged.

## Verdict

The Docker risk is manageable if the install milestone remains verification-only and the first CUA run is deferred. The largest risks are background services, WSL/backend setup, disk growth, network exposure, and accidental host mounts.
