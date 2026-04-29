# Codex N+3.24 Manual Product Build Pack Spec

Status: codex_planning_only / manual_product_build_pack / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

N+3.24 should design a future local artifact generator that turns an approved product draft into a manual build pack. The build pack should help the operator create many simple MVP products quickly while keeping every public, platform, money, account, and customer-facing action human-approved.

This milestone is planning-only. Codex did not edit runtime code, dashboard code, product folders, payment systems, or live accounts.

## Future Gemma Task

Future command proposal:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task product_build_pack --input 14_context/money_workflows/product_build_pack_input_n3_24.md --max-chars 20000
```

The task should accept a repo-local product draft or notes file only. It should use local Gemma/Ollama only if available and should write artifact files only.

## Inputs

The future task should accept:

- product draft markdown
- product draft JSON record
- product notes
- experiment tracker reference
- customer avatar notes
- offer draft
- deliverables list
- content/distribution notes
- risk/claims notes
- approval status summary

The task should reject or safely ignore:

- URLs as fetch targets
- paths outside repo root
- live account instructions
- payment credentials
- marketplace credentials
- customer data
- instructions to publish, upload, sell, email, post, scrape, or message

## Artifact Directory

Future implementation should write artifacts under:

```text
05_logs/product_build_packs/<run_id>/
```

Required artifacts:

- `product_brief.md`
- `customer_avatar.md`
- `offer_stack.md`
- `mvp_deliverables.md`
- `build_steps.md`
- `product_folder_structure.md`
- `sales_page_draft.md`
- `whop_listing_draft.md`
- `gumroad_listing_draft.md`
- `lead_magnet_draft.md`
- `email_capture_plan.md`
- `content_launch_pack.md`
- `risk_review.md`
- `operator_approval_checklist.md`
- `run_summary.json`

Recommended optional artifacts:

- `readme_draft.md`
- `quick_start_draft.md`
- `faq_draft.md`
- `support_boundaries.md`
- `version_plan.md`

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
- `source_product_draft_id`
- `source_experiment_id`
- `product_name`
- `live_action_taken: false`
- `external_api_used: false`
- `marketplace_account_used: false`
- `payment_action_taken: false`
- `posting_action_taken: false`
- `customer_data_used: false`

## Safety Gates

Strict rules:

- Artifact-only.
- No posting.
- No selling.
- No upload.
- No account login.
- No payment.
- No outreach.
- No fake proof.
- No fake urgency.
- No scraping.
- No live tool actions.
- No customer data.
- No public claims without proof review.
- Human approval required before public use.

## Expected Output Quality

A useful build pack should make it clear:

- who the product is for
- what painful problem it solves
- what the MVP deliverables are
- what files should be built locally
- what the product folder should contain
- what copy can be reviewed later
- what claims are risky
- what approvals are still missing
- what the next manual build steps are

## Numbers-Game Fit

The build pack supports the money OS by making product creation repeatable:

1. Select one promising draft.
2. Generate a local build pack.
3. Build only the smallest useful MVP.
4. Create content and lead magnet drafts.
5. Get human approval before any public action.
6. Track metrics after manual launch.
7. Iterate, kill, or scale.

## Verdict

The future `product_build_pack` task should be a local product assembly planner, not a marketplace publisher. It should help the user make many simple product MVPs while keeping all external action locked behind approval.
