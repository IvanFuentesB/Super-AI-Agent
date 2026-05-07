# Codex N+3.17 Money Experiment Helper Audit

Status: codex_audit_only / safe_script_spec / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 77bfb74

## Purpose

Design a safe future helper script for creating money experiment entries. This is a spec only. Codex did not create the script in this milestone.

Future script:

`03_scripts/money_workflow_new_experiment.py`

## Safety Goals

The helper should make it easy to add many planned experiments without enabling live business actions. It should only append local JSONL records and optionally create local artifact folders.

It must not:

- call external APIs
- post content
- sell products
- send email or outreach
- scrape platforms
- use live accounts
- open browsers
- run Docker/CUA
- install packages
- execute Gemma output
- modify files outside repo root

## CLI Arguments

Recommended args:

```text
--id <experiment_id>
--workflow-type <video_to_money|digital_product|content_batch|whop_plan|local_business|phone_game|other>
--hypothesis <text>
--product-or-offer <text>
--audience <text>
--channel <text>
--cost <number>
--time-budget <text>
--expected-revenue <number>
--risk-level <low|medium|high>
--approval-required <comma-separated approvals>
--files <comma-separated repo-relative paths>
--status <planned_not_started|drafting|approval_needed|published_manual|measuring|paused|killed|scaled>
--dry-run
--tracker 14_context/money_workflows/experiments/experiment_tracker.jsonl
```

Defaults:

- `status`: `planned_not_started`
- `cost`: `0`
- `actual_revenue`: `0`
- `content_count`: `0`
- `leads_count`: `0`
- `email_signups`: `0`
- `sales_count`: `0`
- `approval_required`: `["publish_approval"]` for any external channel

## Dry-Run Mode

Dry-run is mandatory for first use and should:

- print the JSON object
- print computed risk and approval flags
- print target tracker path
- not write any file
- exit 0 if validation passes

Sample dry-run:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --id money_20260428_001 --workflow-type digital_product --hypothesis "AI builders want a starter template pack" --product-or-offer "AI Operator Starter Kit" --audience "AI builders and students" --channel "manual_review_future_whop" --cost 0 --time-budget "2 hours" --expected-revenue 0 --risk-level low --approval-required publish_approval,pricing_approval
```

## JSONL Append Behavior

Real append should:

- create parent directory if inside repo root
- open tracker in append mode
- write exactly one compact JSON object per line
- preserve existing lines
- reject duplicate `id`
- reject invalid JSON in existing tracker
- validate all required fields before writing
- print the appended ID and tracker path

Sample safe real append:

```powershell
python 03_scripts/money_workflow_new_experiment.py --id money_20260428_001 --workflow-type digital_product --hypothesis "AI builders want a starter template pack" --product-or-offer "AI Operator Starter Kit" --audience "AI builders and students" --channel "draft_only" --cost 0 --time-budget "2 hours" --expected-revenue 0 --risk-level low --approval-required publish_approval,pricing_approval
```

## Required Fields

The helper should write:

- `id`
- `created_at`
- `status`
- `workflow_type`
- `hypothesis`
- `product_or_offer`
- `audience`
- `channel`
- `cost`
- `time_budget`
- `expected_revenue`
- `actual_revenue`
- `content_count`
- `leads_count`
- `email_signups`
- `sales_count`
- `lessons`
- `next_action`
- `risk_level`
- `approval_required`
- `files`

## Approval Required Logic

Always require approval for:

- `publish_approval` if channel is TikTok, Instagram, YouTube, X/Twitter, Reddit, LinkedIn, Whop, Gumroad, Lemon Squeezy, Shopify, Discord, email list, SEO/blog publishing, or any live platform.
- `account_approval` if channel implies a live account.
- `spend_approval` if cost is greater than zero.
- `outreach_approval` for cold/warm outreach.
- `legal_review` for legal/tax/finance claims.
- `risk_review` when risk is medium or high.

The helper should default to draft-only if approval fields are missing.

## Risk-Level Logic

Low risk:

- local artifact only
- no posting
- no account
- no spend
- no regulated claims

Medium risk:

- future publishing
- future platform account use
- business claims
- local-business research
- fitness/nutrition content

High risk:

- finance/investing
- legal/tax
- outreach
- paid tools
- live account automation
- scraped data
- app store/payment workflows

High-risk entries can be logged locally but must remain `approval_needed` before any external action.

## Validation Commands

Claude should run:

```powershell
python -m py_compile 03_scripts/money_workflow_new_experiment.py
python 03_scripts/money_workflow_new_experiment.py --dry-run --id money_test_001 --workflow-type digital_product --hypothesis "Test" --product-or-offer "Test product" --audience "builders" --channel "draft_only" --cost 0 --time-budget "30 minutes" --expected-revenue 0 --risk-level low --approval-required publish_approval
python -c "import json; [json.loads(line) for line in open('14_context/money_workflows/experiments/experiment_tracker.jsonl', encoding='utf-8') if line.strip()]; print('tracker jsonl ok')"
git diff --check
git diff --cached --check
```

## PASS Criteria

PASS means:

- dry-run writes nothing
- real append writes one valid JSONL line
- duplicate IDs are rejected
- required fields are enforced
- outside-repo tracker path is rejected
- high-risk/live channels require approval fields
- no external action occurs

## Blockers

Block the script if it:

- posts, emails, sells, scrapes, or opens live accounts
- installs dependencies
- runs browsers, Docker, CUA, Paperclip, OpenClaw, n8n, or Unity
- writes outside repo root
- silently overwrites tracker files
- allows missing approvals for live channels

## Recommendation

Implement this helper only after the money workflow templates exist. Keep it local, dry-run-first, append-only, and boring. Boring is the point here: a small reliable tracker beats a flashy agent that accidentally touches the real world.
