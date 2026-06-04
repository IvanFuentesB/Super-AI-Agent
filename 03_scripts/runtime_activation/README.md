# Ghoti Runtime Activation Pack (N+6.17A)

Small, local PowerShell wrappers that make Ghoti easier to actually use from
PowerShell, Telegram, and WSL Hermes. Every script emits a single JSON object, runs
locally and read-only by default, and uses an argument array for any external call
(no `Invoke-Expression`, no `shell=True`).

The configuration contract for the pack lives in
`14_context/runtime_activation/` and `23_configs/runtime_activation.example.json`.

## Why this pack exists

The PATH `python` shim is broken on this host (a uv trampoline that fails to spawn
its Python child). Bare `python` therefore fails, which breaks the existing
launchers. This pack resolves a *working* interpreter first, then drives the local
status tooling with it.

## The commands

Run these from the repo root in PowerShell.

1. **Resolve a working Python** (skips the broken PATH shim):

   ```powershell
   pwsh -File 03_scripts/runtime_activation/ghoti_python_resolver.ps1
   ```

   Emits `{ ok, executable, source, tried, error }`.

2. **Check runtime health** in one command:

   ```powershell
   pwsh -File 03_scripts/runtime_activation/check_ghoti_runtime.ps1
   ```

   Resolves Python, reports `origin/main`, checks the status brain / status bridge /
   Telegram bot scripts are present, checks the secret files exist (existence only,
   never their values), and best-effort probes WSL, ollama, and a local gemma model.
   The output shape is documented in
   `14_context/runtime_activation/runtime_activation_status_schema.json`.

3. **Write the Hermes status handoff** (so Hermes reads one status source instead of
   repeating a generic summary):

   ```powershell
   pwsh -File 03_scripts/runtime_activation/write_hermes_status_handoff.ps1
   # preview only, writes nothing:
   pwsh -File 03_scripts/runtime_activation/write_hermes_status_handoff.ps1 -DryRun
   ```

   Uses the resolved Python to call the local read-only status bridge with
   `--write-hermes-handoff`. The note is written inside the repo at
   `14_context/agent_handoff_vault/04_Logs/HERMES_STATUS_BRIDGE_LAST_RUN.md`.

4. **Enable Telegram `/status` to use the status bridge** in the LOCAL runtime config
   only (written OUTSIDE the repo, never committed):

   ```powershell
   # preview what would be written, write nothing:
   pwsh -File 03_scripts/runtime_activation/enable_status_bridge_runtime_config.ps1 -DryRun
   # actually write the local runtime config:
   pwsh -File 03_scripts/runtime_activation/enable_status_bridge_runtime_config.ps1
   ```

   Flips `status_bridge_enabled` and `use_status_bridge_for_telegram_status` to true
   in `C:/Users/ai_sandbox/.ghoti_runtime/telegram_status_config.json`. The config
   stores only file PATHS to the token and chat-id files; it never stores a token or
   a chat id. Telegram stays status-only — there is no `/run` and no live control.

5. **Start the status-only GhotiDeepBot runtime** using the resolved Python:

   ```powershell
   # preview the would-run command and readiness, start nothing:
   pwsh -File 03_scripts/runtime_activation/start_ghotideepbot_status_only.ps1 -DryRun
   # start the bot attached to this window (keep the window open):
   pwsh -File 03_scripts/runtime_activation/start_ghotideepbot_status_only.ps1
   ```

   The token is never placed on the command line and never printed.

6. **Resume the same WSL Hermes session** `20260601_081506_d35c70`:

   ```powershell
   # preview the exact command, launch nothing (default):
   pwsh -File 03_scripts/runtime_activation/resume_wsl_hermes_session.ps1
   # actually resume WSL Hermes attached to this window:
   pwsh -File 03_scripts/runtime_activation/resume_wsl_hermes_session.ps1 -Run
   ```

## Secrets stay outside the repo

The Telegram bot token and the allowed chat id live OUTSIDE the repo, in
`C:/Users/ai_sandbox/.ghoti_secrets/`. The local runtime config the enable script
writes lives outside the repo too, at
`C:/Users/ai_sandbox/.ghoti_runtime/telegram_status_config.json`. Nothing in this
repo contains a real token or a real chat id.

## Hermes is WSL-only now

The Windows Hermes Desktop app was deleted. WSL Hermes is the only Hermes
installation now, and the pack resumes the same session `20260601_081506_d35c70`.
The status bridge and the handoff note are the memory source Hermes reads.

## Safety

Local and read-only by default. No live Telegram control, no `/run`, no live agent
launch, no MCP, no live browser/computer-use, no OS click/type, no account login, no
email/WhatsApp, no auto-send, no external API, no installs, and no Docker/VPS
deployment. Approval gates are unchanged.
