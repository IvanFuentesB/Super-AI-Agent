# Hermes Manual Bridge Verification

N+6.2A makes Hermes easier to understand and verify as a manual bridge. It is not a live automation milestone.

Current truth:

- Hermes is installed in Ubuntu WSL at `/home/ai_sandbox/.local/bin/hermes`.
- Hermes version is `Hermes Agent v0.14.0`.
- Codex provider support remains pending/not proven.
- Telegram remains manual later/no token.
- Browser/Playwright remains degraded/not claimed.
- No VPS is required.

Use:

```powershell
python 03_scripts/hermes_manual_bridge_verifier.py --status --json
python 03_scripts/hermes_manual_bridge_verifier.py --doctor --json
python 03_scripts/hermes_manual_bridge_verifier.py --wsl-explain --json
python 03_scripts/hermes_manual_bridge_verifier.py --write-guide --json
```

The verifier is local-only. It uses safe probes only. No live API calls, provider setup, Telegram setup, tokens, browser automation, computer-use click/type, or account actions are run.

## What This Unlocks

- A repeatable WSL/Hermes status check.
- A guide for Windows-to-WSL path mapping.
- A safe command list.
- A blocked command list.
- A future bridge packet for N+6.3A safe computer-use preparation.

## What Remains Manual

- Hermes setup or provider config.
- Codex provider verification inside Hermes.
- Telegram.
- Browser/Playwright remediation.
- Any click/type/browser/account action.
