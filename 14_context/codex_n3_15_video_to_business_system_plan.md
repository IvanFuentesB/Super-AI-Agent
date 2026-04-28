# Codex N+3.15 Video-to-Business-System Plan

Status: codex_audit_plan_only / video_to_system_pipeline / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Purpose

Design a safe pipeline for turning money-making videos into compact business systems, product ideas, content calendars, and implementation tasks. This should save API credits by using local Gemma/Ollama for first-pass summarization and compression while reserving Claude Code, Codex, and ChatGPT for harder planning and implementation.

## Inputs

- YouTube URL.
- Transcript from manual copy, creator-provided captions, or approved legal/TOS-safe source.
- User notes.
- Screenshots supplied by the user or captured only after a separate approved capture workflow.
- Comments only if available through legal/TOS-safe means and only for high-level public sentiment.
- Optional metadata: creator, niche, video date, source link, and user goal.

## Pipeline

1. Intake one video into `14_context/money_workflows/<slug>/`.
2. Store source metadata and a compact transcript excerpt, not repeated full transcripts.
3. Run Gemma on the local transcript/notes to create a first-pass summary.
4. Extract the business model, tools, steps, costs, required assets, and risk points.
5. Produce product ideas and content angles from the extracted system.
6. Codex audits feasibility, TOS/legal risk, and missing assumptions.
7. User approves whether the system becomes a real project.
8. Claude Code implements templates or automation only after the plan is approved.

## Gemma Role

Gemma should handle:

- summarize transcript
- extract ordered steps
- identify tools mentioned
- detect costs and setup requirements
- create checklists
- create content angles
- create short risk labels
- compress notes for future prompts

Gemma should not:

- execute code
- edit repo files automatically
- decide to spend money
- post content
- contact people
- scrape platforms
- make legal, tax, or financial recommendations as final advice

## Codex Role

Codex should:

- audit whether the video logic is realistic
- identify platform/TOS/legal concerns
- compare extracted steps with existing Ghoti safety rules
- create planning docs and score product ideas
- check whether a workflow should be Gemma, Claude Code, or human-only
- verify that no fake engagement, spam, cap bypass, or deceptive automation is being proposed

## Claude Code Role

Claude Code should implement only after approval:

- repo-local templates
- markdown artifact generators
- local dashboard read models
- validation scripts
- local Gemma compression commands
- product scoring templates

Claude Code should not automate posting, live accounts, purchases, outreach, or paid tool usage without explicit approval.

## User Role

The user must approve:

- target niche
- product direction
- claims and pricing
- external research sources
- tool spending
- account use
- posting or scheduling
- outreach
- affiliate programs
- any workflow involving live platform actions

## Required Outputs

Each video workflow should produce:

- `video_summary.md`
- `extracted_business_model.md`
- `action_checklist.md`
- `product_ideas.md`
- `content_calendar.md`
- `risk_notes.md`

Suggested optional outputs:

- `tool_list.md`
- `cost_assumptions.md`
- `competitor_notes.md`
- `user_decision.md`

## Artifact Format

`video_summary.md`:

- source URL
- transcript source
- 5 bullet summary
- claimed opportunity
- key warnings

`extracted_business_model.md`:

- target customer
- offer
- acquisition channel
- delivery method
- monetization path
- required assets
- required tools

`action_checklist.md`:

- setup steps
- research steps
- product steps
- content steps
- approval gates
- blocked/later steps

`product_ideas.md`:

- idea
- buyer
- price range hypothesis
- effort
- risk
- first MVP

`content_calendar.md`:

- platform
- hook
- format
- asset needed
- call to action
- approval status

`risk_notes.md`:

- legal/TOS risk
- rights/copyright risk
- financial claim risk
- platform risk
- privacy/security risk
- manual approval required

## Memory Strategy

- Store compact summaries under `14_context/money_workflows/`.
- Do not paste full transcripts into future prompts unless specifically needed.
- Use source file references and short excerpts.
- Keep one `index.md` per workflow folder.
- Promote only stable lessons into Obsidian/vault notes.
- Archive bulky inputs outside prompts and summarize them through Gemma.

## Approval Gates

- No posting without approval.
- No spending without approval.
- No scraping beyond legal/TOS-safe use.
- No fake engagement.
- No spam.
- No autonomous live-account action.
- No copying a creator's paid product or course.
- No using AI-generated likenesses or copyrighted assets without rights review.

## First MVP

Create one manual workflow folder from a user-provided transcript:

```text
14_context/money_workflows/<video_slug>/
  video_summary.md
  extracted_business_model.md
  action_checklist.md
  product_ideas.md
  content_calendar.md
  risk_notes.md
```

Gemma can draft the first pass locally. Codex reviews. The user approves whether Claude Code turns the format into a reusable CLI/template workflow later.
