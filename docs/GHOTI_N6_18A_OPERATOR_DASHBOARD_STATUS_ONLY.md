# Ghoti Operator Dashboard - status-only MVP (N+6.18A)

This milestone makes Ghoti **visibly useful**: the first local operator view. Instead
of reading raw terminal JSON, the user opens one local web page and sees Ghoti's
runtime status at a glance. It is built with the Python standard library only and is
**status-only**.

## The problem this solves

Ghoti already has a status bridge and a runtime activation pack, but using them means
running scripts and reading JSON in a terminal. There was no single place to *look*.
This dashboard is that place - a small, local, read-only control center that
aggregates the existing local status tools into cards.

## What it is (and is not)

- It **is** a local-only web page plus three read-only GET JSON endpoints.
- It is **status-only**: there is **no live automation**. It runs no commands, starts
  or stops no processes, mutates no runtime config, launches no agent, and sends
  nothing.
- It has **no external access**: the server binds the loopback interface (`127.0.0.1`)
  only, loads no external CSS/JS/fonts, opens no external network connection, and
  calls no external API.
- It needs **no secrets**: it never reads a token or chat-id value; it reports only
  whether helper scripts exist and surfaces the already-sanitized status packet.

## What the dashboard shows

1. Runtime health
2. Python resolver status
3. Status brain availability
4. Status bridge availability
5. Telegram status-bot readiness (status-only)
6. WSL Hermes session command preview (same session)
7. Ollama / Gemma availability
8. Current `origin/main` short SHA
9. Latest Claude / Codex reports (if available)
10. Computer-use sandbox status (dry-run only)
11. What is disabled
12. The next recommended action

## How to run

```
# preview, start nothing:
pwsh -File 03_scripts/operator_dashboard/start_operator_dashboard.ps1 -DryRun
# start locally on 127.0.0.1:8765 (Ctrl+C stops it):
pwsh -File 03_scripts/operator_dashboard/start_operator_dashboard.ps1
```

Then open <http://127.0.0.1:8765/>. The status JSON and a safety self-check are also
available without a server:

```
python 03_scripts/operator_dashboard/ghoti_operator_dashboard.py --status-json
python 03_scripts/operator_dashboard/ghoti_operator_dashboard.py --check --json
pwsh   -File 03_scripts/operator_dashboard/check_operator_dashboard.ps1
```

## Endpoints

| Route | Method | Returns |
|-------|--------|---------|
| `/` | GET | the dashboard page |
| `/api/status` | GET | the full status payload |
| `/api/health` | GET | a health object |
| `/api/disabled-capabilities` | GET | the disabled-capability list and flag posture |

There are **no POST routes** and no command-execution or process-control endpoints.
The output shape is documented in
`14_context/operator_dashboard/operator_dashboard_status_schema.json`.

## Safety

- **Local and read-only.** Binds `127.0.0.1` only; a non-loopback host is refused
  unless an explicit opt-in flag is passed, and that flag is left disabled.
- **No live automation, no external access, no secrets.** Every subprocess call uses
  an argument array - never a shell string and never `Invoke-Expression`.
- **Approval gates intact.** Nothing here weakens an approval gate.
- **Feature flags off.** Five `operator_dashboard_*` flags are added to
  `23_configs/ghoti_feature_flags.example.json`, all defaulting to `false`. The global
  invariant is preserved: the only flag that may be `true` in the example config is
  `telegram_status_commands_enabled`.

## Future public dashboard

A future public or remote dashboard is a **separate milestone**. Exposing this
dashboard beyond localhost would require **authentication** and **HTTPS** first, and
is explicitly out of scope here. This milestone ships the local operator view only.

## What stays disabled

Remote/external access, command execution, process start/stop, runtime-config
mutation, Telegram `/run` and `/send`, live agent launch, Claude/Codex launch, MCP,
live browser/computer-use, OS-level input, account login, email/WhatsApp drafting,
auto-send, external API calls, installs, Docker/VPS runtime, and external-repo code
execution are all still disabled and out of scope for this milestone.
