# Ghoti Agent Arena - Visual Simulator (N+6.21A)

The first visual place to watch Ghoti agents and swarms work - as a **simulation**,
before any live overnight automation. It reuses the N+6.18A operator dashboard pattern
(a Python standard-library server bound to the loopback interface, serving a static
page plus read-only GET JSON endpoints) and renders a sample simulation.

## Simulation-first

This is **simulation-first**: the arena loads `sample_simulation.json` and draws it.
It launches no agent, runs no command, merges or pushes nothing, and `live_execution`
is forced `false` in every payload. There is **no live automation** of Claude, Codex,
or Hermes in this milestone.

## What it shows

- **Agent cards** for the six roles: ChatGPT strategy brain, Claude builder, Codex
  auditor, Hermes coordinator, Gemma summarizer, and the Human approver - each with its
  role, **state** (`idle`, `queued`, `running`, `blocked`, `done`), branch/worktree,
  current task, and a token/cost **estimate**.
- A **queue / timeline** of tasks and state transitions.
- **Totals**: agent count and simulated token/cost estimates.
- **Handoff files** passed between agents.
- A **trace / replay** of the run's steps.

## Run it

```
python 03_scripts/agent_arena/ghoti_agent_arena.py --check --json
python 03_scripts/agent_arena/ghoti_agent_arena.py --simulation-json
powershell -ExecutionPolicy Bypass -File 03_scripts/agent_arena/check_agent_arena.ps1
powershell -ExecutionPolicy Bypass -File 03_scripts/agent_arena/start_agent_arena.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File 03_scripts/agent_arena/start_agent_arena.ps1
# then open http://127.0.0.1:8766/
```

## Endpoints (all GET, read-only)

| Route | Returns |
|-------|---------|
| `GET /` | the arena page |
| `GET /api/health` | a health object |
| `GET /api/simulation` | the simulation payload (shape in `14_context/agent_arena/agent_arena_schema.json`) |
| `GET /api/disabled-capabilities` | what stays disabled |

There are **no POST routes** and no command-execution endpoints. The server binds
`127.0.0.1` only; a non-loopback host is refused unless an explicit opt-in flag is
passed, and that flag is left disabled.

## Safety

Local and read-only. No live agent launch, no Claude/Codex/Hermes automation, no
auto-submit, no MCP, no live browser, no OS click/type, no account login, no
email/WhatsApp, no Docker, no external API, no secrets. The page loads no external
CSS/JS/fonts, and the server makes no subprocess call at all.

## Next milestone

A later milestone may add **real trace ingestion**: reading actual lane-status and
handoff files to replay a real run in the arena. That stays read-only, behind a
feature flag, and there is still **no live unattended swarm** until the approval gates
(kill switch, no overlapping worktrees, auto-stop on errors, logs, no auto merge/push)
exist. Until then, the arena only simulates.
