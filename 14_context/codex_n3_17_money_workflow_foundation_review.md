# Codex N+3.17 Money Workflow Foundation Review

Status: codex_audit_only / foundation_review / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 77bfb74

## Purpose

Review the repo-local money workflow foundation that Claude Code should implement next. The foundation should turn the N+3.15 and N+3.16 planning docs into usable templates without posting, scraping, selling, sending outreach, using accounts, or connecting paid tools.

## Recommended Folder Structure

```text
14_context/money_workflows/
  README.md
  money_os_index.md
  templates/
    experiment_tracker.schema.json
    video_to_money_intake_template.md
    digital_product_shot_template.md
    content_batch_template.md
    simple_phone_game_pipeline.md
    whop_workflow_plan.md
    distribution_and_exposure_checklist.md
  experiments/
    experiment_tracker.jsonl
  video_intake/
  product_cards/
  content_batches/
  distribution/
05_logs/money_workflow_runs/
```

The structure should start as markdown, JSON, and JSONL only. No dashboard, database, live API, or account integration is needed yet.

## Required Artifacts

### `money_os_index.md`

Why it matters:

- Gives the user one place to see the numbers-game operating system.
- Links templates, experiments, product cards, content batches, and distribution checklists.
- Keeps future Claude/Codex/Gemma prompts compact by referencing paths instead of pasting old context.

Required content:

- core money OS principle
- weekly cadence
- approval gates
- top workflows
- links to tracker and templates

### `experiment_tracker.schema.json`

Why it matters:

- Makes experiments measurable and machine-checkable.
- Allows many shots to be recorded consistently.
- Creates a future bridge to dashboard cards or SQLite.

Required fields:

- id, created_at, status, workflow_type, hypothesis, product_or_offer
- audience, channel, cost, time_budget
- expected_revenue, actual_revenue
- content_count, leads_count, email_signups, sales_count
- lessons, next_action, risk_level, approval_required, files

### `experiment_tracker.jsonl`

Why it matters:

- Append-friendly experiment log.
- Easy to diff and validate.
- Good first format before SQLite or dashboard routes.

Starter planned entries:

- `video_to_business_system_extractor`
- `digital_product_prompt_pack_test`
- `faceless_short_form_batch_test`

Each should be `planned_not_started`, with no live URL and no revenue claim.

### `video_to_money_intake_template.md`

Why it matters:

- Converts videos, transcripts, course notes, and market observations into products and experiments.
- Keeps Gemma work artifact-only and source-truth-aware.

Must include:

- source title and link/reference
- transcript/notes source truth
- main claim
- monetization mechanism
- skills, tools, cost, time required
- proof quality
- risks and TOS/legal notes
- 3 MVP experiments
- 5 productizable templates
- 10 content angles
- approval checklist

### `digital_product_shot_template.md`

Why it matters:

- Converts ideas into sellable digital products without overthinking.
- Supports the numbers-game strategy by making product cards fast.

Must include:

- product name
- buyer
- pain solved
- promised outcome
- format
- production time
- price hypothesis
- distribution channel
- email-list hook
- proof needed
- MVP version
- upsell path
- scores and final priority

### `content_batch_template.md`

Why it matters:

- Forces every product idea to have exposure attached.
- Supports TikTok, Instagram Reels, YouTube Shorts, X/Twitter, LinkedIn, Reddit where allowed, email, and SEO/blogs later.

Must include:

- platform
- theme
- 10 hooks
- 10 short scripts
- CTA
- email capture idea
- product link placeholder
- posting schedule
- repurposing plan
- metrics
- approval status

### `simple_phone_game_pipeline.md`

Why it matters:

- Captures the future simple mobile game lane without installing Unity or Unity-MCP now.
- Lets the user evaluate tiny game concepts as product shots.

Must include:

- game idea
- target audience
- simplest prototype
- monetization hypothesis
- asset needs
- validation plan
- Unity-MCP future note
- no Unity/App Store/Google Play actions yet

### `whop_workflow_plan.md`

Why it matters:

- Whop can be a product/community distribution lane.
- The first step should be product planning, not account automation.

Must include:

- product concept
- buyer
- price hypothesis
- fulfillment assets
- listing copy draft
- support boundary
- manual publish checklist
- no live Whop account action without approval

### `distribution_and_exposure_checklist.md`

Why it matters:

- Products need exposure.
- Every experiment should include audience and channel thinking from day one.

Must include:

- social channels
- email-list lead magnet
- community rules
- anti-spam rules
- owned-account-only rules
- metrics to track
- kill/iterate/scale decision

## Numbers-Game Template Requirements

Each template should make repeated shots easy:

- one idea per card
- fast MVP first
- score effort, speed, upside, confidence, and risk
- define distribution before building
- define metrics before publishing
- include kill criteria
- record user energy/interest
- keep approval gates visible

## Exposure and Email-List Requirements

Every experiment should answer:

- Who sees this?
- Why would they care?
- What is the lead magnet?
- What is the call to action?
- Where does email capture happen later?
- What content can be repurposed?
- What platform rules apply?

Email-list-first does not mean immediate email tool integration. It means every product/content idea should include a consent-based lead magnet and future opt-in concept.

## Live Action Approval Gates

Human approval is required before:

- publishing
- outreach
- spending money
- using accounts
- scraping or platform data collection
- paid media tools
- Whop/Gumroad/Lemon Squeezy/Shopify actions
- app store actions
- email list setup
- legal/tax/finance actions

## Current Recommendation

Claude Code should implement the folder and templates first, then add a small local helper script only after the templates are stable. Do not build dashboard routes, n8n workflows, Paperclip orchestration, OpenClaw workers, Unity workflows, or live posting rails in this step.
