# API-Saving Memory Workflow — N+3.17

Date: 2026-04-28
Milestone: N+3.17
Branch: feat/ghoti-visible-operator-stack
Status: established / updated / no_cap_bypass

---

## Core Rule

Gemma handles free easy local text work.
Claude Code handles hard multi-file implementation.
Codex handles audits and analysis docs.
ChatGPT handles planning and prompts.

This is not cap bypass. It is legitimate local compute.

---

## Updated Task Routing Table

| Task | Route to | Why |
|---|---|---|
| Summarize local markdown / doc | Gemma (free) | Local only, no reasoning needed |
| Compress context for handoff | Gemma (free) | Reduces Claude Code input tokens by 60–90% |
| Draft validation checklist | Gemma (free) | Simple structured output |
| Classify task risk level | Gemma (free) | Pattern matching, no hard judgment |
| Draft product ideas from notes | Gemma (free) | First pass only; operator reviews |
| Draft 10 content hooks | Gemma (free) | First pass only; operator reviews |
| Video/transcript → core lesson | Gemma (free) | Compression + extraction |
| Experiment tracker entry draft | Gemma (free) | Structured output, template fill |
| Independent audit / second opinion | Codex (copy-paste) | No live actions |
| Hard multi-file implementation | Claude Code (paid) | Commits, validation, push |
| Architecture / planning / strategy | ChatGPT (human-operated) | High-level reasoning |
| New milestone prompt generation | ChatGPT (human-operated) | Context-setting, sequencing |

---

## How to Use Before Each Claude Code Session

1. Run Gemma compression on the largest context file:
   ```
   python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py \
     --task compress_context \
     --input 14_context/current_state.md \
     --max-chars 12000
   ```
2. Read output at: `05_logs/local_brain_runs/<run_id>/response.txt`
3. Paste compressed bullets into the next milestone prompt instead of the full file.
4. Save 3,000–6,000 tokens per session.

---

## Money Workflow Extension (N+3.17)

Gemma is now the first-pass processor for money workflow intake:

1. Save raw video notes or transcript to a local markdown file
2. Run `compress_context` to get a structured summary
3. Copy summary bullets into `video_to_money_intake_template.md`
4. Use `money_workflow_new_experiment.py` to generate experiment tracker entries
5. Review all outputs before any external action

Gemma never posts, sells, emails, or takes live actions. All outputs are artifacts.

---

## Credit Savings Estimate

| Task | Claude Code cost | Gemma cost |
|---|---|---|
| Compress current_state.md (12k chars) | ~3,000–6,000 tokens | 0 tokens |
| Draft 10 content hooks | ~500–1,500 tokens | 0 tokens |
| Draft product outline | ~500–1,000 tokens | 0 tokens |
| Classify 5 experiment risks | ~200–400 tokens | 0 tokens |

Over 10 sessions: estimated 30,000–60,000 tokens saved by routing to Gemma.

---

## Paperclip / OpenClaw / n8n Status

Remain planning_only. No install, no runtime wiring. See `14_context/tooling_intake_priority_n3_17.md`.
