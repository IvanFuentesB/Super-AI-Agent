# Runtime MVP

## Why This MVP Exists

This MVP moves the repo from documentation-only setup into a small real runtime that can be executed and checked locally.

## What It Proves

- local task creation works
- approval-aware task states can be persisted
- durable handoff files can be turned into a snapshot artifact
- the runtime can be validated with a repeatable checker

## Current Boundaries

- file-backed JSON only
- standard library only
- no worker loop
- no integrations
- no model execution

## Long-Term Relation

This is the smallest inspectable base for a future agent runtime, not the full long-term system.

## Why It Is Intentionally Small

Small scope keeps the behavior readable, testable, and reversible before more automation or routing layers are added.

## What Should Come After This MVP

- deepen approval workflow
- decide queue semantics
- add wait and resume behavior
- evaluate model routing later
- add integrations later
