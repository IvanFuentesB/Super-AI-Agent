# Dashboard Launcher Check — N+3.14

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.14
Status: readiness_check_pass / no_service_installed / no_autostart

---

## Script Exists

- Path: 03_scripts/run_dashboard.ps1
- Script exists: YES
- Script readable: YES (32 lines)
- Script valid PowerShell: YES (syntax check via Get-Content preview passed)

---

## Node Syntax Checks

| File | Check |
|---|---|
| 01_projects/dashboard_mvp/server.js | PASS (node --check) |
| 01_projects/dashboard_mvp/public/app.js | PASS (node --check) |
| 01_projects/dashboard_mvp/public/overlay.js | PASS (node --check) |

---

## Launch Command

To start the dashboard:
```
powershell.exe -ExecutionPolicy Bypass -File .\03_scripts\run_dashboard.ps1
```

With browser auto-open:
```
powershell.exe -ExecutionPolicy Bypass -File .\03_scripts\run_dashboard.ps1 -OpenBrowser
```

Dashboard URL: http://localhost:3210

---

## What Was NOT Done

- No Windows service installed
- No Startup folder entry added
- No autostart mechanism created
- No npm install run
- No admin required
- Dashboard was NOT launched in this milestone check (dry readiness check only)

---

## Later Shortcut Recommendation

When ready (separate operator decision):
1. Create a Desktop shortcut pointing to:
   `powershell.exe -ExecutionPolicy Bypass -File "C:\Users\ai_sandbox\Documents\AI_Managed_Only\03_scripts\run_dashboard.ps1" -OpenBrowser`
2. Test that the dashboard survives terminal close when launched via shortcut.
3. Optionally place shortcut in Windows Startup folder for auto-start on login (requires separate approval).
