# Next Controlled Swarm Task

Milestone source: N+6.27A repo-backed controlled swarm launcher (dry-run only).

## What N+6.27A produced

- `03_scripts/swarm_launcher/ghoti_swarm_launcher.py` - reads a task spec and emits a
  **dry-run plan**: scope validation, role assignment, file-ownership overlap detection,
  placeholder worktree paths, dependency waves, kill-switch/approval gates, and an
  Agent-Arena-shaped status block. It launches nothing.
- Task/plan schemas, three example task specs, a PowerShell check, a README, and a
  repo-inspiration attribution manifest/report (patterns adapted from `am-will/swarms`,
  `HKUDS/ClawTeam`, `affaan-m/claude-swarm`, `affaan-m/ecc`; no code vendored).

## The next step (gated, human-approved)

The next milestones move from plan to a **first, tiny real launch** - each its own audited,
human-approved step:

1. **Kill switch + approval implementation (still no launch):** a repo-local approval record
   and a kill file/flag the launcher would honor; dry-run still the only mode.
2. **Agent Arena integration:** render the dry-run `arena_status` in the Agent Arena
   (read-only) so a human can see the proposed swarm before approving.
3. **First single-pair real launch (separate audited milestone):** one Claude builder + one
   Codex auditor on a **trivial** task, worktree-per-agent, fully logged, `local_only: true`,
   with the kill switch armed and human approval required for each step. Auto-submit stays
   blocked; main merge stays Codex-gate-only.
4. **Bounded growth:** only after the single pair is proven, allow a small bounded pool
   (e.g. 2-3), still human-gated. Never overnight-autonomous without a dedicated milestone.

## Do not

- Do not enable live launching, process spawning, hooks, MCP, browser/computer-use, or
  auto-submit in the launcher.
- Do not create real git worktrees or start agent processes from this script.
- Do not vendor third-party repo code; keep clones in the gitignored sandbox only.
- Do not edit the N+6.26A Claude swarm deep-intake files until N+6.26B is merged.
