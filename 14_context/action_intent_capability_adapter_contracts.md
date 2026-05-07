# Ghoti ActionIntent + CapabilityAdapter Contracts

**Status:** contract_created / approval_gated / not_external_adapter_wired
**Milestone:** N+3.1 Native ActionIntent + CapabilityAdapter Contracts
**Date:** 2026-04-26

## What Is Real

- `ActionIntent` records now exist in runtime code as explicit proposed-action state.
- Each intent stores an `action_type`, `adapter_id`, `target`, compact payload, payload hash, risk level, approval id, approval status, consume status, and result status.
- Capability adapters now have a local descriptor model with honest `can_execute: false` status for all adapters in this milestone.
- Creating a non-blocked intent creates a pending approval inbox item.
- Consuming an intent requires the approval item to be approved and the adapter id, action type, and payload hash to match.
- Consumption writes an audit event and records that no execution happened.
- Replay consumption is rejected after the first successful consume.
- Risky action classes are blocked before approval creation.

## What Is Not Real Yet

- No external adapter executes.
- No RUFLO, AutoBrowser, Obscura, Browser Use, or OpenClaw runtime integration exists.
- No browser click, typing, posting, purchase, trade, filing, install, clone, or shell execution is authorized by an observation or intent.
- No autonomous action path exists.

## Runtime State

Runtime state is intentionally stored under ignored runtime files:

- `01_projects/runtime_mvp/runtime_data/action_intents.json`
- `01_projects/runtime_mvp/runtime_data/action_intent_audit.json`

These files are local state and should not be committed.

Approval records continue to use the existing supervised approval inbox:

- `14_context/compact_memory/approval_inbox.json`

## CLI Contract

New CLI commands emit the same supervised JSON envelope used by the existing dashboard pipeline:

- `python -m super_ai_agent.cli ghoti-action-intents`
- `python -m super_ai_agent.cli ghoti-capability-adapters`
- `python -m super_ai_agent.cli ghoti-action-intent-create --action-type <type> --payload-json <object>`
- `python -m super_ai_agent.cli ghoti-action-intent-consume <intent_id> --adapter-id <adapter> --action-type <type> --payload-json <object>`

Every command is read-only or state-transition-only. None executes an adapter.

## Dashboard Read Model

The dashboard backend exposes:

- `GET /api/ghoti/action-intents`

This route reads the CLI JSON contract and returns a dashboard-safe read model containing summary counts, recent intents, adapter descriptors, audit events, and honest status flags.

## Safety Guarantees

- Approval-bound: an intent cannot be consumed unless the linked approval inbox item is approved.
- Payload-bound: consume requires the exact payload hash that was approved.
- Adapter-bound: consume requires the exact adapter id from the intent.
- Action-bound: consume requires the exact action type from the intent.
- Replay-safe: a consumed intent cannot be consumed again.
- Execution-safe: this milestone records consumption only; it does not execute adapters.

## Blocked Categories

The contract blocks known risky categories including:

- External posting/outreach.
- Purchases, payments, trades, and investment execution.
- Legal or tax filings.
- Cap bypass, quota evasion, fake engagement, fake accounts, and phone-farm automation.
- Stealth scraping and unrestricted filesystem access.
- Third-party clone/install actions unless a future milestone explicitly approves them.

## Next Step

Build one tiny local-only `CapabilityAdapter` implementation that can consume an approved `ActionIntent` and produce a harmless artifact, such as a repo-local read-only summary. Keep external adapters disabled until the local adapter path proves the approval-bound contract end to end.
