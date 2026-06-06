# Ghoti N+6.26A - Claude Swarm / Agent-Team / ClawTeam / am-will-swarms Deep Intake

## Summary

N+6.26A is **static research and planning only**: it documents how Claude swarms are done
as of June 2026, separating **official Claude Code mechanisms** from **community launcher
repos**, and lays out a safe path for the operator to test them in a separate profile and
for Ghoti to build a controlled launcher later. **No install, no clone, no execution, no
live agent launch, no agent teams / dynamic workflows / hooks enabled.**

URLs were gathered by read-only web search in June 2026 and are recorded for the operator
to verify. Official features are also grounded in this agent's direct operating context
(it uses subagents, worktrees, skills, slash commands, and the settings hook mechanism).
Reported version numbers and dates are secondary and marked "verify".

## Files

| Area | File |
|------|------|
| Surfaces catalog (md + json) | `14_context/tool_intake/claude_swarm_surfaces_n6_26a.{md,json}` |
| Official agent teams deep dive | `14_context/tool_intake/official_claude_agent_teams_n6_26a.md` |
| ClawTeam | `14_context/tool_intake/clawteam_deep_intake_n6_26a.md` |
| am-will/swarms | `14_context/tool_intake/am_will_swarms_deep_intake_n6_26a.md` |
| ECC + separate-profile test plan | `14_context/tool_intake/ecc_claude_swarm_profile_n6_26a.md` |
| Handoff | `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_CLAUDE_SWARM_TASK.md` |
| Test | `01_projects/runtime_mvp/tests/test_n6_26a_claude_swarm_deep_intake.py` |

## Claude-side vs Ghoti-side swarm

- **Claude-side swarm:** runs *inside Claude Code / the Claude profile* - subagents, agent
  view / background agents, agent teams, dynamic workflows, skills, hooks. Can launch real
  agents in the operator's profile.
- **Ghoti-side swarm:** a *repo-controlled launcher/coordinator* that drives Claude / Codex
  / Hermes from this repo (worktree-per-agent, approval gates). **Planned and gated; does
  not exist yet.**

## Official Claude swarm summary

- **subagents** - separate workers with their own context; model-invoked; moderate tokens;
  guidance_only for Ghoti.
- **agent view + background agents** - manage many sessions; `/bg` and `claude --bg` run
  async sessions; should_stay_disabled. (The operator's **`/batch` is not a confirmed
  command**; the real one is `/bg`.)
- **agent teams** - multiple Claude instances (team lead + teammates, reported 2-16);
  experimental env `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`; high token cost; should_stay_disabled.
- **dynamic workflows** - Claude-written JavaScript orchestrates subagents at scale
  (`/workflows`); research preview; high cost; should_stay_disabled.
- **skills** - model-loaded instructions; low cost; guidance_only.
- **hooks** - event-triggered shell commands via settings; run code; should_stay_disabled
  (hook-as-validator idea only).
- **worktrees** - git isolation substrate; already enabled in Ghoti (one branch/worktree
  per task).

## Community swarm repo summary

- **ECC / Everything Claude Code** (`affaan-m/ecc`) - bundle of commands/agents/skills/
  hooks; adapt as guidance only; do not install. (NOT elliptic curve cryptography.)
- **ClawTeam** (`HKUDS/ClawTeam`) - one-command agent-swarm launcher; local-JSON state, no
  server; should_stay_disabled.
- **am-will/swarms** (`am-will/swarms`) - multi-agent orchestration **skills** for Claude
  Code/Codex (super-swarm, swarm-planner, parallel-task up to 15 subagents); the lightest,
  most Ghoti-aligned pattern; study then guidance. Distinct from `kyegomez/swarms`.
- **affaan-m/claude-swarm** - orchestration + terminal UI (parallels the Agent Arena).
- **kyegomez/swarms** - the enterprise framework (swarms.ai); recorded to disambiguate;
  tier2_later.

## What is automatic vs manual

- **Manual to start:** background agents, agent teams, dynamic workflows, every community
  launcher (a human triggers them).
- **Automatic once started:** agent teams (teammates coordinate), dynamic workflows
  (runtime executes the script), `parallel-task` (rolling pool).
- **Model-invoked:** subagents, skills (the model decides to use them).
- **Event-triggered:** hooks (fire on lifecycle events).

## What costs more tokens

agent teams and dynamic workflows (most) > background/parallel sessions > subagents >
skills > worktrees/hooks (no model cost). Parallel real sessions are the expensive part.

## What needs worktrees

agent teams, parallel/background sessions, and (often) dynamic workflows want
**worktree-per-agent**. Subagents that only read can share the tree. Ghoti already uses one
worktree per task.

## What can launch real agents (stays disabled)

subagents (parallel), background agents, agent teams, dynamic workflows, ECC, ClawTeam,
am-will/swarms, claude-swarm, kyegomez/swarms. All **disabled** for Ghoti until the
controlled-launcher milestone.

## What must be tested in a separate profile

agent teams, dynamic workflows, background agents, hooks, ECC, ClawTeam, am-will/swarms,
claude-swarm. See the ordered plan in `ecc_claude_swarm_profile_n6_26a.md`.

## Safe test order (separate throwaway profile)

1. subagents -> 2. skills -> 3. worktrees -> 4. background agents (`/bg`) -> 5. agent view
-> 6. agent teams (small) -> 7. dynamic workflows (read the generated JS first) -> 8. hooks
(no-op) -> 9. community launchers (ECC, am-will/swarms, ClawTeam, claude-swarm), license
verified, in the sandbox only. Record automatic/manual, token cost, worktree need, and
whether anything acts without approval. Bring back only notes.

## Exact future path for the Ghoti controlled launcher

1. **Dry-run launcher (no execution):** a repo script that prints the exact agent commands
   it *would* run (per task, per worktree) and stops. Reuse the Hermes Phase-2 `launch_*`
   wrappers as the seam and the N+6.25A status packet as grounding.
2. **Bounded plan model:** adopt the am-will/swarms "waves + rolling pool" idea - waves are
   **approval points**, the pool bounds concurrency (small, e.g. 2-3 to start).
3. **Worktree-per-agent:** one branch/worktree per launched agent; no overlapping edits.
4. **Human approval gate:** a human approves each wave before any real launch; auto-submit
   stays blocked.
5. **First real launch (separate milestone):** one Claude builder + one Codex auditor on a
   trivial task, fully logged, `local_only: true`, with a kill path.
6. **Only later:** larger teams / dynamic workflows, still human-gated, never overnight-
   autonomous without a dedicated audited milestone.

## Safety posture

Static intake only. Nothing installed, cloned, executed, or launched. No agent teams,
dynamic workflows, or hooks enabled. No MCP, no browser/computer-use, no auto-submit, no
Docker, no secrets, no real local paths/usernames. ECC = Everything Claude Code (not
elliptic curve cryptography). Unverified items are `source_needed: true` with a null URL;
no URL is fabricated. This lane does not edit `hermes_status` (N+6.25B not merged) or any
`agent_arena` file.
