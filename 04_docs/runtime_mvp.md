# Runtime MVP

## Why This MVP Exists

This MVP moves the repo from documentation-only setup into a small real runtime that can be executed and checked locally.

## What It Proves

- local task creation works
- approval-aware task states can be persisted
- durable handoff files can be turned into a snapshot artifact
- the runtime can be validated with a repeatable checker
- council, workflow, report, truth-plan, and publishability scaffolding can be exercised locally

## Current Boundaries

- file-backed JSON only
- standard library only
- no live provider integrations
- no real browser or app execution
- no remote auth layer
- no real external execution

## Long-Term Relation

This is the smallest inspectable base for a future execution-first control system, not the full long-term system.

## Why It Is Intentionally Small

Small scope keeps the behavior readable, testable, and reversible before deeper integration, routing, and security layers are added.

## What Should Come After This MVP

- add a real provider adapter layer
- deepen approval and access control
- research browser and app execution safely
- add publishability hardening
- add integrations later
