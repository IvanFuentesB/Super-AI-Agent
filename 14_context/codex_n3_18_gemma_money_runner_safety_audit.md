# Codex N+3.18 Gemma Money Runner Safety Audit

Status: codex_audit_only / safety_review / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 6be07a5

## Purpose

Audit the safety boundaries for a future Gemma-powered video-to-money runner. The runner should help create local planning artifacts, not operate a business autonomously.

## Non-Negotiable Boundaries

- Local-only input.
- Artifact-only output.
- No URL fetch.
- No scraping.
- No YouTube download.
- No external API.
- No model output execution.
- No live posting.
- No selling/listing/uploading.
- No outreach/email/DM sending.
- No payment, purchase, subscription, trade, or money movement.
- No app-store action.
- No fake proof.
- No fake engagement.
- No spam.
- No live account login.
- No Paperclip/OpenClaw/n8n/Unity-MCP/Manus/Dolphin/CUDA runtime use.

## Input Safety

Allowed:

- user-provided local transcript `.md` or `.txt`
- user-provided course notes
- user idea notes
- existing money workflow template text
- output from local Gemma compression artifacts

Rejected:

- URLs as source to fetch
- credentials
- private customer data
- bank/payment/account data
- third-party copyrighted content copied into repo without rights
- files outside repo root
- binary/media files
- CV docs or unrelated private docs unless explicitly requested by the user

## Output Safety

Allowed:

- markdown summaries
- internal product ideas
- internal content angles
- internal distribution plan
- internal risk checklist
- local experiment candidates
- local approval checklist

Rejected:

- direct posts
- emails/DMs
- store listing uploads
- API calls
- executable scripts generated from model output
- auto-modification of source docs
- auto-append to canonical tracker without review

## Model Output Truth

Gemma output must be treated as draft text:

- may hallucinate
- may invent proof
- may miss legal/TOS risks
- may generate generic business advice
- must be reviewed by operator/Codex/Claude before use

The runner should label output as:

`draft_from_local_model / requires_human_review`

## Fake Proof Guard

The runner must not:

- invent revenue
- invent testimonials
- invent sales
- invent follower counts
- invent case studies
- imply the operator has results not actually achieved

Every proof claim should be one of:

- `none_yet`
- `operator_verified`
- `artifact_linked`
- `needs_validation`

## Anti-Spam Guard

The runner can draft outreach scripts only as internal review artifacts if a later milestone approves that feature. For N+3.18, it should not generate or queue outreach. Distribution plans can include "manual outreach later" only as approval-blocked.

Forbidden:

- mass cold email
- scraped lead lists
- automated DMs
- comment bots
- follow/unfollow
- engagement pods
- fake reviews

## Money-Facing Approval Gates

Human approval required before:

- public content
- store listing
- price test
- Whop/Gumroad/Lemon Squeezy/Shopify action
- email list setup
- email send
- outreach
- paid tool usage
- domain/hosting purchase
- app-store account or submission
- affiliate link
- ad spend
- legal/tax/finance content

## Runner PASS Criteria

PASS means:

- source path is repo-local and text-only
- all outputs are under `05_logs/money_workflow_runs/<run_id>/`
- canonical tracker is not changed automatically
- runner records `model_output_executed: false`
- runner records `live_actions_performed: false`
- runner records `external_api_calls: false`
- runner records approval blockers
- runner exits safely if Gemma/Ollama is missing

## Runner Blockers

Block if implementation:

- fetches URLs
- reads browser state
- writes social/email/store content to live systems
- runs external tools
- uses Docker/CUA
- imports third-party packages not already in stdlib
- edits repo files based on model output
- silently appends to tracker
- omits approval gates

## Safety Verdict

A Gemma video-to-money runner is safe to implement next only as a local artifact generator. It should convert text into draft opportunities and candidate experiments, then stop. The human operator decides what becomes public, commercial, or tracked.
