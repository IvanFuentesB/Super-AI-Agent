# NEXT PLUG-AND-PLAY TOOLS TASK

## Current state (as of N+6.30A)

**Branch:** `feat/ghoti-agent-claude-n6-30a-plug-and-play-swarm-memory-intake`
**Status:** IMPLEMENTED_AND_PUSHED — awaiting Codex audit

N+6.30A is a pure inspection and planning milestone. It synthesizes all prior tool intake
work (N+6.12A through N+6.28B) into a ranked playbook for plug-and-play swarm and memory
tools. No code installed, no agents launched, no tools enabled.

---

## Immediate next steps (in order)

### 1. Codex: audit N+6.29B (computer_use_adapter)
- Branch: `feat/ghoti-agent-claude-n6-29a-computer-use-repo-backed-adapter`
- Audit target: `audit/ghoti-agent-codex-n6-29a-computer-use-repo-backed-adapter`
- Once merged: `computer_use_adapter` files unlock for next milestone

### 2. Wire Rust policy bridge (post N+6.29B merge)
- Extend `03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py`
- Pipe validated plans to `cargo run --manifest-path rust/ghoti_policy_checker/Cargo.toml`
- Update `rust_policy_bridge_ready: true`
- Add regression test for bridge handshake

### 3. Operator: confirm source_needed tools
The following tools are blocked from further intake until the operator supplies the exact repo URL:

| Tool | What to confirm |
|------|-----------------|
| Claude Mem | Exact repo/tool for session-memory continuity |
| Obsidian-skills | Exact source for Claude Code ↔ Obsidian bridge |
| MemPalace (agent) | Whether an agent memory palace repo exists distinct from the PAO app |
| UI-TARS | Exact upstream (bytedance/UI-TARS? another fork?) |
| Paperclip | Exact project (several unrelated projects use the name) |
| Understand-Anything | Exact repo |
| CodeGraph / Git Nexus | Exact project |
| Stop / Stop skill | Exact tool / skill |

### 4. Isolated profile trials (operator-run, bring back notes only)
Follow `14_context/tool_intake/ecc_ruflo_swarm_trial_plan_n6_30a.md`:
1. am-will/swarms (swarm-planner in Plan Mode → parallel-task max 3 agents)
2. ECC (governance skill only; inspect all hooks before accepting)
3. affaan-m/claude-swarm (2-agent; check auto-commit)
4. ClawTeam (simplest goal; inspect P2P network + state)

Never trial in Ghoti profile. Bring back notes → add to `14_context/tool_intake/`.

### 5. Claude main profile swarm trial (after isolated profile notes)
- Subagents with read-only Explore type (already working)
- Skills: add one SKILL.md from ECC patterns
- Record: automatic vs manual, token cost, auto-commit behavior

---

## Files to review for context

| File | Purpose |
|------|---------|
| `14_context/tool_intake/plug_and_play_swarm_tools_n6_30a.json` | Structured tool registry with ranking |
| `14_context/tool_intake/ecc_ruflo_swarm_trial_plan_n6_30a.md` | Trial plan for ECC / swarms / ClawTeam |
| `14_context/tool_intake/cua_ui_tars_computer_use_trial_plan_n6_30a.md` | CUA / UI-TARS next steps |
| `14_context/tool_intake/claude_mem_obsidian_mempalace_intake_n6_30a.md` | Memory stack plan |
| `14_context/tool_intake/tier_one_priority_status_n6_30a.md` | Tier-1 dashboard |
| `docs/GHOTI_N6_30A_PLUG_AND_PLAY_SWARM_MEMORY_INTAKE.md` | Full milestone doc |

---

## What must stay disabled until explicit milestone

- Live agent launching (all forms)
- Ruflo / Claude Flow (any version; supply-chain incidents)
- Agent Teams (experimental; off until dedicated milestone)
- Dynamic Workflows (executes generated JS; off until dedicated milestone)
- Background Agents (off until kill-switch milestone)
- Real OS click/type (off until Docker sandbox milestone)
- MCP setup (off until dedicated MCP milestone)
- Auto-submit (never)
- Docker (off until approved image digest milestone)
- External website navigation (never in computer-use plans)
- Account login (never)
