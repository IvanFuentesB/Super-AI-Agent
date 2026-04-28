# Codex N+3.14 n8n / OpenClaw / Paperclip Architecture Plan

Status: codex_parallel_audit / architecture_plan_only / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Architecture Overview

Ghoti should stay local-first and approval-gated while adding layers carefully:

1. Brain Router
2. Orchestration
3. Execution
4. Deterministic Workflows
5. Assistant Channels
6. Memory

## Layer 1 — Brain Router

Purpose: choose the right brain/tool before spending API credits or touching risky systems.

- Gemma local for cheap/easy text tasks.
- Claude Code for hard repo implementation.
- Codex for audits, reviews, scoped edits, and verification.
- ChatGPT for planning/architecture.

First build:

- Preview-only policy/config.
- CLI dry-run route preview.
- Worker-card suggestion.

Defer:

- automatic dispatch
- autonomous retries
- model-driven CUA/browser execution

## Layer 2 — Orchestration

Candidate: Paperclip.

Paperclip can potentially provide:

- task registry
- org chart
- worker status
- budgets/costs
- agent heartbeats
- governance/approvals
- session persistence
- Claude/Codex/OpenClaw adapters

First build in Ghoti:

- worker-card registry
- task owner/scope/status file
- small policy that says which worker can touch which files

Defer:

- Paperclip install
- Paperclip runtime
- Paperclip controlling Claude/Codex/OpenClaw
- public exposure
- broad filesystem workspaces

## Layer 3 — Execution

Current/future execution surfaces:

- current Ghoti runtime
- ActionIntent + CapabilityAdapter contracts
- JSONL audit trail
- repo executor
- CUA screenshot observe path
- later CUA click/type
- browser automation later

Rules:

- proposals before actions
- approval before external/risky/destructive actions
- payload hash for CUA/computer-use
- audit event before and after execution
- no live accounts until specific task approval

## Layer 4 — Deterministic Workflows

Candidate: n8n.

n8n should be used for boring repeatable rails after the workflow is stable:

- schedule health checks
- watch local files
- trigger local summary jobs
- notify the user
- receive local webhooks
- enqueue proposed Ghoti tasks

Rules:

- no external sends by default
- no credentials by default
- no scraping by default
- no posting/email/outreach until approved
- no paid APIs until approved
- no money/legal/tax workflows without human final action

## Layer 5 — Assistant Channels

Candidate: OpenClaw later.

OpenClaw can become:

- a personal assistant surface
- a channel/chat/mobile interface
- a worker under Paperclip or Ghoti supervision
- a skill/channel integration reference

Rules:

- local sandbox first
- no public exposure
- no broad credentials
- no live email/social/banking/calendars until reviewed
- no unattended external actions

## Layer 6 — Memory

Existing Ghoti memory should stay canonical first:

- `14_context/`
- compact vault
- wait/resume items
- run artifacts
- logs
- worker cards
- finish-line docs

Future Paperclip or n8n should read small summaries and file references rather than swallowing giant logs.

## What To Build First

1. `23_configs/brain_routing_policy.example.json`
2. `20_agents/worker_card_registry.example.json`
3. `20_agents/agent_registry.example.json`
4. Preview CLI: `brain_route_preview.py`
5. Optional dashboard read-only route later: recommended brain / worker status

## What To Defer

- Paperclip install.
- OpenClaw runtime.
- n8n runtime.
- public deployment.
- live account connections.
- CUA click/type.
- browser actions beyond approved local smoke.
- autonomous task dispatch.

## Security Model

- No public exposure by default.
- No unattended live accounts.
- No autonomous money/legal actions.
- No fake engagement or spam.
- No provider/API limit bypass.
- No broad host mounts.
- No secrets in prompts.
- No third-party runtime wiring without approval.
- Every risky action needs ActionIntent or equivalent approval record.

## Verdict

Paperclip is likely the best future control-plane candidate. n8n is likely the best deterministic workflow rails candidate. OpenClaw is likely a future channel/personal-assistant worker. Ghoti should first build a tiny native worker-card and brain-routing preview so it can evaluate those systems from a position of control rather than handing them control prematurely.
