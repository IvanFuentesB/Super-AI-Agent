# Obsidian Open Helper — N+3.49A

Generated: 2026-05-06
Branch: feat/ghoti-agent-claude-n3-49-local-orchestrator-ruflo-smoke
Deliverable: N+3.49A-D

## Purpose

`03_scripts/open_obsidian_vault.ps1` — PowerShell helper to inspect and open the Ghoti Obsidian vault.

## Vault Location

```
14_context/obsidian_vault/
```

Required files verified present:
- `00_Index.md`
- `01_Current_State.md`
- `02_Next_Actions.md`
- `09_Migration_Handoff.md`

## Usage

```powershell
# Check required files exist (read-only)
.\03_scripts\open_obsidian_vault.ps1 -Check

# Open vault in Obsidian app (requires Obsidian installed)
.\03_scripts\open_obsidian_vault.ps1 -Open
```

## Safety Notes

- Script is read-only (`-Check` mode); makes no writes.
- `-Open` uses `obsidian://` URI scheme — requires Obsidian desktop app installed.
- No network calls, no account actions, no token spend.
- If Obsidian is not installed, `-Open` will silently fail or open a browser prompt.

## Integration with Orchestrator

`ghoti_local_orchestrator.py --obsidian-check` performs the same file checks programmatically via Python (no PowerShell required). Use the `.ps1` script when you want to open the vault in the Obsidian UI.
