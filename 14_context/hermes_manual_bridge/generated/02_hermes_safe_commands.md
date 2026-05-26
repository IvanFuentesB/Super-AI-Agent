# Hermes Safe Commands

        These commands are safe now because they are read-only probes or local Ghoti
        status commands. They do not run setup, auth, Telegram, provider config,
        live APIs, browser automation, or computer-use control.

        - `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; pwd"` - Confirms Ubuntu WSL opens and shows the current Linux path.
- `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; command -v hermes || true"` - Read-only command lookup; no setup or login.
- `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --version || true"` - Read-only version check.
- `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes skills list | head -120 || true"` - Read-only skills view capped at 120 lines.
- `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --help | head -120 || true"` - Read-only command surface overview capped at 120 lines.
- `python 03_scripts/ghoti_product_launcher.py --hermes-manual-status --json` - Repo-local JSON status wrapper for daily use.

        Safety: safe probes only, no live provider setup.
