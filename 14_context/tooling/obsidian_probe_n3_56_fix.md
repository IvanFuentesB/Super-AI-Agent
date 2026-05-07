# Obsidian Probe — N+3.56-FIX

**Script**: `03_scripts/obsidian_probe.py` (new in N+3.56-FIX)

## Purpose
Single source of truth for Obsidian vault and app detection.
Used by `ghoti_dashboard.py` and `open_obsidian_vault.ps1` to get consistent status.

## Checks performed
- Vault path: `14_context/obsidian_vault`
- Required files: `00_Index.md`, `01_Current_State.md`, `02_Next_Actions.md`, `09_Migration_Handoff.md`
- Executable candidates (same list in both probe and PS1):
  - `C:\Users\Navif\AppData\Local\Programs\Obsidian\Obsidian.exe`
  - `C:\Users\ai_sandbox\AppData\Local\Programs\Obsidian\Obsidian.exe`
  - `C:\Users\ai_sandbox\AppData\Local\Obsidian\Obsidian.exe`
  - `C:\Program Files\Obsidian\Obsidian.exe`
  - `$LOCALAPPDATA\Programs\Obsidian\Obsidian.exe`
  - `$LOCALAPPDATA\Obsidian\Obsidian.exe`
- Winget check: `winget list --id Obsidian.Obsidian --exact` if winget present.

## Validation commands
```bash
python 03_scripts/obsidian_probe.py --status
python 03_scripts/obsidian_probe.py --json
powershell -ExecutionPolicy Bypass -File 03_scripts/open_obsidian_vault.ps1 -Check
```

## --json output fields
```json
{
  "vault": {
    "path": "...",
    "exists": true/false,
    "md_file_count": N,
    "required_files": { "00_Index.md": true/false, ... },
    "required_files_pass": true/false
  },
  "app": {
    "exe_found": true/false,
    "exe_path": "...",
    "exe_candidates_checked": [...],
    "winget_found": true/false,
    "winget_detail": null
  }
}
```

## Safety
- Read-only. No app launch. No network calls. No writes.
- Does not open Obsidian unless `-Open` is explicitly passed to the PS1 script.
