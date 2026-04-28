# Persistent Dashboard Launcher — N+3.13

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.13
Status: launcher_script_created / no_service_installed / no_auto_start

---

## What Was Implemented

A minimal PowerShell launcher script was created at:
  03_scripts/run_dashboard.ps1

No service installed. No Windows Startup folder entry. No admin required.
Operator-triggered only.

---

## Exact Launch Command

From repo root:
  powershell.exe -ExecutionPolicy Bypass -File .\03_scripts\run_dashboard.ps1

With browser auto-open:
  powershell.exe -ExecutionPolicy Bypass -File .\03_scripts\run_dashboard.ps1 -OpenBrowser

Dashboard URL: http://localhost:3210

---

## How the Launcher Works

1. Resolves repo root from script path (no hardcoded paths)
2. Verifies server.js exists at 01_projects/dashboard_mvp/server.js
3. Sets Location to dashboard_mvp directory
4. Runs: node server.js
5. Optionally opens browser at http://localhost:3210
6. Prints URL and stop instructions

---

## How to Stop

Press Ctrl+C in the terminal running the launcher.
The Node.js server process exits cleanly.

---

## Future Shortcut Plan

When ready (future milestone, operator decision):
1. Create a Windows Desktop shortcut pointing to:
     powershell.exe -ExecutionPolicy Bypass -File "C:\Users\ai_sandbox\Documents\AI_Managed_Only\03_scripts\run_dashboard.ps1" -OpenBrowser
2. Test that dashboard survives terminal close when launched via shortcut
3. Optionally place shortcut in Startup folder for auto-start on login

---

## What Was NOT Implemented

- No Windows service (requires separate approval)
- No Startup folder entry (operator to evaluate after shortcut test)
- No npm package installs
- No admin required
- No service account setup
- No auto-start mechanism

---

## Dashboard State

- server.js port: 3210 (env PORT or default)
- Routes available: screenpipe/status, computer-use/candidates, action-intents, wait-resume/status, ghoti/action-audit/status
- Dashboard is manually started only
- No runtime changes to server.js made
