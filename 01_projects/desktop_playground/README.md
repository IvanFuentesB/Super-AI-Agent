# Desktop Playground

Local desktop bridge playground for a narrow, safe, approval-aware first slice of desktop-aware operator actions.

## What It Checks Now

- PowerShell environment visibility
- basic process visibility
- harmless shell command execution
- harmless local launcher capability
- allowlisted window discovery
- foreground window detection
- focusing an allowlisted terminal window
- opening an allowlisted local app
- capturing a repo-local desktop screenshot artifact

## What It Does Not Do Yet

- no arbitrary desktop control
- no general app switching or window targeting
- no click or typing automation
- no clipboard orchestration
- no approval wait loop or daemon behavior

## How To Run

```powershell
powershell.exe -ExecutionPolicy Bypass -File C:\Users\ai_sandbox\Documents\AI_Managed_Only\01_projects\desktop_playground\check_desktop_playground.ps1
```
