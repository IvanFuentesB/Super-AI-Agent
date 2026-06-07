# Ghoti N+6.26A - Claude Swarm / Agent-Team / ClawTeam / am-will-swarms Deep Intake (Report)

## Verdict

IMPLEMENTED_AND_PUSHED

## Lane

- Branch: `feat/ghoti-agent-claude-n6-26a-claude-swarm-deep-intake`
- Worktree: `<repo>/.claude/worktrees/n6_26a_claude_swarm_deep_intake`
- Base main: `origin/main` `7a6e6b3` (docs: record n6.24b skills ecc swarms merge gate)
- Codex audit target: `audit/ghoti-agent-codex-n6-26a-claude-swarm-deep-intake`
- Commit: `docs(ghoti): add claude swarm deep intake`

## Start condition

- `git fetch origin --prune`; `origin/main` = `7a6e6b3`.
- N+6.24B (Skills/ECC/Swarms map) confirmed on main (skills map + swarm intake json present).
- N+6.25B (Hermes status packet) **not merged** -> this lane did **not** edit any
  `03_scripts/hermes_status` or `14_context/hermes_status` file.
- Clean worktree created from `origin/main`; dirty primary worktree untouched.

## Mission

Static research/planning only: document how Claude swarms are done as of June 2026,
separating official Claude Code mechanisms from community launcher repos. No install, no
clone, no execution, no live agent launch, no agent teams / dynamic workflows / hooks
enabled.

## Research method (honesty)

Official surfaces are grounded in this agent's direct operating context (it uses subagents,
worktrees, skills, slash commands, and the settings hook mechanism) plus read-only web
search (June 2026) for first-party doc URLs. Community repos are recorded with their URLs
from web search. Reported version numbers/dates are secondary and marked "verify". No URL
is fabricated; unverified items are `source_needed: true` with a null URL. URLs containing
numeric IDs were avoided.

## Files added

- `docs/GHOTI_N6_26A_CLAUDE_SWARM_DEEP_INTAKE.md`
- `14_context/tool_intake/claude_swarm_surfaces_n6_26a.md`
- `14_context/tool_intake/claude_swarm_surfaces_n6_26a.json`
- `14_context/tool_intake/clawteam_deep_intake_n6_26a.md`
- `14_context/tool_intake/am_will_swarms_deep_intake_n6_26a.md`
- `14_context/tool_intake/ecc_claude_swarm_profile_n6_26a.md`
- `14_context/tool_intake/official_claude_agent_teams_n6_26a.md`
- `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_CLAUDE_SWARM_TASK.md`
- `01_projects/runtime_mvp/tests/test_n6_26a_claude_swarm_deep_intake.py`
- `14_context/claude_n6_26a_claude_swarm_deep_intake.md` (this report)

Purely additive (no existing file edited). `hermes_status`, `agent_arena`, and the N+6.24A
skills/swarm files were read for context only, never edited.

## Official Claude swarm summary

- **subagents** - own-context workers; model-invoked; moderate tokens; guidance_only.
- **agent view + background agents** - `/bg`, `claude --bg`; async sessions; disabled.
- **agent teams** - team lead + teammates (reported 2-16); experimental env
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`; high cost; disabled.
- **dynamic workflows** - Claude-written JS orchestrates subagents (`/workflows`); research
  preview; high cost; disabled.
- **skills** (guidance_only), **hooks** (disabled; runs code), **worktrees** (enabled; git
  isolation; already Ghoti's pattern).
- **Correction:** the operator's `/batch` is **not** a confirmed command; the background
  command is `/bg`.

## Community swarm repo summary

- **ECC / Everything Claude Code** (`affaan-m/ecc`) - bundle; adapt as guidance only.
- **ClawTeam** (`HKUDS/ClawTeam`) - one-command launcher; local-JSON state; disabled.
- **am-will/swarms** (`am-will/swarms`) - orchestration **skills** (super-swarm,
  swarm-planner, parallel-task up to 15 subagents); most Ghoti-aligned; study then guidance.
  Distinct from the enterprise framework `kyegomez/swarms`.
- **affaan-m/claude-swarm** - orchestration + terminal UI (parallels the Agent Arena).
- ECC = Everything Claude Code, not elliptic curve cryptography.

## Safe test order (separate throwaway profile)

1. subagents -> 2. skills -> 3. worktrees -> 4. background agents (`/bg`) -> 5. agent view
-> 6. agent teams (small) -> 7. dynamic workflows (read the generated JS first) -> 8. hooks
(no-op) -> 9. community launchers (ECC, am-will/swarms, ClawTeam, claude-swarm), license
verified, sandbox only. Record automatic/manual, token cost, worktree need, and whether
anything acts without approval. Bring back only notes.

## Future Ghoti controlled launcher (gated)

dry-run launcher (prints commands, stops) -> bounded "waves + rolling pool" plan ->
worktree-per-agent -> human approval gate -> first real launch (1 builder + 1 auditor on a
trivial task) as a separate audited milestone -> larger teams only later, never
overnight-autonomous without a dedicated milestone.

## Validation

- `python -m unittest discover -p "test_n6_26a_*.py"` -> all tests pass.
- `public_repo_security_audit.py --run --json` -> `failed_checks: 0`,
  `safe_to_make_public: true`, 0 blockers.
- `ghoti_product_launcher.py --status` -> ok; `--context-pack` and `--repo-map` -> ok.
- `git diff --check` / `git show --check` clean; generated residue restored.
- Surfaces JSON: 8 official + 5 community surfaces; all required fields; `source_url` null
  whenever `source_needed` true.

## Safety summary

- Static intake only. No install, clone, execution, or live agent launch.
- No agent teams, dynamic workflows, or hooks enabled. No MCP, no browser/computer-use, no
  auto-submit, no Docker.
- No secrets/tokens/cookies/auth files. No real local paths/usernames/private images
  (placeholders only). No fabricated URLs.
- `hermes_status` not edited (N+6.25B not merged); `agent_arena` not edited.

## Final verdict

IMPLEMENTED_AND_PUSHED
