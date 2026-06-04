# Ghoti Agent Arena - Swarm Simulator Plan (N+6.21A)

A visual place to plan and **simulate** multi-agent work before any live multi-agent
run. This is **simulation-first**: simulate swarms before live swarms, and run no
unattended live swarm until the approval gates exist.

## Visual model

- **Agent nodes / cards** - each agent is a card showing role, task, branch, worktree,
  and status.
- **Queue / timeline** - a timeline of tasks moving queued -> in progress -> audit ->
  merge-gate.
- **Branch / worktree per agent** - every simulated agent maps to its own feature
  branch and repo-contained worktree (one-agent-per-task).
- **Token / cost estimate** - each card estimates tokens + cost before anything runs,
  so a swarm's budget is visible up front.

## Simulation-first

- A **simulated** swarm launches no agents. It generates the prompt packets, the
  planned branches/worktrees, and the per-card token/cost estimate, and renders the
  arena - all without launching any agent.
- Only after the approval gates are in place (kill switch, no overlapping worktrees,
  auto-stop on errors, logs, no auto merge/push) may a guarded, operator-confirmed live
  run be considered in a later milestone.

## Inspiration candidates (study only, no install)

- `generative_agents` - a simulated agent society; supports the simulate-before-live
  idea.
- AgentPrism-style traces - per-agent observability traces, useful for the timeline.
- SwarmClaw-style runtime dashboard - a swarm dashboard layout for the arena cards.

## N+6.21A implementation scope

- A local, read-only arena view that reuses the N+6.18A operator dashboard pattern
  (Python standard-library server, loopback only, no external assets).
- Cards + timeline fed by **simulated** task plans (no live agents).
- A per-card token/cost estimator.
- Everything behind `agent_arena_simulator_enabled` (off by default).

## What stays disabled

No live unattended swarm, no automatic agent launch, no auto merge/push. The arena
simulates and plans; the human approves and runs.
