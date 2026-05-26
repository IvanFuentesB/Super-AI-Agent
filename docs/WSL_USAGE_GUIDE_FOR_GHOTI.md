# WSL Usage Guide For Ghoti

WSL lets Windows run Ubuntu. Ghoti uses Ubuntu WSL for Hermes checks, but N+6.2A only verifies the manual bridge. No live API calls, provider setup, Telegram setup, browser automation, or computer-use click/type are run.

Open Ubuntu from Windows PowerShell:

```powershell
wsl -d Ubuntu
```

Exit Ubuntu:

```bash
exit
```

## Path Mapping

- Windows repo path: `C:\Users\ai_sandbox\Documents\AI_Managed_Only`
- WSL repo path: `/mnt/c/Users/ai_sandbox/Documents/AI_Managed_Only`
- Prompt example: `ai_sandbox@Ivan-G14:/mnt/c/Users/ai_sandbox$`

The `/mnt/c` prefix is Ubuntu's view of the Windows `C:\` drive. The prompt means user `ai_sandbox`, machine `Ivan-G14`, current directory `/mnt/c/Users/ai_sandbox`.

## Safe Checks

```powershell
wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; command -v hermes || true"
wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --version || true"
wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes skills list | head -120 || true"
```

These are safe probes only. They do not configure providers, tokens, Telegram, browser automation, computer-use, or live APIs.

## Ghoti Commands

```powershell
python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json
python 03_scripts/ghoti_product_launcher.py --hermes-wsl-guide --json
python 03_scripts/ghoti_product_launcher.py --hermes-safe-commands --json
python 03_scripts/hermes_manual_bridge_verifier.py --write-guide --json
```

Generated files live under `14_context/hermes_manual_bridge/generated/`.
