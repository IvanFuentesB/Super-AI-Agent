# Codex N+3.15 Next Claude Money Workflow Prompt Review

Status: codex_audit_plan_only / next_claude_scope_review / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Recommended Next Claude Code Milestone

N+3.16 Claude - Money Workflow Intake and Video-to-Business-System Templates

## Why This Should Come Before Paperclip/OpenClaw/n8n Installs

- It creates money-focused artifacts immediately.
- It uses the already-working Gemma/Ollama local brain for cheap summaries and drafts.
- It does not require new installs, live accounts, Docker, Paperclip, OpenClaw, or n8n.
- It creates clear folder formats that future orchestrators can consume later.
- It keeps posting, spending, outreach, and platform actions manual and approval-gated.

## Exact Implementation Scope

Claude Code should create repo-local planning assets only:

- `14_context/money_workflows/README.md`
- `14_context/money_workflows/templates/video_summary.template.md`
- `14_context/money_workflows/templates/extracted_business_model.template.md`
- `14_context/money_workflows/templates/action_checklist.template.md`
- `14_context/money_workflows/templates/product_ideas.template.md`
- `14_context/money_workflows/templates/content_calendar.template.md`
- `14_context/money_workflows/templates/risk_notes.template.md`
- `14_context/money_workflows/templates/product_idea_scoring.template.md`

Optional if scoped and safe:

- update `23_configs/local_brain_router_policy.example.json` to add a preview-only `money_video_summary` or `business_system_extract` task class
- add a small sample workflow folder using synthetic placeholder content only
- add wait/resume seed reminding that money workflows are manual-review only

## Required Behavior

- Input is user-provided transcript, notes, or legal/TOS-safe source material.
- Output is artifact-only markdown.
- Gemma can draft first-pass summaries and checklists.
- No model output is executed.
- No repo edits are made from Gemma output without Claude/Codex/human review.
- No live posting, account automation, paid tools, scraping, outreach, purchasing, or money movement.

## Validation Checklist

Claude should run:

- `git status --short`
- `git diff --check`
- targeted `git diff --check -- 14_context/money_workflows`
- JSON validation if policy config is edited
- relevant Python/Node syntax checks only if implementation files are edited
- `git diff --cached --name-status` before commit

Acceptance criteria:

- templates exist and are readable
- each template includes approval gates
- first MVP path is documented
- Gemma role is local/text-only
- no external services are connected
- no runtime wiring is added
- no blocked dirty files are staged

## Files Claude Should Edit Later

Allowed for the N+3.16 implementation:

- `14_context/money_workflows/**`
- `23_configs/local_brain_router_policy.example.json` only if adding preview-only routing policy
- `14_context/current_state.md` if Claude owns state updates for that milestone
- `14_context/next_actions.md` if Claude owns state updates for that milestone
- `14_context/ghoti_finish_line_log.md` if Claude owns finish-line logging

## Files Claude Should Not Touch

- `14_context/ghoti_current_prompt.md`
- `14_context/ghoti_current_prompt_N1_6.md`
- third-party repo contents
- `.claude/skills/`
- CV docs
- `output/`
- runtime code unless the user explicitly converts the milestone into an implementation lane
- dashboard code unless a later milestone explicitly requests a read-only view

## Exact Next Scope Summary

Build the money workflow folder and templates first. Then run one manual example from a user-provided transcript or notes. Keep Gemma as the cheap local drafting brain, Codex as audit/review, Claude Code as template implementer, and the user as the approval gate for niches, products, platforms, posts, spending, accounts, and claims.
