# Plug-and-Play Swarm & Memory Tool Intake (N+6.30A)

**Milestone:** N+6.30A
**Date:** 2026-06-07
**Status:** static planning only — no install, no clone, no execution, no live agent launch
**Base main:** `ca90fbd` (N+6.28B Rust policy checker merged)
**Prior intake building on:** N+6.12A, N+6.22A, N+6.24A, N+6.26A, N+6.27A, N+6.28A

## Dependency State

| Branch | Status | Impact |
|--------|--------|--------|
| N+6.27B swarm_launcher | merged | swarm_launcher patterns active |
| N+6.28B Rust policy checker | merged | Rust safety layer active |
| N+6.29B computer_use_adapter | not merged | computer_use_adapter files untouched |

---

## Plug-and-Play Tool Ranking

### Tier A — Use Now in Main Claude Profile

| Tool | Source | License | Why Now | Risk |
|------|--------|---------|---------|------|
| **Subagents (built-in)** | Official | Anthropic TOS | Already in use; lowest blast radius | Low |
| **Skills (built-in)** | Official | Anthropic TOS | Model-invoked, no agent spawning | Low |

**Action:** continue using subagents and skills. Spawn with explicit read-only instructions.
Do not add hooks, agent teams, or dynamic workflows until dedicated milestone.

### Tier B — Use Soon (Separate Throwaway Profile → Ghoti Adapt)

| Tool | Source | License | Why Soon | Risk |
|------|--------|---------|---------|------|
| **am-will/swarms** | `github.com/am-will/swarms` | unverified | Skills-based, no server | Medium |
| **ECC (affaan-m/ecc)** | `github.com/affaan-m/ecc` | MIT ✓ | Governance/skill patterns | Medium |
| **affaan-m/claude-swarm** | `github.com/affaan-m/claude-swarm` | MIT ✓ | Dep-graph + file conflict | Medium-High |

**Action:** trial in isolated throwaway profile (no Ghoti repo, no real accounts). Follow
`ecc_ruflo_swarm_trial_plan_n6_30a.md` sequence.

### Tier C — Inspect More / Source Needed

| Tool | Status | Action |
|------|--------|--------|
| **Claude Mem** | source_needed | Operator confirms exact repo/tool |
| **Obsidian-skills** | source_needed | Operator confirms exact source |
| **MemPalace (agent memory)** | source_needed | Distinct from PAO app (N+6.24A) |
| **UI-TARS** | source_needed | Operator confirms exact upstream (model vs app vs SDK) |
| **ClawTeam** | needs sandbox trial | Read README fully; sandbox before any use |
| **Paperclip** | source_needed (Tier-1) | Operator confirms exact repo |
| **Understand-Anything** | source_needed (Tier-1) | Operator confirms exact repo |
| **CodeGraph / Git Nexus** | source_needed (Tier-1) | Operator confirms exact repo |
| **Stop / Stop skill** | source_needed (Tier-1) | Operator confirms exact repo |

### Tier D — Defer

| Tool | Why Defer |
|------|-----------|
| **Dynamic Workflows** | Research preview; executes generated JS; very high token cost |
| **Agent Teams** | Experimental; 2-16 live agents; highest blast radius |
| **Background Agents (/bg)** | Unmonitored async surface; off until kill-switch milestone |
| **TryCUA / CUA** | Patterns used in N+6.29A; real use needs Docker + sandbox gate |
| **MemPalace PAO app** | Future product (N+6.24A); Tier-1-last |

### Tier E — Avoid

| Tool | Why Avoid |
|------|-----------|
| **Ruflo / Claude Flow** | Supply-chain history: malicious npm pre-install, MCP prompt-injection #1375, SQL injection. Patterns only; never install. |
| **kyegomez/swarms (enterprise)** | Different owner/project from am-will/swarms; Tier-2 at best; not evaluated yet |

---

## What Is Automatic vs Manual

| Surface | Auto/Manual | Token Cost | Ghoti Default |
|---------|-------------|-----------|---------------|
| Subagents | model-invoked | moderate | guidance_only |
| Skills | model-invoked | low | guidance_only |
| am-will/swarms parallel-task | skill-invoked; up to 15 agents | moderate-high | study_then_guidance |
| ECC | manual install; model-invoked per skill | low-per-skill | adapt_guidance_only |
| affaan-m/claude-swarm | manual trigger; semi-auto | moderate-high | should_stay_disabled |
| ClawTeam | one-command; full automation | high | should_stay_disabled |
| Agent Teams | experimental env var; 2-16 auto | very high | should_stay_disabled |
| Dynamic Workflows | manual `/workflows`; auto JS runtime | very high | should_stay_disabled |
| Background Agents | manual `/bg`; then async | moderate-high | should_stay_disabled |
| Ruflo | install hooks run on npm install | high | should_stay_disabled |

## What Burns the Most Credits

1. **Agent Teams** — 2-16 parallel live model contexts; experimental
2. **Dynamic Workflows** — many subagents from generated JS
3. **Background Agents** — parallel async sessions
4. **am-will/swarms parallel-task** — rolling pool up to 15 subagents
5. **ClawTeam** — full automation, unbounded agent count

## What Creates Files / Scripts Without Explicit Approval

- **Ruflo** — install hooks run code on `npm install` before you can inspect
- **ClawTeam** — "full automation" goal; likely auto-commits
- **Dynamic Workflows** — generates JS and executes it; can create files
- **Agent Teams** — each agent has Write tool access by default
- **ECC hooks** — if wired; run arbitrary commands at session/stop events

**The safe ones:** subagents + skills + read-only Explore agents do not create files if
given explicit no-write instructions.

---

## Attribution / License Table

| Tool | License | Code Copied | Attribution Needed |
|------|---------|-------------|-------------------|
| am-will/swarms | unverified | no | verify before any snippet |
| ECC (affaan-m/ecc) | MIT | no | copyright notice if snippet reused |
| affaan-m/claude-swarm | MIT | no | copyright notice if snippet reused |
| ClawTeam (HKUDS/ClawTeam) | MIT | no | copyright notice if snippet reused |
| TryCUA/CUA | MIT | no (patterns adapted in N+6.12A) | recorded in N+6.29A manifest |
| Ruflo | MIT | no | never install; supply-chain risk |
| UI-TARS | Apache-2.0 (reported) | no | source_needed; NOTICE if snippet |
| Claude Mem | unknown | no | source_needed |
| Obsidian-skills | unknown | no | source_needed |
| MemPalace (agent) | unknown | no | source_needed |
