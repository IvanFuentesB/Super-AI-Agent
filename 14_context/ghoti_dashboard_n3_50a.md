# Ghoti Dashboard — N+3.50A

Script: `03_scripts/ghoti_dashboard.py`
Dashboard card: `14_context/ghoti_dashboard_card.md`

## What It Does
Stdlib-only local orchestrator card generator. Reads local files only — no external calls.
Produces machine-readable JSON and human-readable markdown dashboard cards.

## Commands
| Command | Effect |
|---|---|
| `--status` | Compact summary to stdout |
| `--json` | Machine-readable JSON status |
| `--card --dry-run` | Preview markdown card |
| `--card --apply` | Write card to `14_context/ghoti_dashboard_card.md` |

## Data Sources
- `14_context/agent_lanes/active_locks.jsonl`
- `14_context/agent_lanes/lane_status.jsonl`
- `14_context/prompt_bus/outbox/`
- `14_context/obsidian_vault/`
- `14_context/compact_memory/`
- `21_repos/third_party/evals/ruflo/package.json` (read-only)
- `ollama list` (read-only, local process)
- `git branch --show-current` (read-only)

## Dashboard UI Route
`GET /api/ghoti/local-orchestrator/status` — added to dashboard_mvp server.js
Card ID: `local-orchestrator-card` in index.html
Sidebar: "Local Orchestrator" link
JS: `renderLocalOrchestratorCard()` + `refreshLocalOrchestrator()` in app.js

## Safety
Read-only. No live actions. No approve/execute/install/post/pay buttons.
