# Runtime Activation context (N+6.17A)

This folder holds the configuration contract for the **Ghoti Runtime Activation
Pack** — a small set of local PowerShell wrappers that make Ghoti easier to actually
use from PowerShell, Telegram, and WSL Hermes. The scripts themselves live in
`03_scripts/runtime_activation/`.

## What the activation pack does

It gives you one safe local command for each everyday action:

1. Resolve a working Python interpreter even when the PATH `python` shim is broken.
2. Check Ghoti runtime health in one command.
3. Generate status brain output / write a Hermes handoff note.
4. Enable Telegram `/status` to read the status bridge — in a **local runtime
   config only**, written outside the repo.
5. Start the status-only `GhotiDeepBot` runtime.
6. Resume the same WSL Hermes session.

## Files here

- `runtime_activation_status_schema.json` — the shape of the JSON emitted by
  `check_ghoti_runtime.ps1`.
- This README.

The example config is `23_configs/runtime_activation.example.json`.

## Secrets stay outside the repo

The Telegram bot token and the allowed chat id live **outside the repo**, in:

- `C:/Users/ai_sandbox/.ghoti_secrets/telegram_bot_token.txt`
- `C:/Users/ai_sandbox/.ghoti_secrets/telegram_allowed_chat_id.txt`

The local runtime config the enable script writes lives outside the repo too, at
`C:/Users/ai_sandbox/.ghoti_runtime/telegram_status_config.json`. Nothing in this
repo contains a real token or a real chat id, and the runtime config is never
committed.

## Hermes is WSL-only now

The Windows Hermes Desktop app was deleted. WSL Hermes is the only Hermes
installation now. The activation pack resumes the same session
`20260601_081506_d35c70`. The status bridge and the handoff note are the memory
source Hermes reads, so it stops repeating a generic summary.

## Safety

Local and read-only by default. No live Telegram control, no `/run`, no live agent
launch, no MCP, no live browser/computer-use, no OS click/type, no account login, no
email/WhatsApp, no auto-send, no external API, no installs, and no Docker/VPS
deployment. Approval gates are unchanged.
