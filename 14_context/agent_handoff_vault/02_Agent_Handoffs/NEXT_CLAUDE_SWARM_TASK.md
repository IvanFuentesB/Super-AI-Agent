# Next Claude Swarm Task

Milestone source: N+6.26A Claude swarm / agent-team / ClawTeam / am-will-swarms deep intake
(static research/planning only).

## What N+6.26A produced

- A surfaces catalog (`claude_swarm_surfaces_n6_26a.{md,json}`) separating **official**
  Claude Code swarm mechanisms (subagents, agent view/background `/bg`, agent teams,
  dynamic workflows `/workflows`, skills, hooks, worktrees) from **community** launchers
  (ECC `affaan-m/ecc`, ClawTeam `HKUDS/ClawTeam`, `am-will/swarms`, `affaan-m/claude-swarm`,
  `kyegomez/swarms`).
- Deep-intake notes for ClawTeam and am-will/swarms, an ECC + swarm **separate-profile test
  plan**, and an official-agent-teams deep dive.
- Correction recorded: the operator's `/batch` is not a confirmed command; the real
  background command is `/bg`.

## The two next tracks

### Track A - operator verifies in a separate profile (manual)

Run the safe test order in `ecc_claude_swarm_profile_n6_26a.md` in a **throwaway Claude
profile / disposable VM** (no Ghoti repo access, no secrets, scratch repo only). Capture per
item: automatic vs manual, token cost, worktree need, and whether anything acts without
approval. Confirm repo owners/licenses for ClawTeam, am-will/swarms, claude-swarm. Bring
back only notes.

### Track B - Ghoti dry-run controlled launcher (gated, human-approved)

The first Ghoti-side step is a **dry-run launcher that prints the agent commands it would
run and stops** - no real launch. It should:

- reuse the Hermes Phase-2 `launch_*` wrappers as the seam and the N+6.25A status packet as
  grounding,
- adopt the "waves + bounded rolling pool" idea from am-will/swarms (waves = approval
  points; small pool),
- use worktree-per-agent, one task per agent, no overlapping edits,
- keep `local_only: true`, `live_action: false`, auto-submit blocked.

The first **real** launch (one Claude builder + one Codex auditor on a trivial task) is a
separate, audited, human-approved milestone after the dry-run lands.

## Do not

- Do not enable agent teams, dynamic workflows, hooks, MCP, browser/computer-use, or
  auto-submit.
- Do not clone/install/run ClawTeam, am-will/swarms, claude-swarm, ECC, or kyegomez/swarms
  in the Ghoti environment - separate profile only.
- Do not edit `hermes_status` files until N+6.25B is merged; do not edit `agent_arena`.
- Do not fabricate URLs/licenses; resolve `source_needed`/verify items with the operator.
