# Claude Swarm Surfaces - Official vs Community (N+6.26A)

Milestone: N+6.26A
Date: 2026-06-06
Status: static research / planning only. No install, no clone, no execution, no live agent
launch. Structured data: `claude_swarm_surfaces_n6_26a.json`.

This maps how Claude swarms are done as of June 2026, separating **official Claude Code
mechanisms** from **community launcher repos**. URLs were gathered by read-only web search
in June 2026; the operator should verify them before any intake. Official features are also
grounded in this agent's own operating context (it uses subagents, worktrees, skills, slash
commands, and the settings hook mechanism directly). Reported version numbers and dates are
secondary and marked "verify".

## Claude-side vs Ghoti-side swarm (the key distinction)

- **Claude-side swarm:** features that run *inside Claude Code / the Claude profile* -
  subagents, agent view / background agents, agent teams, dynamic workflows, skills, hooks.
  These can launch real agents in the operator's profile.
- **Ghoti-side swarm:** a *repo-controlled launcher/coordinator* that drives Claude / Codex
  / Hermes from this repo (worktree-per-agent, approval gates). This is **planned and
  gated** - it does not exist yet.

N+6.26A studies both so the future Ghoti launcher can reuse the good ideas without turning
on anything unsafe.

## Official Claude Code surfaces

| Surface | Auto/Manual | Token cost | Needs worktrees | Can launch real agents | Ghoti default |
|---------|-------------|-----------|-----------------|------------------------|---------------|
| subagents | model-invoked | moderate | no (helps if parallel) | yes | guidance_only |
| agent view + background (`/bg`) | manual then async | moderate-high | recommended | yes | should_stay_disabled |
| agent teams | manual then semi-auto | high | yes | yes | should_stay_disabled |
| dynamic workflows (`/workflows`) | manual then auto | high | often | yes | should_stay_disabled |
| `/batch` (operator-named) | n/a | n/a | n/a | no (unconfirmed) | needs_verification |
| skills | model-invoked | low | no | no | guidance_only |
| hooks | event-triggered | n/a (runs code) | no | no (runs code) | should_stay_disabled |
| worktrees | manual (git) | none | is the mechanism | no | enabled |

Notes:

- **`/batch` is not confirmed.** The documented background command is **`/bg`** (and
  `claude --bg "<task>"`); dynamic workflows use **`/workflows`**. Treat "/batch" as a
  mislabel until verified in the profile.
- **agent teams** are reported experimental (enabled by an env var, recent Claude Code
  version, 2-16 agents). **dynamic workflows** are a research preview that runs Claude-
  generated JavaScript. Both launch many real agents and cost the most tokens, so both stay
  off for Ghoti.

## Community / repo / plugin surfaces

| Surface | Repo | What it is | Ghoti default |
|---------|------|-----------|---------------|
| ECC / Everything Claude Code | `affaan-m/ecc` | bundle of commands/agents/skills/hooks | adapt_guidance_only |
| ClawTeam | `HKUDS/ClawTeam` | one-command agent-swarm launcher | should_stay_disabled |
| am-will/swarms | `am-will/swarms` | orchestration **skills** for Claude Code/Codex | study_then_guidance |
| claude-swarm | `affaan-m/claude-swarm` | multi-agent orchestration + terminal UI | should_stay_disabled |
| swarms (enterprise) | `kyegomez/swarms` | the big, different-owner framework | tier2_later |

Notes:

- `am-will/swarms` (Claude-Code skills) is **distinct** from `kyegomez/swarms` (the
  enterprise framework at swarms.ai). Do not conflate them.
- `affaan-m/claude-swarm` is by the same author as `affaan-m/ecc`; its terminal-UI
  visualization parallels Ghoti's Agent Arena.
- Deeper notes: `clawteam_deep_intake_n6_26a.md`, `am_will_swarms_deep_intake_n6_26a.md`,
  `ecc_claude_swarm_profile_n6_26a.md`, `official_claude_agent_teams_n6_26a.md`.

## What costs more tokens

Highest first: **agent teams** and **dynamic workflows** (many parallel sessions /
orchestrated subagents) > **background agents** (several live sessions) > **subagents**
(one extra context per worker) > **skills** (loaded only when relevant) > **worktrees /
hooks** (no model cost). Parallel real sessions are the expensive part - budget before
enabling.

## What needs worktrees

Any surface that runs **parallel real agents editing the same repo** wants worktree-per-
agent: agent teams, background/parallel sessions, and (often) dynamic workflows. Subagents
that only read or report can share the tree. Ghoti already uses one branch/worktree per
task, so this maps cleanly onto the future launcher.

## What can launch real agents (and so stays disabled for Ghoti)

subagents, background agents (`/bg`), agent teams, dynamic workflows, and every community
launcher (ECC, ClawTeam, am-will/swarms, claude-swarm, kyegomez/swarms). All stay
**disabled** for Ghoti until the controlled-launcher milestone. skills and worktrees do not
launch agents by themselves; hooks run code but do not launch agents.

## What must be tested in a separate Claude profile

agent teams, dynamic workflows, background agents, hooks, and any community launcher/skill
(ECC, ClawTeam, am-will/swarms, claude-swarm). See the safe test order in
`docs/GHOTI_N6_26A_CLAUDE_SWARM_DEEP_INTAKE.md` and `ecc_claude_swarm_profile_n6_26a.md`.

## Safety

Static intake only. Nothing here is installed, cloned, executed, or launched. No agent
teams, dynamic workflows, or hooks are enabled. No MCP, no browser/computer-use, no
secrets, no real local paths. ECC = Everything Claude Code (not elliptic curve
cryptography). Unverified items are `source_needed: true` with a null URL; no URL is
fabricated.
