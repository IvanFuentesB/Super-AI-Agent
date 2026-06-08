# GHOTI N+6.30A — Plug-and-Play Swarm & Memory Tool Intake

## Overview

N+6.30A is an inspection and planning milestone. It surveys the best plug-and-play swarm,
memory, and computer-use tools available, builds a concrete use/install/adapt ranking,
and creates Ghoti-native playbooks. Nothing is installed, run, or enabled.

**Base main:** `ca90fbd` (N+6.28B Rust policy checker merged)
**Branch:** `feat/ghoti-agent-claude-n6-30a-plug-and-play-swarm-memory-intake`

## Dependency State

| Branch | Status |
|--------|--------|
| N+6.27B swarm_launcher | merged |
| N+6.28B Rust policy checker | merged |
| N+6.29B computer_use_adapter | merged — computer_use_adapter files untouched by N+6.30A |

---

## 1. Inspected Tools Summary

| Tool | Source | License | Inspected | Status |
|------|--------|---------|-----------|--------|
| Subagents (built-in) | Official | Anthropic TOS | N+6.26A | active, in use |
| am-will/swarms | github.com/am-will/swarms | unverified | N+6.26A, N+6.27A | trial plan ready |
| ECC (affaan-m/ecc) | github.com/affaan-m/ecc | MIT ✓ | N+6.26A, N+6.27A | trial plan ready |
| affaan-m/claude-swarm | github.com/affaan-m/claude-swarm | MIT ✓ | N+6.26A, N+6.27A | trial plan ready |
| ClawTeam (HKUDS/ClawTeam) | github.com/HKUDS/ClawTeam | MIT ✓ | N+6.26A | sandbox trial needed |
| Ruflo / Claude Flow | github.com/ruvnet/ruflo | MIT (supply-chain risk) | N+6.12A | defer indefinitely |
| TryCUA / CUA | github.com/trycua/cua | MIT ✓ | N+6.12A | patterns in N+6.29A |
| UI-TARS | unknown (ambiguous) | Apache-2.0 (reported) | N+6.12A (source_needed) | source_needed |
| Claude Mem | unknown | unknown | none | source_needed |
| Obsidian-skills | unknown | unknown | none | source_needed |
| MemPalace (agent) | unknown (warn: impostor sites exist) | unknown | N+6.24A (PAO only) | source_needed |
| Dynamic Workflows | Official | Anthropic TOS | N+6.26A | defer |
| Agent Teams | Official | Anthropic TOS | N+6.26A | defer |
| OpenDream / opendreams | unknown (source_needed) | unknown | none | source_needed (dream lane) |
| dream-skill | unknown (source_needed) | unknown | none | source_needed (dream lane) |
| dream-memory | unknown (source_needed) | unknown | none | source_needed (dream lane) |
| memory-lancedb-dreaming | unknown (source_needed) | unknown | none | source_needed (dream lane) |

No third-party code committed. No repos cloned in N+6.30A (prior inspection records used).
Dream/memory-consolidation candidates added via N+6.30A patch; all are source_needed.

---

## 2. Plug-and-Play Ranking

### Use Now in Main Claude Profile
- **Subagents (built-in)** — already verified; continue using
- **Skills (built-in)** — model-invoked, lowest blast radius

### Use Soon (Separate Throwaway Profile → Ghoti Adapt)
- **am-will/swarms** — skills-based; no server; wave+pool model maps onto Ghoti gates
- **ECC (affaan-m/ecc)** — governance/skill patterns; install only in isolated profile
- **affaan-m/claude-swarm** — dependency-graph patterns already adopted in N+6.27A

### Inspect More / Source Needed
- **Claude Mem** · **Obsidian-skills** · **MemPalace (agent)** · **UI-TARS** — all await operator URL confirmation
- **ClawTeam** — needs full sandbox trial; "full automation" goal requires careful gate
- **Paperclip** · **Understand-Anything** · **CodeGraph** · **Stop skill** — Tier-1 source_needed items

### Defer
- **Dynamic Workflows** — executes generated JS; very high token cost; research preview
- **Agent Teams** — experimental; 2-16 live agents; highest blast radius
- **Background Agents** — off until kill-switch milestone
- **TryCUA real use** — patterns only until Docker sandbox milestone

### Avoid
- **Ruflo / Claude Flow** — supply-chain incidents (malicious pre-install, MCP injection, SQL injection); never install

---

## 3. Claude Main Profile Swarm Playbook

### Safe Order (least risky → most risky)

1. **Subagents** — already in use; continue with explicit read-only instructions
2. **Skills** — add one SKILL.md (ECC governance pattern); confirm load only
3. **am-will/swarms swarm-planner** — Plan Mode; junk repo; record plan format
4. **am-will/swarms parallel-task** — max 3 agents; junk repo; record token cost
5. **affaan-m/claude-swarm** — 2 agents; junk repo; check auto-commit behavior
6. **ClawTeam** — simplest goal; junk repo; inspect P2P network + state
7. **ECC full install** — isolated profile; inspect every hook before accepting
8. **Agent Teams** — isolated profile; 2-agent team; scratch repo; record cost
9. **Dynamic Workflows** — isolated profile; read generated JS before executing

### What to Record Per Tool
- Automatic vs manual (does it require human approval at each step?)
- Token cost (rough; full run vs dry-run)
- Whether it auto-commits or auto-pushes
- Whether it makes outbound network calls without approval
- Anything that surprised you

### What Stays Disabled in Ghoti (regardless of trial results)
- Live agent launching, agent teams, dynamic workflows
- Executable hooks in Ghoti profile
- Ruflo (any version)
- Background agents
- MCP setup
- Browser / computer-use (until Docker milestone)
- Auto-submit, auto-post, auto-paste

---

## 4. Ghoti Integration Plan

### Already Active (no new work needed)
- Dry-run swarm launcher (N+6.27B) — wave + role + overlap detection
- Rust policy checker (N+6.28B) — default-deny JSON policy validator
- Computer-use adapter contract (N+6.29A pending) — URL guard + dry-run payload

### Next Integration Steps (in order)

**Step 1 — Wire Rust bridge** (future audited runtime lane)
- Extend `ghoti_computer_use_adapter.py` to pipe validated plans to Rust checker.
- Update `rust_policy_bridge_ready: true` once wired and tested.

**Step 2 — Add am-will/swarms wave pattern to swarm launcher** (post trial)
- Extend `ghoti_swarm_launcher.py` with wave-based execution plan.
- Each wave = one human approval gate.
- `max_parallel` bounds the agent pool.

**Step 3 — Feed Agent Arena from adapter + launcher** (post both above)
- Launcher emits `arena_status` blocks.
- Adapter emits `arena_status` blocks.
- Agent Arena (`21_agents/`) visualizes both.

**Step 4 — Hermes grounding** (ongoing)
- Hermes status packet (N+6.25B) feeds Hermes on every turn.
- Never let Hermes run without a current status packet.
- Extend status packet with swarm_launcher and adapter state.

**Step 5 — Controlled live launch** (future, audited milestone)
- Kill switch + approval token required.
- Worktree-per-agent isolation.
- One agent pair (Claude builder + Codex auditor) on trivial task.
- Codex merge gate required.

### Codex Merge Gate (always required before main)
Every Claude feature branch → Codex audit branch → Codex merge → main.
No Claude branch merges directly to main.

---

## 5. Memory Stack Plan

### Current (no change needed)
- **Memory Vault** (`14_context/00_main_memory/`) — canonical, committed
- **Compact memory** (`14_context/compact_memory/`) — LLM-ready context packs
- **Hermes status packet** — grounds Hermes in current mission state
- **Context pack builder** — generates compact_memory/ from vault
- **Repo knowledge map** — generates task bundles from repo structure

### Conditional Additions (pending source confirmation)
- **Claude Mem** — if file-based/local: Ghoti-native adapter wrapping existing vault
- **Obsidian bridge** — read-only path first; write path gated to dedicated folder
- **MemPalace (agent)** — if file-based: structured index over 14_context/ (warn: impostor sites exist; confirm official repo)

### Dreams / Memory Consolidation Lane (N+6.30A patch)
All four candidates are source_needed. Shared invariants:
- **OpenDream / opendreams** — session consolidation; confirm repo; read-only first
- **dream-skill** — SKILL.md-style consolidation; Ghoti-native fallback available
- **dream-memory** — persistent reflective memory layer; local/file-based only
- **memory-lancedb-dreaming** — vector memory with dream phases; confirm local LanceDB mode

None of these auto-write `AGENTS.md` or `CLAUDE.md`. All writes require human preview and
approval. No sensitive data, secrets, private paths, health details, or account data stored.
These are memory consolidation tools — not live agent launchers.

### Hard Rules (all layers)
- Local and file-based until secret-management milestone
- No cloud service, no API key in any memory layer
- Memory Vault is source of truth; nothing overwrites it without approval gate
- PAO app (N+6.24A) is a separate product lane (future user-facing product); Tier-1-last
- Dream/consolidation tools are distinct from the PAO app

---

## 6. Tier-1 Priorities Summary

| Item | Status | Action |
|------|--------|--------|
| Paperclip | source_needed | Operator confirms URL |
| Understand-Anything | source_needed | Operator confirms URL |
| CodeGraph / Git Nexus | source_needed | Operator confirms URL |
| Stop / Stop skill | source_needed | Operator confirms URL |
| DeepSeek routing | research_only | No key yet; plan in model_provider_lane_n6_22a.md |
| Rust runtime | **active (N+6.28B)** | Bridge wiring next |
| am-will/swarms | trial plan ready | Isolated profile trial |
| ECC | trial plan ready | Isolated profile trial |
| Ghoti swarm launcher | **merged (N+6.27B)** | Extend with wave pattern post-trial |
| Computer-use adapter | **merged (N+6.29B)** | Keep dry-run; wire Rust bridge only in an audited lane |
| Claude Mem | source_needed | Operator confirms tool |
| Obsidian-skills | source_needed | Operator confirms source |
| MemPalace (agent) | source_needed | Operator confirms repo (warn: impostor sites) |
| OpenDream / opendreams | source_needed (dream lane) | Operator confirms exact repo |
| dream-skill | source_needed (dream lane) | Operator confirms; Ghoti-native fallback available |
| dream-memory | source_needed (dream lane) | Operator confirms; local/file-based |
| memory-lancedb-dreaming | source_needed (dream lane) | Operator confirms; evaluate local LanceDB |

---

## 7. What Remains Disabled

| Surface | Gate Required |
|---------|-------------|
| Live agent launching | Kill-switch + approval token + worktree-per-agent milestone |
| Agent Teams | Dedicated milestone with worktree isolation |
| Dynamic Workflows | Read generated JS gate; dedicated milestone |
| Background Agents | Kill-switch milestone |
| Ruflo / Claude Flow | Never (supply-chain incidents) |
| Browser / computer-use | Separate audited sandbox milestone |
| Real OS click/type | Docker sandbox milestone |
| MCP setup | Dedicated MCP milestone |
| Auto-submit | Never |
| Docker | Dedicated Docker milestone with approved image digest |
| External website navigation | Never |
| Account login | Never |
| Secrets in plans | Never |

---

## Files Added

| File | Purpose |
|------|---------|
| `docs/GHOTI_N6_30A_PLUG_AND_PLAY_SWARM_MEMORY_INTAKE.md` | This document |
| `14_context/tool_intake/plug_and_play_swarm_tools_n6_30a.md` | Tool ranking + attribution table |
| `14_context/tool_intake/plug_and_play_swarm_tools_n6_30a.json` | Structured tool registry |
| `14_context/tool_intake/ecc_ruflo_swarm_trial_plan_n6_30a.md` | ECC / Ruflo / swarms / ClawTeam trial plan |
| `14_context/tool_intake/cua_ui_tars_computer_use_trial_plan_n6_30a.md` | CUA / UI-TARS computer-use plan |
| `14_context/tool_intake/claude_mem_obsidian_mempalace_intake_n6_30a.md` | Memory stack intake |
| `14_context/tool_intake/tier_one_priority_status_n6_30a.md` | Tier-1 status dashboard |
| `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_PLUG_AND_PLAY_TOOLS_TASK.md` | Handoff |
| `01_projects/runtime_mvp/tests/test_n6_30a_plug_and_play_swarm_memory_intake.py` | Tests |
| `14_context/claude_n6_30a_plug_and_play_swarm_memory_intake.md` | Context snapshot |

## Codex Audit Target

`audit/ghoti-agent-codex-n6-30a-plug-and-play-swarm-memory-intake`
