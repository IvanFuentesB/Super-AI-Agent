# Codex N+3.19 Future Money OS Roadmap

Status: codex_planning_only / money_os_roadmap / approval_gated

## Core Principle

Ghoti's money workflow should be a numbers-game operating system:

- many shots
- many products
- many content pieces
- many distribution attempts
- fast review
- fast iteration
- explicit human approval for public/money-facing actions

## Recommended Sequence

### N+3.18 - Finish Gemma Video-to-Money + Scoring

Finish the dirty Claude implementation:

- local notes/transcript input.
- Gemma artifact generation.
- product ideas.
- content angles.
- distribution plan.
- risk review.
- experiment candidates.
- scoring dry-run.
- no live actions.

### N+3.19 - Money Dashboard Read View + Shot Counter

Add:

- `GET /api/ghoti/money/summary`.
- Money OS dashboard card.
- total shot counter.
- workflow type counts.
- status counts.
- score bucket counts.
- latest experiments.
- distribution channel visibility.
- approval-required count.

Read-only only.

### N+3.20 - Gemma Weekly Review Artifact Generator

Use Gemma for a local weekly review:

- summarize tracker.
- identify top shots.
- identify stale shots.
- suggest next drafts.
- generate weekly plan artifact.
- no posting/selling/outreach.

### N+3.21 - Content Batch Planner Templates

Create read/write templates for content batches:

- hooks.
- scripts.
- repurposing plan.
- CTA options.
- email-list angle.
- approval checklist.

Still no live posting.

### N+3.22 - Digital Product / Whop Draft Pipeline

Draft:

- product cards.
- offer pages.
- lead magnet outlines.
- Whop/Gumroad listing drafts.
- pricing hypotheses.

No store upload or account action without approval.

### N+3.23 - Simple Phone Game Shot Pipeline

Plan:

- game idea cards.
- mechanics.
- prototype scope.
- monetization review.
- Unity-MCP evaluation only if explicitly approved.

No Unity install, app-store action, ads, IAP, or account work without approval.

### N+3.24 - Paperclip Control Plane Evaluation

Paperclip can be evaluated as a future zero-human-company/control-plane candidate:

- worker registry.
- task ownership.
- budgets.
- statuses.
- handoffs.

No production install or runtime wiring until approved and audited.

### N+3.25 - n8n Rails / OpenClaw Worker Layer Planning

Evaluate:

- n8n as deterministic workflow rails.
- OpenClaw as future worker/channel layer.
- approval inbox.
- webhook intake.
- local scheduled summaries.

No live account workflows until explicitly approved.

## Gemma Free-Task Usage

Gemma/Ollama should handle:

- local note summaries.
- context compression.
- transcript summaries from user-provided files.
- product outline drafts.
- content angle drafts.
- risk label first pass.
- weekly tracker summaries.
- checklist generation.

Gemma should not handle alone:

- multi-file implementation.
- Git commits/pushes.
- installs.
- live accounts.
- posting.
- selling.
- outreach.
- legal/tax/financial claims.
- browser/CUA actions.

## Agent Routing

- Gemma: cheap local drafting.
- Claude Code: implementation, validation, commit/push.
- Codex: independent audits, specs, safety review.
- ChatGPT: strategy, prompt creation, architecture, prioritization.

## External Tool Status

- Paperclip: future control-plane candidate, not live.
- n8n: future workflow rails, not live.
- OpenClaw: future worker/channel layer, not live.
- Unity-MCP: future phone-game lane, not live.
- Mythos: audit-only verification concept; no leaked code clone/copy/install/use.

## Exposure And Distribution

Every experiment should include:

- at least three distribution channels.
- one email-list angle.
- one CTA.
- one validation metric.
- one approval status.

Exposure matters because the product with no distribution does not get feedback. The dashboard should make distribution gaps visible before Ghoti ever touches a public platform.

## Approval Truth

Public/live actions require explicit human approval:

- post.
- sell.
- email.
- outreach.
- account.
- payment.
- app-store.
- scraping.
- external API.
- paid tool.

Until then, money workflow artifacts remain drafts and planning objects only.
