# N+3.13 Codex Persistent Dashboard/App Review

Status: codex_parallel_audit / dashboard_persistence_review / no_implementation / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Current Dashboard Relaunch Problem

The dashboard is a local Node server at:

```text
01_projects/dashboard_mvp/server.js
```

`server.js` listens on `127.0.0.1` and defaults to port `3210` via `process.env.PORT || "3210"`.

Dashboard package scripts:

```json
{
  "start": "node server.js",
  "dev": "node server.js",
  "check": "node server.js --check"
}
```

Current pain: the operator must manually relaunch the dashboard after reboot or terminal close.

## Safest Next Step

Create a repo-local launcher script later:

```text
03_scripts/run_dashboard.ps1
```

This should be the next persistence step, not a Windows service or Electron app.

## Why Not Windows Service Yet

- Services can run without a visible operator context.
- Services may require admin setup.
- Service restart behavior can hide failures.
- Ghoti is still approval-gated and operator-visible; invisible background operation would be premature.

## Why Not Electron/Tauri Yet

- Adds dependencies and packaging complexity.
- Dashboard UX/runtime is still changing quickly.
- A thin PowerShell launcher provides most near-term value with far less surface area.

## Why Not Auto-Start Yet

- Auto-start could make Ghoti feel like a daemon before the operator UX is stable.
- Startup folder behavior should require a separate approval after manual launcher proves reliable.

## Recommended Progression

1. PowerShell launcher.
2. Desktop shortcut.
3. Health check script.
4. Optional Startup folder entry after approval.
5. Later Electron/Tauri app if dashboard stabilizes.

## Candidate Launcher Behavior

Future `03_scripts/run_dashboard.ps1` should:

- `cd` to repo root or dashboard directory deterministically.
- Check Node version.
- Start `01_projects/dashboard_mvp/server.js`.
- Print the localhost URL.
- Bind only to `127.0.0.1`.
- Avoid admin rights.
- Avoid background daemon behavior unless user approves.
- Avoid public network exposure.
- Avoid touching runtime data except natural dashboard behavior.

## Plugin / Tool Note

- No Codex plugin is needed beyond terminal/git for this launcher.
- Claude Code should perform repo changes when this becomes an implementation milestone.
- Docker Desktop should remain manually supervised for now.
- Vercel, Cloudflare, Neon, Sentry, Hugging Face, and deployment plugins are not needed for local dashboard persistence.

## Verdict

Persistent dashboard work is worthwhile, but should start with a simple local PowerShell launcher and desktop shortcut. Do not jump to service/app/autostart until the operator approves the next level.
