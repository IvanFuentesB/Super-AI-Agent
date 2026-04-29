# Codex N+3.22 Digital Product Pipeline Spec

Status: codex_planning_only / digital_product_draft_pipeline / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

N+3.22 should turn experiments, content batches, and product ideas into draft-only digital product offers. The goal is to increase the number of ethical product shots without touching live stores, payments, accounts, uploads, public claims, or platform actions.

This is the next layer after the content batch and shot production system: content creates exposure, exposure reveals demand, and demand should feed small product drafts that can be reviewed before any public or money-facing action.

## Future Command Proposal

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task digital_product_draft --input 14_context/money_workflows/product_draft_input_n3_22.md --max-chars 20000
```

This future command should use local Gemma/Ollama only if available. It must read repo-local files only and write artifacts only.

## Inputs

The future pipeline should accept one repo-local `.md`, `.txt`, or `.json` input containing:

- experiment or product idea
- target customer
- painful problem
- desired outcome
- offer or bundle concept
- source notes or transcript excerpt
- content angles
- distribution plan
- optional experiment score or bucket
- optional content shot references
- required safety notes

The pipeline should reject or safely ignore:

- URLs as fetch targets
- paths outside the repo root
- live account identifiers
- payment credentials
- platform API keys
- binary uploads
- instructions to publish, list, sell, email, scrape, or message

## Required Outputs

The product draft should include:

- product positioning
- product name ideas
- claim-safe headline options
- offer stack
- module or asset outline
- MVP deliverables
- pricing ladder
- Whop listing draft
- Gumroad-style listing draft
- landing page draft
- email capture lead magnet
- FAQ and objection handling
- fulfillment checklist
- risk and claims review
- next 10 actions

All outputs are drafts for human review.

## Artifact Directory

Future implementation should write to:

```text
05_logs/product_drafts/<run_id>/
```

Recommended files:

- `request.json`
- `source_brief.md`
- `response.txt`
- `product_positioning.md`
- `name_and_headline_options.md`
- `offer_stack.md`
- `mvp_deliverables.md`
- `pricing_ladder.md`
- `whop_listing_draft.md`
- `gumroad_listing_draft.md`
- `landing_page_draft.md`
- `lead_magnet.md`
- `faq_objections.md`
- `fulfillment_checklist.md`
- `risk_claims_review.md`
- `next_10_actions.md`
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
- `product_name_count`
- `headline_count`
- `pricing_ladder_present`
- `listing_draft_present`
- `risk_review_present`
- `live_action_taken: false`
- `external_api_used: false`
- `store_account_used: false`
- `payment_action_taken: false`
- `public_claims_published: false`

## No-Live-Action Rules

- No Whop account action.
- No Gumroad, Stripe, Lemon Squeezy, Shopify, or payment action.
- No product upload.
- No live listing creation.
- No pricing activation.
- No public landing page publish.
- No email capture setup.
- No email send.
- No social posting.
- No fake proof or fabricated testimonials.
- No scraped or purchased contact lists.
- No income, health, legal, financial, or business guarantees.

## Numbers-Game Fit

The pipeline should make it cheap to draft many product shots:

1. One experiment becomes one product draft.
2. One product draft becomes one lead magnet, one content batch, one listing draft, and one fulfillment checklist.
3. Weak product drafts are paused or killed quickly.
4. Strong product drafts move to human review, then manual asset creation, then explicit approval before publishing.

## Validation Plan

Claude Code should later validate with:

```powershell
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py', encoding='utf-8').read()); print('LOCAL ROUTER AST OK')"
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task digital_product_draft --input 14_context/money_workflows/product_draft_input_n3_22.md --max-chars 20000
git diff --check
```

If product JSONL or schema files are added, validate JSON and JSONL parsing separately.

## Verdict

The safest next product step is a local, artifact-only `digital_product_draft` task. It helps Ghoti create more product shots without crossing into selling, platform operations, payments, or public claims.
