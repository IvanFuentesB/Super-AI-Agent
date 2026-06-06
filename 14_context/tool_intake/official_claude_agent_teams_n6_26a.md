# Official Claude Code Agent Teams & Orchestration (N+6.26A)

Milestone: N+6.26A
Date: 2026-06-06
Status: static research / planning only. Nothing here is enabled. URLs gathered by
read-only web search (June 2026); version/date specifics are secondary - **verify in the
profile**.

This is the deep dive on the **official** Claude Code orchestration surfaces. It records
what each is, how it is turned on, what it costs, and why Ghoti keeps the launching ones
**off** until a separate audited milestone.

## Subagents

- **What:** a separate worker with its own context window, spawned for a sub-task, reports
  back to the main session.
- **Trigger:** model-invoked (the main agent decides) or via named agent definitions.
- **Cost / worktrees:** moderate tokens (one extra context each); no worktree needed unless
  workers edit in parallel.
- **Ghoti:** guidance_only - Ghoti models roles (Claude builder, Codex auditor) and runs
  them **manually**, one per task. Verified by direct use of the Task/Agent mechanism.
- Source: https://code.claude.com/docs/en/sub-agents (confirm slug).

## Agent view + background agents

- **What:** a single list view to manage many Claude sessions; background sessions run
  asynchronously. **`/bg`** pushes the current session to the background; **`claude --bg
  "<task>"`** launches a fresh background session. The view shows which sessions need input,
  which are working, and which are done.
- **Cost / worktrees:** moderate-to-high (several live sessions); isolate parallel real
  sessions per worktree.
- **Ghoti:** should_stay_disabled - these launch live agents.
- **Correction:** the operator listed `/batch`; no `/batch` command was found. The
  background command is **`/bg`**.
- Source: https://claude.com/blog/agent-view-in-claude-code

## Agent teams

- **What:** coordinate multiple Claude Code instances. One session is the **team lead**
  (assigns tasks, synthesizes); **teammates** each run in their own context and can
  communicate. Reported to support **2-16 agents** on a shared codebase.
- **Enable (reported, verify):** experimental; set env
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` (in `settings.json` or the environment); needs a
  recent Claude Code version. Has known limits around session resume / shutdown.
- **Cost / worktrees:** **high** - many parallel sessions ("what parallel sessions actually
  cost"); use worktree-per-teammate for safe shared-repo edits.
- **Ghoti:** should_stay_disabled - highest blast radius; experimental.
- Source: https://code.claude.com/docs/en/agent-teams

## Dynamic workflows

- **What:** a **JavaScript script** (written by Claude for the task you describe) that
  orchestrates subagents at scale; a runtime runs it in the background while your session
  stays responsive. Shows each phase's agent count, token total, and elapsed time.
- **Status (reported, verify):** research preview; needs a recent Claude Code version and a
  paid plan / Anthropic API / a supported cloud provider.
- **Cost / worktrees:** **high** - orchestrates many subagents; often wants worktrees.
- **Ghoti:** should_stay_disabled - it executes generated JS that launches many agents.
- Source: https://code.claude.com/docs/en/workflows ,
  https://claude.com/blog/introducing-dynamic-workflows-in-claude-code

## Skills, hooks, worktrees (recap)

- **Skills:** model-loaded instructions; low cost; no launching. Ghoti uses repo playbooks
  as skills (guidance_only).
- **Hooks:** event-triggered shell commands via settings; run code; highest-risk building
  block. Ghoti keeps hook-as-validator as an **idea only** (should_stay_disabled).
- **Worktrees:** git worktrees are the isolation substrate; Ghoti already uses one
  branch/worktree per task (enabled). Source: https://git-scm.com/docs/git-worktree.

## Why Ghoti keeps the launching ones off

subagents (parallel), background agents, agent teams, and dynamic workflows all launch real
agents and can edit the repo and spend real tokens. Ghoti's safety model requires
human-approved, dry-run-first, worktree-isolated launching. Until the controlled-launcher
milestone, these stay **disabled** and are exercised only in a **separate throwaway Claude
profile** (see `ecc_claude_swarm_profile_n6_26a.md`).
