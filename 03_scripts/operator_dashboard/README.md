# Ghoti Operator Dashboard (N+6.18A)

A small, local-only operator view: one web page that shows Ghoti's runtime status at
a glance, so you no longer have to read raw terminal JSON. It is **status-only** and
read-only - it runs no commands, starts or stops no services, mutates no config, and
shows no secrets. Python standard library only; nothing to install.

## Quick start

Resolve a working Python and start the dashboard (the start wrapper handles the
broken PATH `python` shim for you):

```powershell
# preview the would-run command and readiness, start nothing:
pwsh -File 03_scripts/operator_dashboard/start_operator_dashboard.ps1 -DryRun
# start the dashboard attached to this window (Ctrl+C stops it):
pwsh -File 03_scripts/operator_dashboard/start_operator_dashboard.ps1
```

Then open <http://127.0.0.1:8765/> in your browser. Pass `-OpenBrowser` to have the
wrapper open it for you (it opens nothing by default).

## Commands

1. **Status JSON without a server:**

   ```
   python 03_scripts/operator_dashboard/ghoti_operator_dashboard.py --status-json
   ```

2. **Safety self-check (files, routes, config are safe):**

   ```
   python 03_scripts/operator_dashboard/ghoti_operator_dashboard.py --check --json
   ```

3. **Serve locally (loopback only):**

   ```
   python 03_scripts/operator_dashboard/ghoti_operator_dashboard.py --serve --host 127.0.0.1 --port 8765
   ```

4. **One-command health/safety check (PowerShell):**

   ```
   pwsh -File 03_scripts/operator_dashboard/check_operator_dashboard.ps1
   ```

Because the PATH `python` shim is broken on this host, prefer the PowerShell wrappers
(they resolve a working interpreter first), or call a known-good interpreter directly.

## What the page shows

Runtime health, Python resolver status, status brain and status bridge availability,
Telegram status-only readiness, the WSL Hermes resume command preview, Ollama/Gemma
availability, the current `origin/main` short SHA, the latest Claude/Codex reports,
the computer-use sandbox status, the disabled capabilities, and the next recommended
action.

## Endpoints

All routes are GET and read-only:

- `GET /` - the dashboard page
- `GET /api/status` - the status payload
- `GET /api/health` - a health object
- `GET /api/disabled-capabilities` - the disabled-capability list

There are no `POST` routes and no command-execution endpoints. The server binds
`127.0.0.1` only; a non-loopback host is refused unless an explicit opt-in flag is
passed, and that flag is left disabled.

## Safety

Local and read-only. No live automation, no external access, no command execution, no
process start/stop, no runtime-config mutation, no secrets, no MCP, no live
browser/computer-use, no OS input, no auto-send, no external API, no installs. Every
subprocess call uses an argument array (no `Invoke-Expression`, no shell string).
Approval gates are unchanged. A future public/remote dashboard is a separate
milestone and would require authentication and HTTPS first.
