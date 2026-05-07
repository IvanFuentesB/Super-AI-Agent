# Codex N+3.21 Content Batch Planner Spec

Status: codex_planning_only / content_batch_planner_spec / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

The N+3.21 content batch planner should turn one approved local product or experiment brief into a large batch of reusable content ideas. This supports the numbers-game money operating system: more shots, more content, faster feedback, more exposure, and better learning, while keeping every public or money-facing action human-approved.

This milestone is planning-only for Codex. Claude Code should implement later only after N+3.18 is finished or explicitly paused.

## Future Command Proposal

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task content_batch --input 14_context/money_workflows/content_batch_input_n3_21.md --max-chars 20000
```

The command should use local Gemma/Ollama only if already configured. It must not call external APIs, browse the web, scrape platforms, post content, send email, sell products, or touch live accounts.

## Planner Inputs

The planner should accept a repo-local `.md`, `.txt`, or `.json` brief containing:

- product idea
- target customer
- painful problem
- offer or promised outcome
- platform list
- optional transcript or notes artifact path
- optional experiment score or bucket
- optional product card path
- optional distribution constraints
- required safety notes

The input must stay inside the repo root. Absolute paths outside the repo, URLs as fetch targets, binary files, and live platform identifiers should be rejected or treated as plain text only.

## Required Outputs

The generated batch should include:

- 30 short-form hooks
- 10 long-form content ideas
- 10 email ideas
- 10 community or social post ideas
- 5 lead magnet ideas
- 5 CTA variants
- repurposing map
- safety and claims review
- weekly posting calendar draft
- next 10 shots execution list

All outputs are drafts for review. They are not instructions to publish.

## Artifact Directory

Future implementation should write artifacts under:

```text
05_logs/content_batches/<run_id>/
```

Recommended artifact files:

- `request.json`
- `source_brief.md`
- `short_form_hooks.md`
- `long_form_ideas.md`
- `email_ideas.md`
- `community_post_ideas.md`
- `lead_magnet_ideas.md`
- `cta_variants.md`
- `repurposing_map.md`
- `safety_claims_review.md`
- `weekly_posting_calendar.md`
- `next_10_shots.md`
- `next_10_shots.jsonl`
- `run_summary.json`

## Run Summary Fields

`run_summary.json` should include:

- `run_id`
- `created_at_utc`
- `task`
- `input_path`
- `max_chars`
- `model`
- `artifact_dir`
- `output_files`
- `short_form_hook_count`
- `long_form_idea_count`
- `email_idea_count`
- `community_post_count`
- `lead_magnet_count`
- `cta_variant_count`
- `safety_review_present`
- `live_action_taken: false`
- `external_api_used: false`
- `posting_performed: false`

## Safety Rules

- Read local files only.
- Generate artifacts only.
- Never execute model output.
- Never auto-commit model output.
- Never post, send, sell, list, buy, scrape, or message.
- Never use live accounts.
- Never make fake income claims or fake proof.
- Never suggest fake engagement, bots, comment spam, purchased lists, or misleading testimonials.
- Require human approval before any public, platform, money, outreach, or account action.

## Validation Plan

Claude Code should later validate with:

```powershell
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py', encoding='utf-8').read()); print('LOCAL ROUTER AST OK')"
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task content_batch --input 14_context/money_workflows/content_batch_input_n3_21.md --max-chars 20000
git diff --check
```

If a schema or JSONL template is added, validate it with `python -m json.tool` or a line-by-line JSONL parse.

## Verdict

The next content milestone should be an artifact-only Gemma content batch planner. It is useful because exposure is the bottleneck, but it stays safe because it drafts content without publishing or touching live accounts.
