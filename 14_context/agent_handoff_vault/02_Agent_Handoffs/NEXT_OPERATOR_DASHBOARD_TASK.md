# Next task: Operator Dashboard

Status-only handoff note. This describes the next safe, local step around the N+6.18A
operator dashboard. It authorizes no live control, no remote access, no command
execution, no agent launch, and no secrets in the repo.

## Where things stand

- The operator dashboard (`03_scripts/operator_dashboard/`) is the first local
  operator view: one local web page that shows Ghoti's runtime status so you no longer
  have to read raw terminal JSON. It is **status-only** and read-only.
- It serves a static page plus three read-only GET JSON endpoints (`/api/status`,
  `/api/health`, `/api/disabled-capabilities`) on `127.0.0.1:8765`. There are no POST
  routes and no command-execution endpoints.
- It aggregates the existing local status tools (status bridge, runtime activation
  config, feature flags, and bounded `wsl`/`ollama` probes) and degrades gracefully if
  any one is missing.

## Useful commands

```
pwsh -File 03_scripts/operator_dashboard/start_operator_dashboard.ps1 -DryRun
pwsh -File 03_scripts/operator_dashboard/start_operator_dashboard.ps1
pwsh -File 03_scripts/operator_dashboard/check_operator_dashboard.ps1
python 03_scripts/operator_dashboard/ghoti_operator_dashboard.py --status-json
python 03_scripts/operator_dashboard/ghoti_operator_dashboard.py --check --json
```

Then open <http://127.0.0.1:8765/>.

## Suggested next step (when approved)

If you want to use the dashboard daily, start it with the PowerShell wrapper and keep
the window open. Keep everything local and read-only; do not add any POST route,
command execution, process control, or remote access.

## Out of scope / still disabled

Remote/external access, command execution, process start/stop, runtime-config
mutation, Telegram `/run` and `/send`, live agent launch, MCP, live
browser/computer-use, OS input, account login, email/WhatsApp, auto-send, external
API, installs, and external-repo code execution remain disabled. A future public or
remote dashboard is a separate milestone and would require authentication and HTTPS
first. No secrets are stored in the repo.
