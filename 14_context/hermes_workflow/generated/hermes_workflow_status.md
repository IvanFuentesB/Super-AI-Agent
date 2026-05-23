# Hermes Agent / Manual Bridge Status

Hermes workflow readiness: 58%. Hermes core is installed and skills are visible. Provider setup, Telegram, browser/Playwright, and Codex provider verification remain manual/unproven. Ghoti exposes status, skills index, manual setup plan, and future bridge packet with safe probes only and no live provider setup.

- Launcher: `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
- Dashboard: `http://127.0.0.1:3210`
- Hermes bridge status: `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json`
- Hermes bridge write: `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json`
- Direct status: `python 03_scripts/hermes_agent_workflow_bridge.py --status --json`
- Direct write: `python 03_scripts/hermes_agent_workflow_bridge.py --write-readiness --json`
- Installed: `True`
- WSL path: `/home/ai_sandbox/.local/bin/hermes`
- Version: `Hermes Agent v0.14.0 (2026.5.16)`
- Skills detected: `78`
- Readiness percentage: `58%`
- Codex provider pending/not proven
- Telegram manual later/no token
- browser/Playwright degraded/not claimed
- No VPS: `True`

Safety: safe probes only, no live provider setup, no provider config,
no Telegram setup, no tokens, no browser automation, no live APIs.
