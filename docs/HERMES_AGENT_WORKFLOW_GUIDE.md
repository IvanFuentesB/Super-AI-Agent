# Hermes Agent Workflow Guide

Ghoti treats Hermes as a local WSL agent layer that can be inspected safely now and configured manually later. N+5.8A does not run live setup, provider config, Telegram setup, token commands, or browser automation.

## What Works Now

- Hermes WSL status can be checked with safe probes.
- Hermes path is tracked as `/home/ai_sandbox/.local/bin/hermes`.
- Hermes version is tracked as `Hermes Agent v0.14.0`.
- Hermes skills can be indexed with `hermes skills list | head -120`.
- Generated readiness files stay under `14_context/hermes_workflow/generated/`.

## Commands

```powershell
python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json
python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json
python 03_scripts/hermes_agent_workflow_bridge.py --doctor --json
python 03_scripts/hermes_agent_workflow_bridge.py --skills-index --json
```

## Boundaries

- Codex provider support is pending/not proven.
- Telegram is manual later/no token.
- Browser/Playwright is degraded/not claimed.
- No VPS is required.
- Safe probes only; no live provider setup.

## How Hermes Fits

Hermes is a future local agent workflow bridge beside Codex, ChatGPT, Claude, Ollama/Gemma, context packs, Gemma readiness files, and repo knowledge bundles. For now, Ghoti exposes Hermes truth and manual next steps without enabling autonomy. Gemma install and quality work remains separate: use `python 03_scripts/ghoti_product_launcher.py --gemma-doctor --json` and do not run `ollama pull` from Hermes or Codex without a later human-approved milestone.
