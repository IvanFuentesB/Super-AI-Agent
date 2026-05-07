# External Operator Implementation Plan

Date: 2026-04-26
Branch: feat/ghoti-visible-operator-stack
Status label: implementation_plan_created / not_runtime_wired

## Goal

Plan the safest path from Ghoti's current supervised console toward external operator capabilities without blindly cloning, installing, or wiring external tools.

## Core Principle

Ghoti should own the safety contract. External tools can become adapters only after they fit Ghoti's approval, audit, and local-control model.

## Recommended Implementation Order

### Phase 1 — Native Ghoti Operator Contract

Build this before integrating any external operator candidate.

Deliverables:

- `ActionIntent` schema with action type, target, payload hash, risk level, source observation, and expiry.
- `CapabilityAdapter` interface for future browser, desktop, repo, content, inventory, and research adapters.
- Approval creation path that binds approval to action type + payload hash.
- Approval consumption path that rejects replay, mismatched payloads, expired approvals, and wrong adapter IDs.
- Audit trace entry for every observation, proposal, approval, rejection, consumption, adapter call, and result.
- Dashboard panel showing adapter statuses as `not_installed`, `research_only`, `available`, `disabled`, or `blocked`.

Boundaries:

- No autonomous execution.
- No silent writes.
- No external account use.
- No broad filesystem access.
- No runtime dependency on RUFLO, Auto Browser, Obscura, Browser Use, Apify, OpenMontage, or InvenTree.

### Phase 2 — Browser Adapter Design, No External Tool Yet

Design a local browser adapter contract around Ghoti's existing dashboard and Active Mode lessons.

Deliverables:

- Browser action taxonomy: `observe_page`, `open_url`, `click`, `type`, `submit`, `download`, `upload`, `save_auth_profile`, `reuse_auth_profile`.
- Per-action risk classes.
- Required approvals:
  - read-only page observation can be low risk.
  - navigation/click/type/submit require explicit approval.
  - login/auth profile save/reuse require high-risk approval.
  - upload/download/payment/outreach/posting are blocked unless explicitly unlocked by a later milestone.
- Audit fields for URL, origin, selector/target description, payload hash, screenshot/frame reference, and operator ID.

### Phase 3 — Auto Browser Isolated Evaluation

Only after explicit approval:

- Clone `LvcidPsyche/auto-browser` into an isolated evaluation folder.
- Do not run Docker Compose first.
- Inspect Dockerfiles, compose files, `.env.example`, controller routes, MCP tool definitions, auth profile storage, audit logging, and approval enforcement.
- Run static/source review before any service start.
- If service start is approved, bind to localhost only and use a disposable browser session.
- Do not save real credentials in auth profiles during the first smoke test.

Decision gate:

- If Auto Browser's approval/audit/session model is strong, build a Ghoti adapter prototype around its REST API or MCP profile.
- If it is too broad, borrow design patterns only.

### Phase 4 — RUFLO Remains Architecture Reference

RUFLO should not be installed or wired until:

- Security issue history is source-audited.
- Install scripts and package lifecycle scripts are reviewed.
- MCP tool descriptions are inspected for prompt injection.
- Windows behavior is tested in isolation.
- API key/provider handling is understood.
- Uninstall/cleanup path is proven.

Near-term use:

- Extract architecture ideas: role-scoped agents, memory namespaces, coordinator/reviewer/coder separation, anti-drift checkpoints.
- Do not run it as an operator.

### Phase 5 — Obscura Research Only

Obscura should not be part of Ghoti's first operator implementation.

Possible future use:

- Local CDP-compatible browser primitive for authorized testing only.
- Rust performance reference.

Blocking concerns:

- Stealth/anti-detect positioning.
- Scraping-at-scale workflows.
- No observed approval model.
- Legal/TOS risk.

### Phase 6 — Adjacent Workflow Apps

These belong outside the core operator runtime:

- InvenTree: project inventory/hardware/assets app candidate.
- OpenMontage: content pipeline/reference, AGPL and media-rights caution.
- Apify: legal/TOS-aware public research only.
- Browser Use: browser-agent reference, not first adapter due cloud/stealth/CAPTCHA positioning.

## Adapter Status Model

Use these statuses in future dashboard docs/UI:

| Status | Meaning |
|---|---|
| `not_evaluated` | Mentioned but not reviewed |
| `research_only` | Read-only evaluation exists; no clone/install |
| `approved_for_isolated_clone` | Operator explicitly approved clone into evaluation folder |
| `source_audited` | Static source/dependency review completed |
| `available_disabled` | Adapter exists but default-disabled |
| `blocked` | Safety/license/TOS risk too high |
| `runtime_wired` | Proven adapter exists and is documented |

No candidate in N+2.9 is `runtime_wired`.

## First Coding Slice Recommendation

Do not start with Auto Browser integration. Start with Ghoti's adapter contract.

Single best next coding milestone:

> Add a supervised `operator_action_intents.json` state file and CLI/dashboard read model for proposed actions, with action-bound approval creation and replay-safe consumption. No adapter execution yet.

Why:

- It advances core Ghoti safety regardless of which external tool wins.
- It makes future browser/desktop/content/inventory adapters safer.
- It avoids being trapped by any one external repo's safety model.

## Non-Negotiable Safety Rules

- Observations never authorize actions.
- External tool availability never authorizes actions.
- Model output never authorizes actions.
- Every write/external action requires action-bound, payload-bound approval.
- No autonomous posting, outreach, purchases, payments, trades, legal/tax filings, scraping abuse, cap bypass, fake engagement, or stealth workflows.
- No browser credential reuse without explicit high-risk approval.
- No runtime integration without logs, rollback, and dashboard visibility.

## Current Status

- Plan status: `implementation_plan_created / not_runtime_wired`
- Repos cloned: NO
- Tools installed: NO
- Runtime wired: NO
- External services connected: NO
