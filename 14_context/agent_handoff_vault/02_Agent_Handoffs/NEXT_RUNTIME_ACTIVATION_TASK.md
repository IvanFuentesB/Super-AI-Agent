# Next task: Runtime Activation Pack

Status-only handoff note. This describes the next safe, local step around the N+6.17A
runtime activation pack. It authorizes no live control, no remote command, no agent
launch, and no secrets in the repo.

## Where things stand

- The runtime activation pack (`03_scripts/runtime_activation/`) gives one safe local
  command for each everyday action: resolve a working Python, check runtime health,
  write the Hermes handoff, enable the Telegram status-bridge runtime config, start
  the status-only GhotiDeepBot runtime, and resume WSL Hermes.
- Bare `python` is broken on this host (a uv trampoline that fails to spawn its child),
  so the pack resolves a working interpreter first and drives everything with it.
- The Windows Hermes Desktop app was deleted. WSL Hermes is the only Hermes
  installation now, and the pack resumes the same session `20260601_081506_d35c70`.
  The status bridge and the handoff note are the memory source Hermes reads, so it
  stops repeating a generic summary.

## Useful commands

```
pwsh -File 03_scripts/runtime_activation/ghoti_python_resolver.ps1
pwsh -File 03_scripts/runtime_activation/check_ghoti_runtime.ps1
pwsh -File 03_scripts/runtime_activation/write_hermes_status_handoff.ps1
pwsh -File 03_scripts/runtime_activation/enable_status_bridge_runtime_config.ps1 -DryRun
pwsh -File 03_scripts/runtime_activation/start_ghotideepbot_status_only.ps1 -DryRun
pwsh -File 03_scripts/runtime_activation/resume_wsl_hermes_session.ps1
```

## Suggested next step (when approved)

If you want `/status` to read the bridge, run the enable script without `-DryRun` to
write the LOCAL runtime config (outside the repo), then start the status-only bot.
Keep everything local and read-only; do not add any send, remote, or agent-launch
behavior. Telegram stays status-only: there is no `/run` and no live control.

## Out of scope / still disabled

Remote control, `/run`, live agent launch, MCP, live browser/computer-use, OS
click/type, account login, email/WhatsApp, auto-send, external API, installs, and
third-party code execution remain disabled. The Telegram token and chat id stay
outside the repo, and the local runtime config the enable script writes is never
committed.
