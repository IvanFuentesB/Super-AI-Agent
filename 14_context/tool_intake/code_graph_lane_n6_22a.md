# Code Graph lane (N+6.22A)

Static, planning-only. Concept lane for a **dynamic code graph / code-intelligence**
layer (operator names: CodeGraph / Git Nexus / dynamic code graph).

## Status

- Tier: 1.
- Source: **source_needed** - several distinct projects use "CodeGraph"; the operator
  must pick the exact one. No URL guessed.
- Gate: `tier1_static_inspect` once the source is confirmed.

## What the lane would deliver

A local, read-only index that turns the repo into a queryable graph:

- Nodes: files, modules, scripts, milestones, docs, tests.
- Edges: imports/calls, "depends on", "supersedes", "audited by", "merged in".
- Queries: "what calls X", "what does milestone N touch", "what is pending vs merged".

## Principles (if/when built)

- Local and offline. No external service, no external database that leaves the machine.
- Generated and read-only; rebuildable from committed files; executes nothing.
- This overlaps the **GBrain memory upgrade** plan (a file-based memory graph). The
  code graph is the code-structure half; GBrain is the notes/status half.

## Why it matters

A code graph is the "coding brain" substrate: it lets agents reason about the codebase
cheaply (token-efficiently) instead of re-reading everything. It stays a planning lane
until the operator confirms the exact upstream tool to learn from.
