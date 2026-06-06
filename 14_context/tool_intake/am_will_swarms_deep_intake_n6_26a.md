# am-will/swarms - Deep Intake (N+6.26A)

Milestone: N+6.26A
Date: 2026-06-06
Status: static research / planning only. No clone, no install, no execution, no launch.
Source recorded by read-only web search (June 2026); verify before any intake.

- Repo (verify): `https://github.com/am-will/swarms`
- Confidence: web_verified (existence/identity); license + exact behavior: verify.
- **Disambiguation:** this is a **Claude-Code skills** repo and is NOT the enterprise
  framework `kyegomez/swarms` (swarms.ai). Do not conflate them.

## What it is (reported)

`am-will/swarms` provides **multi-agent orchestration *skills* for Claude Code and Codex** -
i.e. it works through the official **skills** + **subagents** mechanisms rather than as a
separate server. Reported skills:

- **super-swarm** - top-level orchestration skill.
- **swarm-planner** - works best in **Plan Mode** (uses Codex's "Request User Input" tool,
  available in Plan Mode).
- **parallel-task** - parses a plan file and delegates tasks in parallel using a **rolling
  pool of up to 15 concurrent subagents**, launching new work as slots free up.

It is reported to trade some parallelism for simplicity (waves run sequentially; tasks run
in parallel within a wave; dependencies are explicit), needing no scripts or conflict
resolution.

## Why it matters to Ghoti

This is the **closest pattern to Ghoti's own "re-express as skills, gate execution"**
approach. It shows how to do swarms **through skills + subagents** (official mechanisms)
instead of a heavyweight launcher - which is exactly the lighter path Ghoti prefers. The
"wave + rolling pool" plan-execution model is a clean reference for a future Ghoti
controlled launcher (waves = approval points; pool = bounded concurrency).

## Why it stays disabled for Ghoti (for now)

The **parallel-task** skill **launches real subagents** (up to a pool of 15). For Ghoti it
is `study_then_guidance`:

- No clone, no install, no run in the Ghoti environment.
- License must be verified before any intake.
- If adopted, only the **patterns** (wave planning, bounded rolling pool, explicit
  dependencies) get re-expressed as a Ghoti skill - and only dry-run-first, human-approved.

## How to evaluate it safely

In a **separate throwaway Claude profile** with no Ghoti repo access and no secrets: read
the SKILL.md files, exercise `swarm-planner` in Plan Mode and `parallel-task` on a scratch
plan against a junk repo, and record how many subagents it launches and the token cost.
Bring only the notes back into Ghoti.

## Open questions for the operator

- License of `am-will/swarms`.
- Whether `parallel-task` can write/commit without approval.
- How its "waves" map onto Ghoti's per-milestone approval gates.
