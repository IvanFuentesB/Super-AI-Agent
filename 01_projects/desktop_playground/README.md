# Desktop Playground

Local desktop bridge foundation for checking whether the workspace can safely support the first desktop-control building blocks.

## What It Checks Now

- PowerShell environment visibility
- basic process visibility
- harmless shell command execution
- harmless local launcher capability

## What It Does Not Do Yet

- no cursor movement
- no app switching
- no click or typing automation
- no clipboard orchestration
- no approval wait loop

## How To Run

```powershell
powershell.exe -ExecutionPolicy Bypass -File C:\Users\ai_sandbox\Documents\AI_Managed_Only\01_projects\desktop_playground\check_desktop_playground.ps1
```
