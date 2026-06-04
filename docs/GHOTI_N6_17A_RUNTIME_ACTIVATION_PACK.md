# Ghoti Runtime Activation Pack (N+6.17A)

This milestone makes Ghoti easier to actually *use* from PowerShell, Telegram, and
WSL Hermes. It adds a small set of local PowerShell wrappers - the **runtime
activation pack** - in `03_scripts/runtime_activation/`. Every wrapper is local and
read-only by default, emits a single JSON object, and makes any external call with an
argument array (no `Invoke-Expression`, no `shell=True`). It is status-only. There is
no remote control, no `/run`, no live agent launch, no MCP, no live
browser/computer-use, no OS click/type, no email or WhatsApp, no auto-send, and no
account automation.

## The problem this solves

Three everyday frictions had simple, local fixes:

- **Bare `python` is broken on this host.** The PATH `python` shim is a uv trampoline
  that fails to spawn its Python child ("failed to spawn ... entity not found"). Any
  launcher that calls bare `python` fails before it starts. The pack resolves a
  *working* interpreter first and drives everything with it.
- **Hermes repeats a generic summary.** When Hermes has no fresh, structured status
  to read, it falls back to boilerplate. The fix is a memory path it can read, not a
  bigger prompt. **The status bridge and the handoff note are the memory source**
  Hermes reads, so it stops repeating a generic summary.
- **Starting the status runtime took several fiddly steps.** The pack gives one safe
  command for each everyday action, each with a dry-run preview.

## What the pack does

One safe local command for each everyday action:

1. **Resolve a working Python** even when the PATH `python` shim is broken
   (`ghoti_python_resolver.ps1`).
2. **Check Ghoti runtime health** in one command (`check_ghoti_runtime.ps1`).
3. **Write the Hermes status handoff** so Hermes reads one status source
   (`write_hermes_status_handoff.ps1`).
4. **Enable Telegram `/status` to use the status bridge** in a LOCAL runtime config
   only, written outside the repo (`enable_status_bridge_runtime_config.ps1`).
5. **Start the status-only GhotiDeepBot runtime** with the resolved Python
   (`start_ghotideepbot_status_only.ps1`).
6. **Resume the same WSL Hermes session** (`resume_wsl_hermes_session.ps1`).

The full how-to-run list is in `03_scripts/runtime_activation/README.md`. The output
shape of the health check is documented in
`14_context/runtime_activation/runtime_activation_status_schema.json`, and the
configuration contract example is `23_configs/runtime_activation.example.json`.

## Useful local commands

Resolve a working Python (skips the broken PATH shim):

```
pwsh -File 03_scripts/runtime_activation/ghoti_python_resolver.ps1
```

Check runtime health in one command:

```
pwsh -File 03_scripts/runtime_activation/check_ghoti_runtime.ps1
```

Write the Hermes-readable handoff note (one status source for Hermes):

```
pwsh -File 03_scripts/runtime_activation/write_hermes_status_handoff.ps1
```

Preview enabling the Telegram status-bridge runtime config (writes nothing):

```
pwsh -File 03_scripts/runtime_activation/enable_status_bridge_runtime_config.ps1 -DryRun
```

Preview starting the status-only bot, and preview resuming WSL Hermes:

```
pwsh -File 03_scripts/runtime_activation/start_ghotideepbot_status_only.ps1 -DryRun
pwsh -File 03_scripts/runtime_activation/resume_wsl_hermes_session.ps1
```

## Hermes is WSL-only now

The Windows Hermes Desktop app was deleted. WSL Hermes is the only Hermes
installation now. The pack resumes the same session `20260601_081506_d35c70` in the
repo mount, so you keep one continuous Hermes session instead of starting over. The
status bridge and the handoff note are the memory source Hermes reads.

## Telegram stays status-only

The enable script flips `status_bridge_enabled` and
`use_status_bridge_for_telegram_status` to true in the LOCAL runtime config only -
`C:/Users/ai_sandbox/.ghoti_runtime/telegram_status_config.json`, written outside the
repo and never committed. That config stores only file PATHS to the token and chat-id
files; it never stores a token or a chat id. **Telegram stays status-only: there is
no `/run` and no live control.**

## Safety

- **No secrets in the repo.** The Telegram bot token and the allowed chat id live
  outside the repo, in `C:/Users/ai_sandbox/.ghoti_secrets/`. The local runtime
  config the enable script writes lives outside the repo too. Nothing in this repo
  contains a real token or a real chat id, and the health check reports only whether
  the secret files exist - it never reads their values.
- **Local and read-only by default.** The wrappers open no network connection, call
  no external API, launch no agent, control no browser or desktop, send nothing,
  install nothing, and run no third-party code. Every external call uses an argument
  array - never a shell string, never `Invoke-Expression`.
- **Preview first.** The actions that write outside the repo, start the bot, or
  resume Hermes all default to a dry-run/preview or require an explicit `-Run`.
- **Approval gates intact.** Nothing here weakens an approval gate. Live control,
  remote command, and agent launch remain future, separately-approved milestones.

## What stays disabled

Remote control, `/run`, live agent launch, MCP, live browser/computer-use, OS-level
click/type, account login automation, email/WhatsApp drafting, auto-send, external
API calls, installs, Docker/VPS runtime, and third-party code execution are all still
disabled and out of scope for this milestone.
