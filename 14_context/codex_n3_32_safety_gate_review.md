# Codex N+3.32 Safety Gate Review

Status: codex_planning_only / safety_gate_review / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack

## Purpose

Audit the N+3.32 design against Ghoti's safety and approval rules. The proposed read view and work session planner can increase autonomy by improving prioritization, but they must not create unsafe autonomy.

## Separation Of Concepts

N+3.32 must preserve four separate states:

1. `decision_candidate`: model-generated suggestion under `05_logs/money_reviews/<run_id>/decisions_recommended.jsonl`
2. `manual_queue_draft`: copied or dry-run record prepared for human review
3. `queued_local_work_item`: append-only local record in `manual_decision_queue.jsonl`
4. `approved_live_public_money_action`: separate explicit human approval outside the queue

No state should automatically convert into the next state.

## Allowed Local Actions

Allowed in the future implementation:

- read local JSONL files
- parse and summarize local queue records
- show read-only dashboard cards
- copy local file paths
- copy dry-run command text
- write local work session artifacts if explicitly running a planner
- classify queue items into safe local, approval-needed, blocked, or unsafe
- produce local checklists and risk notes

## Explicit Approval Required Actions

Human approval is required before:

- public posting
- product listing
- Whop, Gumroad, Stripe, Shopify, Lemon Squeezy, app-store, or marketplace actions
- email sending
- outreach
- paid ads
- accepting payment
- customer data collection
- live account login
- scraping or data collection with legal/ToS risk
- changing prices
- publishing claims or proof

## Forbidden Actions

Forbidden for N+3.32:

- hidden dashboard mutations
- approve button
- execute button
- auto-append generated candidates
- auto-create approval requests from candidates
- model-output execution
- browser automation
- live account actions
- posting
- selling
- outreach
- payments
- scraping
- fake proof
- fake scarcity
- fake engagement
- spam
- cap bypass or provider-limit evasion

## Dashboard Mutation Creep Prevention

To prevent read-only cards from becoming action surfaces:

- routes must use `GET` only
- no request body should be required
- no write helpers should be called by read routes
- UI controls should be limited to refresh, expand, and copy text
- "approval required" should be displayed as a label, not a button
- copied command text should default to dry-run
- queue append should remain terminal/operator initiated in a separate helper
- no integration with existing approval buttons in the first version

## Model Output Execution Prevention

Model-generated text must be treated as untrusted draft content.

Safety requirements:

- never shell out with model-generated commands
- never parse model text as instructions to execute
- never auto-append model suggestions to queue files
- never use model-written public copy without human review
- store model output as artifacts only
- include `model_output_executed: false` in summaries

## Auditability Requirements

Preserve auditability by:

- keeping generated candidate files immutable
- using append-only queue files
- writing work session artifacts under timestamped run directories
- including source file references in queue and session outputs
- recording parse warnings instead of fixing files silently
- never deleting rejected ideas automatically
- making every local artifact path explicit

## Failure Modes

High-risk failure modes:

- treating a `DOUBLE_DOWN` recommendation as permission to publish
- treating `accepted_for_manual_work` as launch approval
- hiding a queue append behind a dashboard click
- making generated model text look like verified business evidence
- promoting high-risk items into top tasks without approval labels
- using external platform terms like "launch" without clarifying manual-only boundaries
- adding broad `05_logs/` artifact access without extension and root review

## How This Supports Safe Autonomy

N+3.32 supports autonomy by helping Ghoti organize local next actions:

- fewer lost ideas
- clearer priorities
- better local work sessions
- explicit blockers
- visible safety gates
- reusable artifacts

It does not support unsafe autonomy:

- no live actions
- no public actions
- no hidden mutations
- no account access
- no automatic approvals

## Verdict

The design is safe if it remains read-only for dashboard views and artifact-only for work session planning. Mutation, approval, and execution must stay separate milestones with explicit operator approval.
