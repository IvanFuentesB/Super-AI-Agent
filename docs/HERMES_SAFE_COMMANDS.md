# Hermes Safe Commands

These commands are allowed in N+6.2A because they are read-only probes or local Ghoti status commands. No live API calls, provider setup, Telegram setup, tokens, browser automation, or computer-use click/type are run.

```powershell
wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; pwd"
wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; command -v hermes || true"
wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --version || true"
wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes skills list | head -120 || true"
wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --help | head -120 || true"
python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json
python 03_scripts/ghoti_product_launcher.py --hermes-wsl-guide --json
python 03_scripts/ghoti_product_launcher.py --hermes-safe-commands --json
```

If a command asks for auth, provider setup, Telegram, a token, browser control, or computer-use control, stop and treat it as out of scope.
