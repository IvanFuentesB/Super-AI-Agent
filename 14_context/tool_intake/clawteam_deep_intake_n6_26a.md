# ClawTeam - Deep Intake (N+6.26A)

Milestone: N+6.26A
Date: 2026-06-06
Status: static research / planning only. No clone, no install, no execution, no launch.
Source recorded by read-only web search (June 2026); verify before any intake.

- Repo (verify): `https://github.com/HKUDS/ClawTeam`
- Confidence: web_verified (existence/identity); license + exact behavior: verify.

## What it is (reported)

ClawTeam is an **"agent swarm intelligence"** launcher: a human gives the goal on one
command line, and an agent team orchestrates the rest toward full automation. It is
reported to be **CLI-agent agnostic** - compatible with Claude Code, Codex, OpenClaw,
nanobot, and Cursor, which act as team members. Reported baseline: config management,
multi-user workflows, a Web UI, P2P transport, and team templates. All state is reported to
live locally as JSON under a `~/.clawteam/` home folder - **no database, no server, no
cloud**.

## Variants / related (verify each)

- `win4r/ClawTeam-OpenClaw` - a fork adapted for OpenClaw as the default agent.
- `zeyuyang8/claw-team` - a mirror/variant.
- Related but **distinct**: `The-Swarm-Corporation/ClawSwarm`, `swarmclawai/swarmclaw`.

## Why it matters to Ghoti

ClawTeam is the closest match to the operator's "one command launches a coordinated agent
team" goal, and its **local-JSON-state, no-server** design is philosophically aligned with
Ghoti (local, file-based, no cloud). Good ideas to study:

- one-command goal -> orchestrated team,
- local JSON state instead of a server/DB,
- CLI-agent-agnostic team membership (Claude / Codex as members).

## Why it stays disabled for Ghoti (for now)

ClawTeam **launches real agents** and aims for "full automation" - exactly the
controlled-launcher risk surface. For Ghoti it is `should_stay_disabled`:

- No clone, no install, no run in the Ghoti environment.
- License must be verified before any intake.
- "Full automation" must be reduced to **dry-run-first, human-approved, worktree-per-agent**
  before any Ghoti use.

## How to evaluate it safely

In a **separate throwaway Claude profile / disposable VM** with no Ghoti repo access and no
real accounts/secrets: read the README, inspect how it spawns agents and where it writes
state, run it only against a scratch repo with junk data, and record notes. Bring only the
**notes** back into Ghoti, never the executable project. See
`ecc_claude_swarm_profile_n6_26a.md` for the order.

## Open questions for the operator

- Exact repo/owner and license (confirm `HKUDS/ClawTeam` vs a fork).
- How it isolates parallel agents (worktrees? containers?).
- What it can do without approval (auto-commit? auto-push? network?).
