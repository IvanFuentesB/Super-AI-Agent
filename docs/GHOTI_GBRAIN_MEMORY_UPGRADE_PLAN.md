# Ghoti GBrain Memory Upgrade Plan

"GBrain" (graph brain) is the idea of a structured, queryable memory graph over the
project's notes, handoffs, and status - instead of scattered Markdown. This plan
upgrades Ghoti's local memory toward that, staying local-only and safe.

## Today's memory

- compact_memory snapshots
- status brain + status bridge (N+6.15A / N+6.16A)
- agent handoff vault
- `repo_knowledge/generated` context packs

## Target: a local, file-based graph index

- A generated, read-only index linking milestones -> reports -> handoffs -> scripts.
- A lightweight JSON/Markdown graph: nodes are milestones/docs/scripts; edges are
  "depends on", "supersedes", "audited by", "merged in".
- Answers everyday questions: "what is the latest status", "what depends on X", "what
  is pending vs merged".

## Principles

- Local and offline. No external vector database, no external API, no embeddings
  service, no secrets.
- Generated, never the source of truth; always rebuildable from committed files.
- Read-only; the memory layer executes nothing.

## Rollout behind `gbrain_memory_upgrade_enabled` (off by default)

- Phase 1: define the node/edge schema (this plan).
- Phase 2: a generator that builds the graph index from committed reports/handoffs.
- Phase 3: a status query over the index that extends the existing status brain.

No phase adds a network service, an external database, or any live action.
