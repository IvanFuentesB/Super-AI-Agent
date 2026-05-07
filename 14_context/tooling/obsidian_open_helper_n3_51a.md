# Obsidian Open Helper — N+3.51A

Generated: 2026-05-06

## Script

`03_scripts/open_obsidian_vault.ps1`

## Commands Run

```powershell
powershell -ExecutionPolicy Bypass -File 03_scripts/open_obsidian_vault.ps1 -Check
```

## Status

| Item | Value |
|------|-------|
| Vault path | `14_context/obsidian_vault` |
| Vault exists | YES |
| Vault .md files | 12 |
| Required files | ALL PRESENT (00_Index.md, 01_Current_State.md, 02_Next_Actions.md, 09_Migration_Handoff.md) |
| Obsidian (winget) | FOUND — Obsidian.Obsidian 1.12.7 |
| Obsidian exe | FOUND — `C:\Users\Navif\AppData\Local\Programs\Obsidian\Obsidian.exe` |

## How to Open

```powershell
powershell -ExecutionPolicy Bypass -File 03_scripts/open_obsidian_vault.ps1 -Open
```

Or via URI:
```
obsidian://open?path=C%3A%5CUsers%5Cai_sandbox%5CDocuments%5CAI_Managed_Only%5C14_context%5Cobsidian_vault
```

## Automation State

- `-Check`: PASS — validates vault, required files, winget listing, executable candidates
- `-Open`: Available (not run in this session — does not claim GUI opened without -Open flag)

## Notes

- The script uses PowerShell `Start-Process` with Obsidian URI — no network calls
- Obsidian exe found at Navif profile path (shared installation)
- Dashboard now checks for Navif path as additional candidate
