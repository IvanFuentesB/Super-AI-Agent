# Agent Arena visual simulator (N+6.21A)

The first visual place to watch Ghoti agents and swarms work - as a **simulation**,
before any live overnight automation. It reuses the N+6.18A operator dashboard pattern
(a Python standard-library server, loopback only, static page) and renders a sample
simulation: agent cards, a queue/timeline, task states, branch/worktree per agent,
token/cost estimates, handoff files, and a trace for replay.

## Simulation-first

Nothing here launches an agent, runs a command, or merges/pushes anything. The arena
loads `sample_simulation.json` and draws it. There is **no live execution**.

## Agents shown

ChatGPT strategy brain, Claude builder, Codex auditor, Hermes coordinator, Gemma
summarizer, and the Human approver. Each card shows its role, state (`idle`, `queued`,
`running`, `blocked`, `done`), branch/worktree, current task, and a token/cost
estimate.

## Run it

```
python 03_scripts/agent_arena/ghoti_agent_arena.py --check --json
powershell -ExecutionPolicy Bypass -File 03_scripts/agent_arena/start_agent_arena.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File 03_scripts/agent_arena/start_agent_arena.ps1
# then open http://127.0.0.1:8766/
```

## Endpoints (all GET, read-only)

- `GET /` - the arena page
- `GET /api/health` - a health object
- `GET /api/simulation` - the simulation payload (shape in `agent_arena_schema.json`)
- `GET /api/disabled-capabilities` - what stays disabled

There are no POST routes and no command-execution endpoints. The server binds
`127.0.0.1` only.

## Safety

Local and read-only. No live agent launch, no Claude/Codex/Hermes automation, no
auto-submit, no MCP, no live browser, no email/WhatsApp, no Docker, no external API,
no secrets. The page loads no external CSS/JS/fonts.

## Next milestone

A later milestone may add **real trace ingestion** - reading actual lane-status and
handoff files to replay a real run in the arena - still read-only and behind a flag,
and still with no live unattended swarm until the approval gates exist.
