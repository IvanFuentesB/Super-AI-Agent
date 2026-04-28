# API-Saving Memory Workflow — N+3.15

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.15
Status: established / local_only / no_cap_bypass

---

## Goal

Reduce paid API token consumption by routing easy local text tasks to Gemma/Ollama
instead of Claude Code or Codex, without widening autonomy or bypassing safety gates.

---

## The Workflow

### Step 1 — Identify the task type

Before starting a Claude Code session, classify the task:

| Task | Route to |
|---|---|
| Summarize a local markdown file | Gemma (local, free) |
| Compress context for handoff | Gemma (local, free) |
| Draft a validation checklist | Gemma (local, free) |
| Classify task risk level | Gemma (local, free) |
| Independent audit / second opinion | Codex (copy-paste) |
| Hard multi-file implementation | Claude Code (paid) |
| Architecture / planning decisions | ChatGPT (human-operated) |

### Step 2 — Run Gemma for easy tasks

```
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py \
  --task compress_context \
  --input 14_context/current_state.md \
  --max-chars 12000
```

Check output at: `05_logs/local_brain_runs/<run_id>/response.txt`

### Step 3 — Use the compressed output in the next Claude Code prompt

Paste the Gemma summary into the next milestone prompt instead of the full file.
This reduces input tokens by 60–90% for large context files.

### Step 4 — Reserve Claude Code for what it's good at

Only use a Claude Code session when:
- The task requires multi-file edits
- A commit or push is needed
- Complex judgment about safety or architecture is required

---

## API Credit Savings Estimate

| Task | Claude Code cost | Gemma cost |
|---|---|---|
| Compress current_state.md (12k chars) | ~3,000–6,000 tokens | 0 tokens |
| Draft 5-item checklist | ~500–1,500 tokens | 0 tokens |
| Classify task risk | ~200–500 tokens | 0 tokens |

Every context compression run that uses Gemma instead of Claude Code saves approximately
3,000–6,000 input tokens per task. Over 10 sessions, this is 30,000–60,000 tokens saved.

This is NOT cap bypass or quota evasion. It is legitimate local compute using an already-installed
model (gemma3:4b via Ollama) to do tasks that do not require cloud-level reasoning.

---

## Obsidian / Vault Role

The `14_context/obsidian_vault/` notes are the canonical compact-state layer.
After a Gemma compression run, the human operator may copy key bullets into vault notes
for reference in future prompts. This further reduces token usage per session.

Vault notes location: `14_context/obsidian_vault/`
Key notes to update after compression: `01_Current_State.md`, `05_Safety_Gates.md`

---

## Skills Role

The `.claude/skills/` directory contains reusable skill definitions.
Skills are important and no new skills are being installed in N+3.15.
Future skills may wrap the compress_context workflow for one-command invocation.
For now, the raw CLI command is the interface.

---

## Multi-Agent Route

Current safe parallel agent setup:
1. **Claude Code** (this session) — hard implementation, commits, push
2. **Gemma via Ollama** (local) — compression, checklists, risk labels
3. **Codex** (copy-paste) — independent audits, analysis docs
4. **ChatGPT** (human-operated browser tab) — planning, strategy, new milestone prompts

Do NOT yet run autonomously: Paperclip, OpenClaw, n8n — all remain approval-gated.

---

## Paperclip / OpenClaw / n8n Status

These remain **planning_only** — not installed, not runtime-wired.
Explicit operator approval is required before any install or runtime wiring.
Worker cards for these candidates exist at `14_context/agent_registry/active_worker_cards_n3_14.md`.
