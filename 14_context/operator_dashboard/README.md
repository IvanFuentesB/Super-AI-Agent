# Operator Dashboard - configuration contract (N+6.18A)

This folder documents the contract for the Ghoti operator dashboard: a small,
local-only web view that shows runtime status so the user no longer has to read raw
terminal JSON. The dashboard itself lives in
`03_scripts/operator_dashboard/`.

## Status-only by design

The dashboard is **status-only** and read-only. It runs no commands, starts or stops
no processes, mutates no runtime config, reads no secrets, and performs **no live
automation**. It binds the loopback interface (`127.0.0.1`) only and has **no external
access**.

## Endpoints (all GET, read-only)

| Route | Returns |
|-------|---------|
| `GET /` | the static dashboard page |
| `GET /api/status` | the full status payload (shape in `operator_dashboard_status_schema.json`) |
| `GET /api/health` | a lightweight liveness/health object |
| `GET /api/disabled-capabilities` | the disabled-capability list and feature-flag posture |
| `GET /static/app.js`, `GET /static/styles.css` | the page's local assets |

There are no `POST` routes and no command-execution or process-control endpoints.

## Data sources

The status payload is aggregated from existing local, read-only tools and degrades
gracefully if any is missing:

- `03_scripts/status_bridge/ghoti_status_bridge.py --json` - origin/main, branch,
  latest Claude/Codex reports, computer-use sandbox status, Telegram runtime status,
  Hermes integration status, and the next recommended action.
- The interpreter serving the dashboard - reported as the resolved Python; the full
  PATH-shim-skipping resolver is `03_scripts/runtime_activation/ghoti_python_resolver.ps1`.
- `23_configs/runtime_activation.example.json` - the WSL Hermes resume command
  preview (same session).
- `23_configs/ghoti_feature_flags.example.json` - the disabled-capability flags.
- Bounded local probes for `wsl`, `ollama`, and a local `gemma` model.

If the status bridge is unavailable, `/api/status` still returns a complete,
deterministic object.

## Feature flags

The five dashboard flags are defined in `23_configs/ghoti_feature_flags.example.json`
and all default to **false**:

- `operator_dashboard_enabled`
- `operator_dashboard_api_enabled`
- `operator_dashboard_mutations_enabled`
- `operator_dashboard_external_access_enabled`
- `operator_dashboard_command_execution_enabled`

The global invariant is preserved: the only flag that may be `true` in the example
config is `telegram_status_commands_enabled`.

## Future public dashboard

A future public or remote dashboard is a **separate milestone**. It would require
**authentication** and **HTTPS** before any non-local access, and is out of scope
here.
