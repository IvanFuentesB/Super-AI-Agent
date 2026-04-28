# API Saving and Agent Routing Summary — N+3.14

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.14

---

## Local Gemma Now Usable for Easy Tasks

Gemma3:4b via Ollama is confirmed working (smoke: GHOTI_LOCAL_BRAIN_OK, N+3.13).
A local brain router (preview_only, enabled=false) now exists and can run safe preview tasks.
The router is ready to handle easy task classes without any paid API call.

Easy task classes available for local routing:
- summarize_local_markdown
- classify_task_risk
- draft_checklist
- compress_context
- suggest_worker_card

## How This Saves API Credits

Each easy task routed to Gemma/Ollama locally instead of Claude Code or Codex:
- Costs zero paid API tokens
- Returns results in seconds (model already loaded)
- Does not require a cloud round-trip
- Is not a cap bypass or quota evasion — this is legitimate local compute

Estimated savings: every context-compression or checklist task sent locally instead of to Claude
saves approximately 1,000–5,000 tokens per task.

## What Still Needs Claude Code / Codex

- Hard multi-file implementation (CLAUDECODE-IMPLEMENT-001)
- Complex reasoning across many files
- Milestone delivery, validation, staging, commit, push
- Any task requiring judgment about unsafe actions

What still needs Codex:
- Independent audits
- Second opinions on docs or code
- Standalone analysis files

What still needs ChatGPT:
- High-level architecture planning
- Roadmap decisions
- Prompt engineering for new milestones

## Safe Parallel Agent Count

Currently safe to run in parallel:
- 1 Claude Code session (this session)
- 1 Codex session (copy-paste, independent)
- 1 local Gemma inference (via ollama, local-only)
- ChatGPT (human-operated, separate browser tab)

Do NOT yet run:
- Paperclip (not installed)
- OpenClaw runtime (not wired)
- n8n (not installed)
- Autonomous external actions of any kind

## Next Step

Route one simple context compression task through Gemma/Ollama and compare output quality
against a Claude Code or Codex equivalent. If acceptable, enable compress_context routing
in the policy (set enabled=true for that class only after review).

Milestone recommendation: N+3.15 — Local Gemma Context Compression Route
(saves API credits now; can be validated quickly against a real compact_memory file).
