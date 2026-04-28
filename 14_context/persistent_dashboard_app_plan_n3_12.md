# Persistent Dashboard/App Plan -- N+3.12

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.12
Status: planning_only / not_implemented

---

## Problem Statement

The Ghoti operator dashboard (Node.js server at 01_projects/dashboard_mvp/server.js) must be
relaunched manually each time the machine restarts or the terminal session closes.
There is no persistent startup mechanism yet.

---

## Options (Lowest to Highest Risk)

### Option 1 — Windows Shortcut + PowerShell Launcher (LOWEST RISK, Recommended First Step)

Create a .ps1 script that:
- Navigates to the dashboard directory
- Starts the Node server
- Opens the browser at localhost:<port>

Create a Windows Desktop shortcut that runs:
  powershell.exe -ExecutionPolicy Bypass -File "C:\...\run_dashboard.ps1"

Pros: No service install, no admin required, operator-triggered, reversible.
Cons: Operator must click the shortcut on each login.

### Option 2 — Startup Folder Entry (LOW RISK)

Place the .ps1 shortcut in:
  %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\

Dashboard auto-starts on user login.

Pros: Auto-start without Windows Service, no admin, reversible.
Cons: Runs in background without tray indicator.

### Option 3 — Local System Tray App / Electron Shell (MEDIUM RISK, Future)

Wrap the dashboard in a minimal Electron app with:
- System tray icon showing Ghoti state
- Start/stop controls
- Health check ping

Pros: Professional operator UX, persistent indicator.
Cons: Requires Electron install (~150 MB), more complexity.

### Option 4 — Windows Service (HIGHER RISK, Needs Separate Approval)

Register dashboard as a Windows service using nssm or sc.exe.

DO NOT implement yet. Requires:
- Explicit operator approval
- Service account scoping
- Restart policy review

---

## Recommended Near-Term Path

1. Create: 03_scripts/run_dashboard.ps1 — starts Node dashboard, prints URL
2. Add health check loop: poll localhost:<port>/api/status until ready
3. Create shortcut for operator convenience
4. Test that dashboard survives terminal close when launched from shortcut
5. Evaluate Option 2 (Startup folder) only if Option 1 proves reliable over several sessions

---

## Constraints

- Localhost only — do NOT expose dashboard on any network interface beyond 127.0.0.1
- Do NOT add Windows service without separate approval
- Do NOT expose publicly
- Do NOT require admin for the basic launcher path
- Keep the existing dashboard server.js unchanged unless a specific fix is needed

---

## Current Dashboard State

- Dashboard server: 01_projects/dashboard_mvp/server.js
- Screenpipe status route: GET /api/ghoti/screenpipe/status (read-only)
- CUA candidates route: GET /api/ghoti/computer-use/candidates (read-only)
- Action intents route: GET /api/ghoti/action-intents (read-only)
- Wait/resume route: GET /api/ghoti/wait-resume/status (read-only)
- Dashboard is manually started; no persistence mechanism yet
