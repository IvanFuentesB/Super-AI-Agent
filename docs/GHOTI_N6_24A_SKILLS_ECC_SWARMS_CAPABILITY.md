# Ghoti N+6.24A - Skills / ECC / Swarms Capability Upgrade + Swarm Repo Intake

## Summary

N+6.24A is a **static intake and planning only** milestone. It builds a clear capability
map of Claude, Codex, and Hermes skills/agents/commands/hooks, explains **ECC = Everything
Claude Code** (not elliptic curve cryptography) and why Ghoti adapts it instead of
installing it, and intakes real **swarm-launcher** repo candidates plus new backlog items.
It prepares the path to actual agent launching later, but it **launches nothing, installs
nothing, clones nothing, and executes nothing** today.

It may run in parallel with Codex N+6.23B because it does **not** edit any
`03_scripts/agent_arena` or `14_context/agent_arena` file.

## What was produced

| Area | File |
|------|------|
| Capability map (index) | `14_context/skills/SKILLS_CAPABILITY_MAP_N6_24A.md` |
| Claude skills/agents/commands/hooks | `14_context/skills/CLAUDE_SKILLS_AND_AGENTS_N6_24A.md` |
| Codex AGENTS.md vs skills | `14_context/skills/CODEX_AGENTS_AND_SKILLS_N6_24A.md` |
| Hermes skills/memory/tooling | `14_context/skills/HERMES_SKILLS_AND_MEMORY_N6_24A.md` |
| ECC = Everything Claude Code | `14_context/skills/ECC_EVERYTHING_CLAUDE_CODE_N6_24A.md` |
| Swarm repo intake (md + json) | `14_context/tool_intake/swarm_launcher_repo_intake_n6_24a.{md,json}` |
| Memory Palace / PAO product lane | `14_context/tool_intake/memory_palace_pao_app_lane_n6_24a.md` |
| Handoff | `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_SKILLS_SWARMS_TASK.md` |
| Test | `01_projects/runtime_mvp/tests/test_n6_24a_skills_ecc_swarms_capability.py` |

## Skills, agents, commands, hooks (the four building blocks)

- **Skill** - instructions/knowledge the model loads; changes *how* an agent works, not
  what it is allowed to do.
- **Agent (subagent)** - a separate worker with its own context that takes a task and
  returns a result; the swarm mechanism.
- **Command** - a named prompt a person triggers.
- **Hook** - event-triggered automation that can run code; the highest-risk block.

Ghoti adopts all four as **guidance/manual** first; runtime wiring requires a separate,
audited, human-approved milestone. Hooks stay **NOT enabled as executable**. Details per
agent are in the skills files above.

## Codex AGENTS.md vs Codex skills

`AGENTS.md` is repo-level rules Codex reads (the Codex-facing `CLAUDE.md`); a Codex skill
is a reusable recipe/prompt. Neither executes code. Codex stays audit-only and manual; the
"Codex skill agent-launching" (conductor) pattern is planned and gated.

## ECC status (Everything Claude Code)

- ECC is **Everything Claude Code**: a curated bundle of Claude Code commands, agents,
  skills, hooks, and security-scanner patterns. **It is not elliptic curve cryptography.**
- Recorded source (re-verify): prior intake records `https://github.com/affaan-m/ecc`
  (medium confidence). No new URL is fabricated.
- **Ghoti adapts, does not install:** ECC hooks execute code and could take live actions
  in the operator's real profile; Ghoti re-expresses the *ideas* as guidance and builds
  its own audited equivalents.
- **Full ECC can be tested in a separate, throwaway Claude profile** (or VM) against a
  scratch repo, with no Ghoti repo access, no secrets, and no live accounts - then only
  the notes come back. See `ECC_EVERYTHING_CLAUDE_CODE_N6_24A.md`.

## Swarm repo candidates

Swarms are meant to **launch and coordinate** other agents later, not only visualize them
in the Agent Arena. Candidates (all study-only, most `source_needed` with null URL):
ClawTeam; `swarms` (operator handle `am-will/swarms`); multiswarm-style worktree
orchestrator; ECC multi-agent/commands references; Claude Code subagent patterns; Codex
skill agent-launching; and existing N+6.22A coordinators (`kimi_claude_swarms`,
`awesome-llm-apps`). Full fields in `swarm_launcher_repo_intake_n6_24a.json`.

### New backlog items

Sentry Search (not priority), Panopticore, cobalt.tools (gated), Claude Mem (tier 1.5),
AIEngineer Coach, Quant Mind (finance-gated), Pake (`tw93/Pake`), ChatGPT memory/dreaming
research, Zero by Vercel (tier 2), LLM RAG AI Agents, Ideogram, and the Memory Palace /
PAO app (tier-1-last product lane).

## Memory Palace / PAO lane (future, tier-1-last)

A learning app on the **PAO (Person-Action-Object)** mnemonic over real or generated 3D
environments (text-described, camera/LiDAR-captured, movie-derived, or generated), with
object placement, infinite palace expansion, and a study/revise/learn loop. It is **build
last**: highest capability surface (3D capture, sensors), so camera/LiDAR/device capture is
**gated and NOT enabled**. Smallest safe first step is a local, text-only PAO prototype.
See `memory_palace_pao_app_lane_n6_24a.md`.

## The safe progression

`simulation -> trace ingestion -> static repo intake -> controlled launcher -> approved-window bridge -> supervised overnight loop`

This milestone is the **static repo intake** step. The **controlled launcher** (real
swarm launching) is the next big, gated step: human-approved, dry-run-first, worktree-per-
agent, under the existing approval gates.

## Safety posture

Static inspection and planning only. No installs, no clones, no external repo execution,
no MCP setup, no browser/computer-use, no account login, no live agent launching, no
auto-submit, no Docker, no secrets/tokens/cookies/auth files, no real local
paths/usernames/private images. Unverified sources are `source_needed: true` with a null
URL; no URL is fabricated. No `03_scripts/agent_arena` or `14_context/agent_arena` file is
edited.
