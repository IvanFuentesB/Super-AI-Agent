# Next Skills / Swarms Task

Milestone source: N+6.24A skills / ECC / swarms capability map + swarm repo intake
(static planning only).

## What N+6.24A produced

- A skills capability map for Claude / Codex / Hermes (skills vs agents vs commands vs
  hooks) under `14_context/skills/*_N6_24A.md`.
- An ECC = Everything Claude Code explainer (adapt-not-install; separate-profile test).
- A swarm-launcher repo intake (`14_context/tool_intake/swarm_launcher_repo_intake_n6_24a.{md,json}`)
  and new backlog items.
- A Memory Palace / PAO future product lane (tier-1-last).

## The next step (gated, human-approved)

The next big step in the safe progression is the **controlled launcher** - the first time
Ghoti actually launches/coordinates agents:

`simulation -> trace ingestion -> static repo intake (done) -> controlled launcher (NEXT) -> approved-window bridge -> supervised overnight loop`

A controlled-launcher milestone must:

- Be **dry-run-first**: print the exact command(s) it would run, then stop. No real launch
  until a separate human approval.
- Use **one agent per task on its own branch/worktree** (worktree-per-agent), no
  overlapping edits.
- Reuse Hermes Phase-2 `launch_*` wrappers as the seam; keep `local_only: true` and
  `live_action: false` logging.
- Verify the swarm candidates first: resolve `source_needed` repos (ClawTeam,
  `am-will/swarms`, multiswarm, Codex skill agent-launching) by having the operator supply
  exact URLs/licenses; static-inspect before anything else.
- Keep all hard limits: no installs, no MCP, no browser/computer-use, no auto-submit, no
  secrets, no live account/API/money actions.

## Do not

- Do not edit `03_scripts/agent_arena` or `14_context/agent_arena` until N+6.23B is merged.
- Do not install ECC into the working Claude profile; if exercised, use a separate
  throwaway profile/VM with no Ghoti repo access and no secrets.
- Do not fabricate URLs; resolve `source_needed` items with the operator.
