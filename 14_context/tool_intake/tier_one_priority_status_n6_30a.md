# Tier-1 Priority Status (N+6.30A)

**Milestone:** N+6.30A
**Date:** 2026-06-07
**Updates from:** N+6.22A tool priority map, N+6.24A, N+6.26A, N+6.28B

This file records the current status of every Tier-1 priority item.
Nothing here is installed, cloned, or run.

---

## Swarm / Agent Orchestration

| Item | Prior status | N+6.30A status | Next action |
|------|-------------|---------------|-------------|
| Subagents (built-in) | guidance_only | **active, in use** | Continue; use Explore agent type for read-only work |
| am-will/swarms | study_then_guidance | plan ready | Trial in isolated profile per `ecc_ruflo_swarm_trial_plan_n6_30a.md` §3 |
| ECC (affaan-m/ecc) | adapt_guidance_only | plan ready | Trial in isolated profile per §1 |
| affaan-m/claude-swarm | should_stay_disabled | plan ready | Trial in isolated profile per §4 |
| ClawTeam | should_stay_disabled | plan ready | Full sandbox trial per §5 |
| Ruflo / Claude Flow | should_stay_disabled | **DEFER indefinitely** | Supply-chain incidents; patterns only; never install |
| Dynamic Workflows | should_stay_disabled | **DEFER** | Research preview; executes JS; high cost |
| Agent Teams | should_stay_disabled | **DEFER** | Experimental; 2-16 live agents; high blast radius |
| Background Agents | should_stay_disabled | **DEFER** | Off until kill-switch milestone |
| Ghoti swarm launcher | N+6.27A branch | **merged (N+6.27B)** | Dry-run only; live launch pending future milestone |

---

## Computer-Use

| Item | Prior status | N+6.30A status | Next action |
|------|-------------|---------------|-------------|
| TryCUA / CUA patterns | inspected N+6.12A | patterns in N+6.29A | N+6.29B merge → Rust bridge wiring |
| UI-TARS patterns | source_needed | **source_needed** | Operator confirms exact upstream |
| N+6.29A adapter | branch pushed | **not merged (N+6.29B pending)** | Codex audit → merge |
| Rust policy bridge | N+6.28B merged | bridge not wired yet | Wire post N+6.29B merge |
| Docker / real OS | blocked | **blocked** | Docker milestone required |

---

## Memory Stack

| Item | Prior status | N+6.30A status | Next action |
|------|-------------|---------------|-------------|
| Memory Vault (14_context/00_main_memory/) | active | **active** | No change needed |
| Compact memory | active | **active** | No change needed |
| Hermes status packet | merged N+6.25B | **active** | Hermes grounded; no change |
| Agent handoff vault | active | **active** | No change needed |
| Claude Mem | source_needed | **source_needed** | Operator confirms exact tool |
| Obsidian-skills | source_needed | **source_needed** | Operator confirms exact source |
| MemPalace (agent memory) | source_needed | **source_needed** | Operator confirms; distinct from PAO app |
| PAO app (N+6.24A) | planning | **Tier-1-last** | Build after core agent stack proven |

---

## Paperclip (Tier-1 flagship)

- **Status:** source_needed — unchanged from N+6.22A.
- **Action:** operator confirms the exact project/repo URL.
- **Gate:** `tier1_static_inspect` → license/README → install script check → trial plan.
- The name "Paperclip" is used by several unrelated projects; no URL is guessed.

---

## Understand-Anything (Tier-1)

- **Status:** source_needed — unchanged from N+6.22A.
- **Action:** operator confirms the exact repo.
- Likely a document/media understanding tool. Once confirmed: static inspect for
  install hooks, network requirements, and license.

---

## CodeGraph / Git Nexus (Tier-1)

- **Status:** source_needed — unchanged from N+6.22A.
- **Action:** operator confirms the exact project (several unrelated projects use "CodeGraph").
- **Value:** a local, offline queryable graph of the repo (nodes = files/milestones/tests;
  edges = imports/deps/audits) is the "coding brain" substrate for agents.
- Once confirmed: static inspect → local-only prototype → no external DB.

---

## Stop / Stop Skill (Tier-1)

- **Status:** source_needed — unchanged from N+6.22A.
- **Action:** operator confirms the exact tool/skill.
- Likely a Claude Code skill or hook for controlled agent stopping behavior.
- A Stop hook is already active in this profile (`~/.claude/stop-hook-git-check.sh`),
  so verify this is not a duplicate.

---

## DeepSeek / Provider Routing (Tier-1)

- **Status:** research_only — no API key, no live calls.
- **Progress:** routing plan documented in `model_provider_lane_n6_22a.md` (N+6.22A).
- **Pattern:** cheap long-context provider (DeepSeek) for wide passes; premium (Claude)
  for careful steps; local (Ollama/Gemma) where possible.
- **Gate:** secret-management milestone required before any live provider call.
- **N+6.30A update:** no change. Rust policy checker (N+6.28B) is the provider-agnostic
  safety layer; it can enforce policy regardless of which model runs the plan.

---

## Rust Runtime (Tier-1-after-main-accelerator)

- **Status:** **in active use** — N+6.28B merged.
- **N+6.28B delivers:** `rust/ghoti_policy_checker/` — a JSON policy checker that
  validates swarm plans (default-deny; blocks live launch, browser/computer-use, MCP,
  accounts, money, mass messaging, secrets, unknown capabilities).
- **Next:** wire bridge to `03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py`
  post N+6.29B merge.
- **Future Rust use:** high-performance agent runtime, file watchers, structured
  logging, local IPC — only when concrete use case is confirmed.

---

## Six Classification Lane Summary

| Lane | Current leader | Status |
|------|---------------|--------|
| `coding_brain_code_graph` | CodeGraph / Git Nexus | source_needed |
| `agent_skills_swarms` | am-will/swarms, ECC, claude-swarm | plans ready for isolated trial |
| `automation_money` | n8n, Composio (no keys yet) | deferred to secret-management milestone |
| `documents_content` | MarkItDown, Stirling PDF | deferred; not on critical path |
| `apps_products` | PAO memory palace app | Tier-1-last; build after agent stack proven |
| `apis_model_routing` | DeepSeek + Rust policy checker | research + Rust active; no live keys |
