# Ghoti N+6.24A - Skills / ECC / Swarms Capability Upgrade + Swarm Repo Intake (Report)

## Verdict

IMPLEMENTED_AND_PUSHED

## Lane

- Branch: `feat/ghoti-agent-claude-n6-24a-skills-ecc-swarms-capability`
- Worktree: `<repo>/.claude/worktrees/n6_24a_skills_ecc_swarms_capability`
- Base main: `origin/main` `61980aa` (docs: record n6.22b tool backlog intake merge gate)
- Codex audit target: `audit/ghoti-agent-codex-n6-24a-skills-ecc-swarms-capability`
- Commit: `docs(ghoti): add skills ecc swarms capability map`

## Mission

Static intake and planning only: map Claude / Codex / Hermes skills, explain ECC =
Everything Claude Code (adapt-not-install), intake real swarm-launcher repo candidates and
new backlog items, and prepare the path to real agent launching later. Launches nothing,
installs nothing, clones nothing, executes nothing.

## Start condition

- `git fetch origin --prune`; `origin/main` = `61980aa`.
- N+6.22B (Tool Backlog Intake v2 + Repo Memory Vault v1) confirmed on main
  (`14_context/memory_vault/README.md` and `tool_intake/tool_backlog_inventory_n6_22a.json`
  present on `origin/main`).
- N+6.23B (Codex audit of N+6.23A Agent Arena trace ingestion) **not merged yet** -> this
  lane does **not** edit any `03_scripts/agent_arena` or `14_context/agent_arena` file.
- Clean worktree created from `origin/main`; the dirty primary worktree was not touched.

## Files added

- `docs/GHOTI_N6_24A_SKILLS_ECC_SWARMS_CAPABILITY.md`
- `14_context/skills/SKILLS_CAPABILITY_MAP_N6_24A.md`
- `14_context/skills/CLAUDE_SKILLS_AND_AGENTS_N6_24A.md`
- `14_context/skills/CODEX_AGENTS_AND_SKILLS_N6_24A.md`
- `14_context/skills/HERMES_SKILLS_AND_MEMORY_N6_24A.md`
- `14_context/skills/ECC_EVERYTHING_CLAUDE_CODE_N6_24A.md`
- `14_context/tool_intake/swarm_launcher_repo_intake_n6_24a.md`
- `14_context/tool_intake/swarm_launcher_repo_intake_n6_24a.json`
- `14_context/tool_intake/memory_palace_pao_app_lane_n6_24a.md`
- `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_SKILLS_SWARMS_TASK.md`
- `01_projects/runtime_mvp/tests/test_n6_24a_skills_ecc_swarms_capability.py`
- `14_context/claude_n6_24a_skills_ecc_swarms_capability.md` (this report)

No existing file was edited (purely additive). No `agent_arena` file touched.

## Skills capability summary

- **Four building blocks** clarified for Claude: **skill** (instructions the model loads),
  **agent/subagent** (a separate worker with its own context - the swarm mechanism),
  **command** (a named prompt a person triggers), **hook** (event-triggered automation
  that runs code - highest risk, NOT enabled).
- **Codex:** `AGENTS.md` (repo rules Codex reads, the Codex-facing `CLAUDE.md`) vs Codex
  skills (reusable recipes). Codex stays audit-only/manual; the agent-launching "conductor"
  skill is planned and gated.
- **Hermes:** "skills" = an allowlist of approved wrappers (read-only phase 1, dry-run
  phase 2); memory = Obsidian vault + status brain + memory vault; visible tool names are
  not enablement.
- Everything stays **guidance/manual**; runtime wiring needs a separate audited milestone.

## ECC status

- ECC = **Everything Claude Code** (commands/agents/skills/hooks/scanner patterns), **not**
  elliptic curve cryptography.
- Recorded source `https://github.com/affaan-m/ecc` from prior N+6.19A intake (medium
  confidence; re-verify). No new URL fabricated.
- **Ghoti adapts, does not install** (ECC hooks execute code -> blast radius in the real
  profile). Full ECC can be exercised in a **separate throwaway Claude profile / VM** with
  no Ghoti repo access and no secrets; only notes return.

## Swarm repo candidates

7 candidates recorded (study-only): ClawTeam; `swarms` (operator handle `am-will/swarms`);
multiswarm-style worktree orchestrator; ECC multi-agent/commands (prior-intake URL);
Claude Code subagent patterns; Codex skill agent-launching; existing N+6.22A coordinators.
Most are `source_needed: true` with a null URL (no fabrication). Swarms are the
launch/coordinate target, not just Agent Arena visualization, and stay gated behind the
controlled-launcher stage.

## New backlog items (12)

Sentry Search (not priority), Panopticore, cobalt.tools (gated), Claude Mem (1.5),
AIEngineer Coach, Quant Mind (finance-gated), Pake (`tw93/Pake`), ChatGPT memory/dreaming
research, Zero by Vercel (2), LLM RAG AI Agents, Ideogram, and Memory Palace / PAO
(tier-1-last). All in `swarm_launcher_repo_intake_n6_24a.json`.

## Memory palace lane summary

A PAO (Person-Action-Object) memory-palace learning app over real or generated 3D
environments (text / camera / LiDAR / movie / generated), with object placement, infinite
palace expansion, and a study/revise/learn loop. **Tier-1-last** (build last): highest
capability surface, so camera/LiDAR/device capture is **gated and NOT enabled**. Smallest
safe first step is a local, text-only PAO prototype.

## Validation

- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_24a_*.py" -v`
  - all tests pass.
- `python 03_scripts/public_repo_security_audit.py --run --json` -> `failed_checks: 0`,
  `safe_to_make_public: true`, 0 blockers.
- `python 03_scripts/ghoti_product_launcher.py --status --json` -> ok; `--context-pack`
  and `--repo-map` run clean (residue restored).
- `git diff --check` / `git show --check` clean.
- Swarm JSON: 7 candidates + 12 backlog items, all required fields, `source_url` null
  whenever `source_needed` true.

## Safety summary

- Static inspection and planning only. No installs, no clones, no external repo execution.
- No MCP, no browser/computer-use, no account login, no live agent launching, no
  auto-submit, no Docker.
- No secrets/tokens/cookies/auth files; no real local paths/usernames/private images
  (placeholders only).
- No `03_scripts/agent_arena` or `14_context/agent_arena` file edited (N+6.23B not merged).
- No fabricated URLs; unverified sources are `source_needed: true` with a null URL.

## Final verdict

IMPLEMENTED_AND_PUSHED
