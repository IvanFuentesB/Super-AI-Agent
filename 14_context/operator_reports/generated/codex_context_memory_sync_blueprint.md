# Ghoti Shared Agent Memory and Context Compression Blueprint

## Executive Summary

Ghoti needs one repo-local memory contract that Claude Code, Codex, Hermes, ChatGPT, local models, and a future Obsidian workspace can all read without the user repeatedly copying long histories between agents.

The proposed system keeps durable source files unchanged as the lossless truth layer. It adds small generated maps, a latest-state pointer, structured agent handoff packets, and artifact-linked run records. Generated summaries are token-budgeted and always traceable to source paths and hashes. Optional vector search may improve discovery later, but it must never become the source of truth.

This is a supervised memory system, not an autonomous self-modification loop. Ghoti may learn recursively by accumulating reviewed evidence, decisions, corrections, and reusable workflows. Model output must never directly authorize commands, live account actions, money actions, or destructive changes.

## Current Problem in Plain English

Ghoti already has valuable context spread across real repo-local structures:

- `14_context/00_main_memory/` holds stable shared memory.
- `14_context/compact_memory/` holds compact pointer-style summaries.
- `14_context/agent_handoff_vault/` provides an Obsidian-friendly handoff board.
- `14_context/obsidian_vault/` contains curated current-state, safety, routing, and tool notes.
- `14_context/bridge/outbox/` and `14_context/prompt_bus/` contain handoff and prompt artifacts.
- `14_context/multi_agent_shared_memory.json` demonstrates a small shared-memory format.
- `05_logs/` and milestone reports hold run evidence.

These pieces are useful, but agents still need a single map that says what is current, what is canonical, what is generated, and what should be read next. Without that map, each agent must scan too much history or rely on a large pasted prompt. This wastes tokens, consumes paid credits, creates stale summaries, and makes handoffs fragile.

The solution is not to compress everything into one giant summary. The solution is a layered memory system:

1. Preserve raw truth.
2. Index it deterministically.
3. Generate small reviewed summaries with source links and hashes.
4. Exchange structured handoff packets.
5. Let each agent load only the context needed for its current task.

## Proposed Architecture

### 1. Raw Lossless Archive

Purpose: preserve durable evidence and make it discoverable without deleting or rewriting original records.

The raw layer contains immutable or append-only records such as milestone reports, reviewed decisions, run records, handoff packets, and artifact manifests. Existing durable files remain valid sources; the first implementation should index them in place rather than broadly moving or duplicating them.

Rules:

- Original source files remain authoritative.
- A compressor never deletes, overwrites, or silently replaces a raw source.
- Corrections create a new record that links to the superseded record.
- Raw records use repo-relative paths only in committed documents.
- Large, sensitive, machine-specific, or noisy local artifacts remain ignored and are represented by sanitized metadata only.

### 2. Generated Context Map

Purpose: provide a compact directory of current truth and useful source pointers.

`14_context/memory/generated/context_map.md` should be a deterministic, token-budgeted map organized by:

- current project state
- current milestone and branch
- agent roles
- safety gates
- active blockers
- recent decisions
- relevant tools and capabilities
- latest handoff packets
- source paths and hashes

It is a navigation layer, not canonical truth. Every statement must point to one or more raw or durable source files.

### 3. Latest State File

Purpose: give any agent a fast startup packet.

`14_context/memory/generated/latest_state.md` should answer:

- What is Ghoti currently capable of?
- What is explicitly disabled?
- What is the current branch/milestone?
- What was the last validated result?
- What is blocked?
- What should the next agent do?
- Which sources should be opened for deeper context?

Target size: 600 to 1,200 words, with a stricter machine-readable token budget recorded in metadata.

### 4. Agent Handoff Inbox and Outbox

Purpose: let agents exchange structured work results without the user copying full conversations.

Each agent receives an inbox and writes to an outbox:

- Claude Code: implementation packets
- Codex: audit and merge-gate packets
- Hermes: coordination, status, and memory packets
- ChatGPT: architecture and planning packets
- Local models: draft summaries and classifications that require review

Agents do not edit another agent's outbox packet. A coordinator may promote a reviewed packet into the shared latest-state and context-map outputs.

### 5. Run Records and Artifact Links

Purpose: separate short context from detailed evidence.

A run record should state what happened and link to:

- committed report
- changed files
- commands run
- test outputs or summarized test evidence
- generated artifacts
- branch and commit
- blockers
- next action

Run records should store pointers and hashes, not full terminal transcripts. No secrets, tokens, cookies, private screenshots, or browser/session dumps may enter the memory layer.

### 6. Obsidian-Compatible Folder Layout

All human-facing memory files should remain plain Markdown with stable relative links so a future Obsidian vault can open the same folder without conversion.

Obsidian is a view and editing surface, not a second source of truth. Its private workspace state, plugin caches, and machine-specific settings should remain uncommitted unless explicitly sanitized and approved.

### 7. Optional Vector Search Later

Local embeddings or vector search may later help find relevant raw files. It must remain a disposable search index:

- It may return candidate source paths.
- It may not establish truth.
- It may not overwrite source records.
- It may not authorize actions.
- Every retrieved claim must be verified against the linked source file and hash.

## Proposed Folder Structure

```text
14_context/memory/
  README.md
  raw/
    decisions/
    reports/
    run_records/
  generated/
    context_map.md
    latest_state.md
    safety_snapshot.md
  agent_handoffs/
    claude/
      inbox/
      outbox/
    codex/
      inbox/
      outbox/
    hermes/
      inbox/
      outbox/
    chatgpt/
      inbox/
      outbox/
    local_models/
      inbox/
      outbox/
  index/
    raw_index.json
    handoff_index.json
    artifact_index.json
  schemas/
    agent_handoff_packet.schema.json
    raw_index.schema.json
```

Compatibility notes:

- Existing `14_context/00_main_memory/`, `14_context/compact_memory/`, `14_context/agent_handoff_vault/`, and `14_context/obsidian_vault/` remain in place during the MVP.
- The first raw index should reference existing files in place. It should not duplicate or migrate them automatically.
- Generated files should link to existing durable records until a separately audited migration is justified.
- Generated runtime residue that is not intended as reviewed evidence should remain ignored.

## Exact Memory Rules

1. Raw files are never deleted by a compressor.
2. Generated summaries must link to raw source paths and record source SHA-256 hashes.
3. A summary that cannot identify its sources is marked unverified and cannot be promoted to latest state.
4. If generated memory conflicts with raw or reviewed durable memory, the raw/reviewed source wins until a human or auditor resolves the conflict.
5. No secrets, API keys, tokens, cookies, credentials, auth files, private memory, sensitive personal data, or browser/session data may be stored.
6. No committed document may contain local absolute private paths. Use repo-relative paths or placeholders such as `<repo>/...`.
7. ZIP files are not the primary AI memory format. Archives may be backups, but agents must use reviewable Markdown and JSON indexes.
8. A vector database is a search aid only, never the source of truth.
9. JSON is used for indexes, schemas, and machine contracts. Markdown is used for human-readable truth, decisions, and handoffs.
10. Generated files include generation time, generator identity, token/word budget, source paths, and source hashes.
11. Local-model summaries are drafts until reviewed. Gemma or another local model may compress source text but may not invent missing facts.
12. Model output never becomes a command automatically.
13. No memory packet may authorize live accounts, email sending, posting, purchases, trading, destructive actions, or uncontrolled agent launches.
14. Recursive learning means reviewed improvements to memory, prompts, tests, and workflows. It does not mean unchecked self-modification.
15. One agent owns a handoff packet while writing it. Multiple agents must not edit the same packet concurrently.

## Agent Handoff Packet Data Contract

The canonical machine contract should be JSON validated by a schema. A Markdown rendering may be generated for Obsidian and humans.

Required fields:

- `schema_version`
- `packet_id`
- `agent_name`
- `agent_role`
- `branch`
- `task`
- `files_touched`
- `commands_run`
- `tests_passed`
- `tests_failed`
- `blockers`
- `next_recommended_action`
- `generated_at`
- `source_sha256`
- `artifact_sha256`
- `safety`

Example:

```json
{
  "schema_version": "1.0",
  "packet_id": "codex-20260611-n6-42a-audit",
  "agent_name": "codex",
  "agent_role": "audit_review_verification",
  "branch": "audit/ghoti-n6-42a-context-memory-map",
  "task": "Audit the context memory map generator and source traceability.",
  "files_touched": [
    "14_context/memory/agent_handoffs/codex/outbox/codex-20260611-n6-42a-audit.json"
  ],
  "commands_run": [
    "python -m unittest discover -s 01_projects/runtime_mvp/tests -p \"test_n6_42a_*.py\" -v"
  ],
  "tests_passed": [
    "source hash verification",
    "token budget enforcement"
  ],
  "tests_failed": [],
  "blockers": [],
  "next_recommended_action": "Human reviews the audit packet before merge.",
  "generated_at": "2026-06-11T00:00:00Z",
  "source_sha256": {
    "14_context/00_main_memory/current-state.md": "<sha256>"
  },
  "artifact_sha256": {
    "14_context/memory/generated/context_map.md": "<sha256>"
  },
  "safety": {
    "contains_secrets": false,
    "live_actions_executed": false,
    "human_approval_required": true
  }
}
```

Contract behavior:

- Paths are repo-relative.
- Commands are recorded as audit evidence, not as commands to execute.
- Missing evidence is represented explicitly, never guessed.
- Hash mismatch marks the packet stale.
- Packets are append-only after review; corrections create a replacement packet linked by ID.

## Minimal MVP Plan

### N+6.42A Context Memory Map

Goal: create a deterministic, repo-local index and compact current-state map from approved existing sources.

Files to add:

- `14_context/memory/README.md`
- `14_context/memory/generated/context_map.md`
- `14_context/memory/generated/latest_state.md`
- `14_context/memory/index/raw_index.json`
- `14_context/memory/schemas/raw_index.schema.json`
- `03_scripts/context_memory/ghoti_context_memory_map.py`
- `01_projects/runtime_mvp/tests/test_n6_42a_context_memory_map.py`
- one milestone report

Files to avoid:

- secrets, auth files, `.env`, cookies, browser/session data
- Obsidian workspace state
- raw terminal transcripts
- existing durable memory files except for read-only indexing
- runtime launchers, computer-use adapters, account tools, and money-action code

Tests and checks:

- index contains only repo-relative paths
- every indexed file exists
- every source hash matches
- generated summaries include source links and hashes
- output respects configured word/token budget
- no secret-like values or absolute private paths
- deterministic output from unchanged inputs
- compressor does not delete or overwrite source files
- public security audit passes

Safety risks:

- accidentally indexing sensitive or ignored files
- presenting stale generated summaries as truth
- generating huge context files that defeat compression
- local model hallucinating unsupported state

Done criteria:

- A fresh agent can read `latest_state.md`, locate supporting truth through `context_map.md`, and verify hashes without scanning the whole repo.
- Generation is deterministic, local-only, read-only toward source records, and covered by tests.

### N+6.42B Shared Agent Handoff Inbox/Outbox

Goal: create validated handoff packets for Claude Code, Codex, Hermes, ChatGPT, and local models.

Files to add:

- `14_context/memory/agent_handoffs/<agent>/inbox/.gitkeep`
- `14_context/memory/agent_handoffs/<agent>/outbox/.gitkeep`
- `14_context/memory/index/handoff_index.json`
- `14_context/memory/schemas/agent_handoff_packet.schema.json`
- `03_scripts/context_memory/ghoti_handoff_packet.py`
- `01_projects/runtime_mvp/tests/test_n6_42b_shared_agent_handoffs.py`
- one milestone report

Files to avoid:

- full chat transcripts
- copied secrets or private user memory
- executable prompts that bypass approval
- files owned by another active agent
- live agent launchers and auto-submit code

Tests and checks:

- schema rejects missing required fields
- schema rejects absolute private paths and secret-like fields
- packet hashes validate
- inbox/outbox ownership rules are enforced
- packet creation is explicit and local-only
- no packet triggers commands or live actions
- stale and superseded packets are visibly labeled

Safety risks:

- prompt injection stored inside a handoff packet
- commands in evidence fields being treated as executable instructions
- simultaneous agents editing the same packet
- stale packets causing incorrect work

Done criteria:

- Claude can leave an implementation packet and Codex can leave an audit packet without user copy-paste.
- Hermes can select the latest reviewed packet and summarize it without executing anything.

### N+6.42C Obsidian Vault Setup

Goal: make the shared memory folder pleasant to browse in Obsidian without creating a second truth system.

Files to add:

- `14_context/memory/obsidian/START_HERE.md`
- `14_context/memory/obsidian/CURRENT_STATE.md`
- `14_context/memory/obsidian/NEXT_ACTIONS.md`
- `14_context/memory/obsidian/SAFETY_GATES.md`
- `14_context/memory/obsidian/AGENT_HANDOFFS.md`
- `03_scripts/context_memory/ghoti_obsidian_memory_view.py`
- `01_projects/runtime_mvp/tests/test_n6_42c_obsidian_memory_view.py`
- one milestone report

Files to avoid:

- private `.obsidian/workspace*.json`
- plugin caches or unreviewed third-party plugins
- local absolute paths
- duplicate canonical truth
- secrets and personal sensitive data

Tests and checks:

- all wiki-style or Markdown links resolve
- generated views identify their source files
- views are reproducible from the indexes
- Obsidian-specific files do not become canonical truth
- no private workspace state is committed

Safety risks:

- humans editing generated views as if they were canonical
- plugins leaking or syncing private data
- broken links hiding source truth

Done criteria:

- Opening `14_context/memory/` as an Obsidian vault provides a clear current-state and handoff dashboard.
- Every generated view links back to the indexed source of truth.

### N+6.43A Optional Local Embedding/Search Trial

Goal: test whether local embeddings improve source discovery without replacing deterministic indexes.

Files to add:

- `docs/GHOTI_N6_43A_LOCAL_MEMORY_SEARCH_TRIAL.md`
- `03_scripts/context_memory/ghoti_local_memory_search.py`
- `23_configs/context_memory_search.example.json`
- `01_projects/runtime_mvp/tests/test_n6_43a_local_memory_search.py`
- sanitized evaluation fixtures
- one milestone report

Files to avoid:

- committed vector database binaries
- remote embedding providers or API credentials
- private or ignored files
- live actions, account tools, and command execution
- automatic truth promotion

Tests and checks:

- search is local-only and read-only
- returned results include source path and current hash
- deleted/stale index entries are detected
- retrieval quality is measured against fixed fixtures
- disabling vector search leaves deterministic memory fully usable
- no result is labeled truth without source verification

Safety risks:

- sensitive files entering the embedding index
- stale vector entries
- plausible but irrelevant retrieval being treated as truth
- large local model or index costs

Done criteria:

- The trial demonstrates measurable retrieval improvement on sanitized fixtures.
- Removing the vector index does not lose any truth or break the base memory workflow.

## How This Reduces Copy-Paste

Today, the user often must carry milestone status, test results, blockers, and safety rules from one agent to another. The proposed system replaces that repeated manual relay with small repo-local packets:

1. The builder writes a structured implementation handoff.
2. The auditor reads the handoff, source diff, and linked evidence.
3. The auditor writes a structured audit handoff.
4. Hermes reads the latest reviewed packets and updates coordination status.
5. ChatGPT reads `latest_state.md`, the current handoff, and only the linked sources needed for planning.

The user still approves risky decisions, but no longer needs to paste the same background into every agent conversation. The files become the shared conversation boundary.

## How This Reduces Token and Credit Usage

- Agents start with a compact latest-state file instead of many full reports.
- The context map points to relevant sources so agents load only what the task needs.
- Stable safety rules and agent roles are referenced once instead of repeated in every prompt.
- Run records store evidence pointers rather than full transcripts.
- Local Gemma/Ollama may draft low-risk compression and classification from local files.
- Hashes let agents detect unchanged sources and reuse reviewed summaries.
- Token budgets prevent generated context from growing without bound.
- Deterministic indexes reduce repeated model-based repo discovery.

Paid models should spend tokens on architecture, difficult implementation, and high-value review. Local models and deterministic scripts should handle indexing, basic compression, classification, and stale-state detection.

Token reduction must never come from hiding blockers, omitting safety constraints, or replacing evidence with unsupported summaries.

## What NOT to Build Yet

- No autonomous self-modifying agent.
- No model-output-to-command loop.
- No uncontrolled recursive training or self-training on unreviewed output.
- No autonomous money-making, trading, purchasing, or payment actions.
- No automatic email, social posting, YouTube publishing, or mass messaging.
- No live account login or credential storage.
- No automatic agent swarm launch from a handoff packet.
- No background process that edits or deletes raw memory.
- No remote vector database or paid embedding dependency.
- No ZIP-only memory archive.
- No broad migration of existing context folders.
- No plugin-heavy Obsidian setup.
- No assumption that a generated summary is canonical.
- No secrets or sensitive personal-life memory in committed shared context.

Future grunt-work automation should be introduced one supervised capability at a time, with dry-run plans, approval gates, deterministic safety checks, and an auditable record.

## Final Recommendation

After N+6.40B / N+6.41A are complete, Claude Code should implement **N+6.42A Context Memory Map** first.

The first implementation should be intentionally small:

1. Read a reviewed allowlist of existing durable files from `14_context/00_main_memory/`, `14_context/compact_memory/`, `14_context/agent_handoff_vault/`, `14_context/obsidian_vault/`, and selected milestone reports.
2. Produce `raw_index.json` with repo-relative paths, SHA-256 hashes, categories, and freshness metadata.
3. Produce compact `context_map.md` and `latest_state.md` files with strict source links and token budgets.
4. Refuse ignored, sensitive, absolute-path, or secret-like inputs.
5. Never delete or overwrite a source record.
6. Add deterministic tests before connecting Hermes, Obsidian, local embeddings, or any agent launcher.

That branch creates the stable foundation for every later memory, handoff, Obsidian, local-model, and supervised multi-agent capability. It reduces copy-paste immediately while preserving the evidence and safety discipline Ghoti needs for larger future ambitions.
