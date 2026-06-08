# Context Snapshot — N+6.30A Plug-and-Play Swarm & Memory Intake

**Milestone:** N+6.30A
**Date:** 2026-06-07
**Branch:** `feat/ghoti-agent-claude-n6-30a-plug-and-play-swarm-memory-intake`
**Base:** `ca90fbd` (N+6.28B Rust policy checker merged)
**Status:** IMPLEMENTED_AND_PUSHED — N+6.30A patch applied (Dreams / memory consolidation lane)

---

## What This Milestone Does

N+6.30A is a pure inspection and planning milestone. No code is installed, no agents are
launched, no tools are enabled. It synthesizes prior tool intake work (N+6.12A through
N+6.28B) into a ranked playbook for plug-and-play swarm and memory tools.

---

## Dependency State

| Branch | Status |
|--------|--------|
| N+6.27B swarm_launcher | merged |
| N+6.28B Rust policy checker | merged |
| N+6.29B computer_use_adapter | not merged — computer_use_adapter files untouched |

---

## Files Added

| File | Purpose |
|------|---------|
| `docs/GHOTI_N6_30A_PLUG_AND_PLAY_SWARM_MEMORY_INTAKE.md` | Main milestone doc |
| `14_context/tool_intake/plug_and_play_swarm_tools_n6_30a.md` | Tool ranking table |
| `14_context/tool_intake/plug_and_play_swarm_tools_n6_30a.json` | Structured tool registry (14 tools) |
| `14_context/tool_intake/ecc_ruflo_swarm_trial_plan_n6_30a.md` | Trial plan for ECC / swarms / ClawTeam |
| `14_context/tool_intake/cua_ui_tars_computer_use_trial_plan_n6_30a.md` | CUA / UI-TARS computer-use plan |
| `14_context/tool_intake/claude_mem_obsidian_mempalace_intake_n6_30a.md` | Memory stack intake |
| `14_context/tool_intake/tier_one_priority_status_n6_30a.md` | Tier-1 status dashboard |
| `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_PLUG_AND_PLAY_TOOLS_TASK.md` | Handoff doc |
| `01_projects/runtime_mvp/tests/test_n6_30a_plug_and_play_swarm_memory_intake.py` | Structural tests |
| `14_context/claude_n6_30a_plug_and_play_swarm_memory_intake.md` | This file |

---

## Tool Ranking Summary

### Tier A — Use Now in Main Claude Profile
- **Subagents (built-in)** — already in use; Explore type for read-only tasks
- **Skills (built-in)** — model-invoked, lowest blast radius

### Tier B — Use Soon (Isolated Profile Trial First)
- **am-will/swarms** — skills-based, no server; wave+pool maps to Ghoti gates; trial plan ready
- **ECC (affaan-m/ecc)** — governance/skill patterns; MIT license verified; trial plan ready
- **affaan-m/claude-swarm** — dependency-graph patterns adopted in N+6.27A; trial plan ready

### Tier C — Inspect More / Source Needed
- **ClawTeam** — MIT license; needs full sandbox trial; "full automation" goal needs careful gate
- **Claude Mem** — source_needed; no URL guessed; await operator confirmation
- **Obsidian-skills** — source_needed; no URL guessed; await operator confirmation
- **MemPalace (agent)** — source_needed; distinct from PAO app (N+6.24A)
- **UI-TARS** — source_needed; ambiguous upstream; await operator confirmation
- **Paperclip / Understand-Anything / CodeGraph / Stop skill** — Tier-1 source_needed items

### Tier D — Defer
- **Dynamic Workflows** — executes generated JS; very high token cost; defer
- **Agent Teams** — experimental; 2-16 live agents; highest blast radius; defer
- **Background Agents** — off until kill-switch milestone
- **TryCUA real use** — patterns only until Docker sandbox milestone

### Tier E — Avoid
- **Ruflo / Claude Flow** — supply-chain incidents: malicious npm pre-install, MCP prompt
  injection (#1375), SQL injection; never install

---

## Key Safety Invariants (unchanged from prior milestones)

- No live agent launching in any form
- No Ruflo installation ever
- No Agent Teams until dedicated worktree-isolation milestone
- No Dynamic Workflows until dedicated milestone with JS-read gate
- No Background Agents until kill-switch milestone
- No real OS click/type until Docker sandbox milestone
- No MCP setup until dedicated MCP milestone
- No auto-submit, no auto-post, no auto-paste, ever
- No secrets in plans, ever
- No external website navigation, ever
- No account login, ever
- PAO app (N+6.24A) is a separate product lane; not conflated with agent memory

---

## What Changed vs Prior Milestones

- N+6.28B (Rust policy checker) is now merged and active — bridge wiring to
  `ghoti_computer_use_adapter.py` is the next concrete step post N+6.29B merge.
- N+6.27B (swarm_launcher) is merged — dry-run only; live launch remains off.
- N+6.29B (computer_use_adapter) is NOT merged; those files are untouched here.
- Tool intake now covers 14 tools with structured JSON registry.
- Memory stack plan documented; no new memory tools installed; all source_needed items
  await operator URL confirmation before any action.

---

## Immediate Next Steps

1. **Codex:** audit N+6.29B (`audit/ghoti-agent-codex-n6-29a-computer-use-repo-backed-adapter`)
2. **Post N+6.29B merge:** wire Rust policy bridge in `ghoti_computer_use_adapter.py`
3. **Operator:** confirm exact repo/tool URLs for source_needed items
   (Claude Mem, Obsidian-skills, MemPalace agent, UI-TARS, Paperclip, Understand-Anything,
   CodeGraph, Stop skill)
4. **Isolated profile trials:** follow `ecc_ruflo_swarm_trial_plan_n6_30a.md`
   (bring back notes only — never trial in Ghoti profile)
5. **Codex audit target:** `audit/ghoti-agent-codex-n6-30a-plug-and-play-swarm-memory-intake`

---

## N+6.30A Patch — Dreams / Memory Consolidation Lane

Added via patch commit on the same branch. Four source_needed candidates:

| Candidate | ID in registry | Purpose |
|-----------|---------------|---------|
| OpenDream / opendreams | `open_dream` | Session consolidation; structured memory summary |
| dream-skill | `dream_skill` | SKILL.md-style consolidation; Ghoti-native fallback |
| dream-memory | `dream_memory` | Persistent reflective memory layer |
| memory-lancedb-dreaming | `memory_lancedb_dreaming` | Vector memory with dream phases |

All four: source_needed=true, source=null, can_launch_real_agents=false.
No URL guessed for any. Operator must confirm exact repos before any intake.

Key invariants: memory consolidation only; read-only first; no auto-write of AGENTS.md
or CLAUDE.md; no sensitive data stored; PAO app (N+6.24A) is a separate product lane.
