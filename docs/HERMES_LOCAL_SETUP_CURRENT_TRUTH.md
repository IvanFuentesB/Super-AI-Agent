# Hermes Local Setup — Current Truth

Milestone: N+6.4A
Date: 2026-05-31
Scope: factual record of the local Hermes coordinator as it exists today. No
setup steps are executed by this document; it only registers the current state.

## Where Hermes runs

- Environment: `ai_sandbox` WSL Ubuntu.
- Hermes version seen: v0.14.0.
- Coordinator model: llama3.1:8b.

## Model provider

- Provider type: custom local endpoint (OpenAI-compatible).
- Endpoint: http://127.0.0.1:11434/v1
- This is a local Ollama-style endpoint on the loopback interface. It is not a
  cloud provider and requires no API key in this repo.

## Local models available

| Model | Purpose |
|-------|---------|
| llama3.1:8b | Hermes coordinator brain (planning, routing, handoff drafting). |
| gemma3:4b | Cheap summaries, compression, and classification. |

- qwen was removed and is no longer part of the local model set.

## Capabilities NOT enabled for Ghoti

These tools may be visible inside Hermes, but for Ghoti they are not approved
and not turned on:

- Telegram: NOT configured for Ghoti Hermes. There is no bot token, chat wiring,
  or messaging integration in this repo.
- Browser automation and computer-use: NOT approved and NOT enabled. Ghoti does
  not click, type, move the mouse, or capture/act on the screen through Hermes.
- Cross-agent automation: Claude Code and Codex are NOT automatically driven by
  Hermes. Handoffs are manual through the Obsidian vault and prompt bus.

## Safety posture

- Local-first: the model endpoint is loopback only.
- No secrets, tokens, `.env`, cookies, or browser sessions are stored or read by
  this registration.
- Human approval remains required for risky actions and all merges.

## Next safe steps (not done here)

- If/when desired, a manual, human-approved Telegram setup can be planned in a
  separate milestone (no auto-enable).
- Browser/computer-use remain gated behind explicit human approval and a
  dedicated safety review before any enablement.
