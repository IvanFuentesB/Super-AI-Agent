# Runtime MVP

## Why This MVP Exists

This MVP moves the repo from documentation-only setup into a small real runtime that can be executed and checked locally.

## What It Proves

- local task creation works
- approval-aware task states can be persisted
- durable handoff files can be turned into a snapshot artifact
- the runtime can be validated with a repeatable checker
- council, workflow, report, truth-plan, publishability, personal-ops, integration-adapter, GitHub write-action, and environment-detection scaffolding can be exercised locally

## Current Boundaries

- file-backed JSON only
- standard library only
- GitHub live read-only support exists
- GitHub write-action scaffolding now exists and is approval-gated
- remote GitHub write actions depend on `gh`
- environment detection and capability summary now exist
- `gh` path and auth remain a gating factor for remote GitHub actions
- mail and Notion are planning-only
- no real browser or app execution
- no remote auth layer
- no real external execution
- no live mail or LinkedIn adapters
- no real Notion adapter

## Long-Term Relation

This is the smallest inspectable base for a future execution-first control system, not the full long-term system.

## Why It Is Intentionally Small

Small scope keeps the behavior readable, testable, and reversible before deeper integration, routing, and security layers are added.

## What Should Come After This MVP

- add a real provider adapter layer
- deepen owned-account workflow scaffolding
- standardize tool detection and `gh` availability further
- add safe GitHub remote smoke testing once `gh` is visible and authenticated
- deepen approval and access control
- research browser and app execution safely
- add publishability hardening
- add integrations later
