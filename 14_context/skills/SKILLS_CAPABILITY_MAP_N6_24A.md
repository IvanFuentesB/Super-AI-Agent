# Ghoti Skills & Swarm Capability Map (N+6.24A)

Milestone: N+6.24A
Date: 2026-06-06
Status: static intake and planning only. Nothing here is installed, wired, or
enabled. This map prepares the path to real agent launching in a later, human-approved
milestone; it launches nothing today.

This is the index. The detail lives in sibling files:

- `CLAUDE_SKILLS_AND_AGENTS_N6_24A.md` - Claude Code skills vs agents vs commands vs hooks.
- `CODEX_AGENTS_AND_SKILLS_N6_24A.md` - Codex `AGENTS.md` vs Codex skills.
- `HERMES_SKILLS_AND_MEMORY_N6_24A.md` - Hermes skills, session memory, tooling.
- `ECC_EVERYTHING_CLAUDE_CODE_N6_24A.md` - ECC = Everything Claude Code (not elliptic curve).
- `../tool_intake/swarm_launcher_repo_intake_n6_24a.md` (+ `.json`) - swarm-launcher repo candidates.
- `../tool_intake/memory_palace_pao_app_lane_n6_24a.md` - future tier-1-last product lane.

It also builds on the existing skills records (do not duplicate them):
`ghoti_skill_registry.md`, `claude_code_skill_install_log.md`, `codex_working_rules.md`,
`hermes_router_wrapper_policy.md`, `ecc_inspired_agent_setup_n6_19a.md`,
`karpathy_guidelines_intake.md`.

## Status legend (consistent across the repo)

- **guidance-only** - a playbook/checklist that shapes how work is done; no runtime
  execution, no live actions.
- **manual** - a documented recipe a human or coordinator runs by hand.
- **planned** - specified, not built.
- **NOT enabled** - visible/named somewhere but not approved or turned on for Ghoti.
- **runtime-wired** - would mean automatic execution. **None today.**

## One-paragraph mental model

A **skill** changes *how* an agent works (instructions/knowledge it loads); it does not
grant new permissions. An **agent/subagent** is a *separate worker* with its own context
that takes a task and returns a result. A **command** is a *named prompt* a person
triggers. A **hook** is *event-triggered automation* that can run code. Across Claude,
Codex, and Hermes the names differ but the four ideas recur. Ghoti adopts all four as
**guidance/manual** first and only wires any of them to runtime behind a separate,
audited, human-approved milestone.

## Capability matrix (today's honest status)

| Agent | Skills | Agents/subagents | Commands | Hooks | Memory |
|-------|--------|------------------|----------|-------|--------|
| Claude Code | guidance playbooks (goal, ultraplan, ghoti-status, prompt-bus, karpathy-guidelines) | role concept ("Claude builder"); manual, not auto-spawned by Ghoti | repo slash playbooks (manual) | hook-as-validator **idea only**; NOT enabled as executable | vault notes + compact memory (manual) |
| Codex | audit rule sheet (`codex_working_rules.md`) | role concept ("Codex auditor"); manual | `AGENTS.md` repo rules (guidance) | none enabled | `14_context/codex_*` reports + vault (manual) |
| Hermes | approved wrappers (read-only phase 1, dry-run phase 2) - **planned** | local coordinator (llama-class); reads handoffs, status-only | named wrappers only; never arbitrary commands | none enabled | Obsidian vault + status brain (manual) |

## The safe progression (the spine of this milestone)

Ghoti moves one audited step at a time:

`simulation -> trace ingestion -> static repo intake -> controlled launcher -> approved-window bridge -> supervised overnight loop`

| Stage | Where it is today | Milestone |
|-------|-------------------|-----------|
| simulation | done | N+6.21A Agent Arena (simulation-only) |
| trace ingestion | done | N+6.23A Agent Arena real local trace (read-only) |
| static repo intake | **this milestone** | N+6.24A skills/ECC/swarm intake (planning only) |
| controlled launcher | planned, not built | future, human-approved; dry-run first |
| approved-window bridge | partial (paste, no auto-submit) | N+6.20A approved-window paste harness |
| supervised overnight loop | planned, not built | future, human-approved, gated |

Swarms are the reason this spine exists: the end goal is a launcher that **coordinates
and launches** Claude/Codex/local-worker agents on real tasks (worktree-per-agent, under
approval gates) - not only the Agent Arena visualization. That launcher is **planned and
gated**; this milestone only maps the capability and intakes candidate repos.

## Dependency note

- N+6.22B (Tool Backlog Intake v2 + Repo Memory Vault v1) is on `main`; this milestone
  builds on its `14_context/tool_intake/` and `14_context/memory_vault/` areas (it adds
  new files there; it does not edit the existing ones).
- N+6.23B (Codex audit of N+6.23A Agent Arena trace ingestion) is **not merged yet**.
  Per the N+6.24A rule this lane does **not** edit any `03_scripts/agent_arena` or
  `14_context/agent_arena` file. It only references them as the simulation/trace stages.

## Hard safety posture for this milestone

Static inspection and planning only: no installs, no clones, no external repo execution,
no MCP setup, no browser/computer-use, no account login, no live agent launching, no
auto-submit, no Docker, no secrets, no real local paths/usernames. Unverified sources are
recorded as `source_needed: true` with a null URL; no URL is fabricated.
