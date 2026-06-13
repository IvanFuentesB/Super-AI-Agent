# Ghoti Agent OS -- Overview

**Status:** Working local MVP (supervised, deny-by-default)
**Entry point:** `03_scripts/agent_os/ghoti_agent_os.py`

---

## Summary

The Ghoti Agent OS is one local supervised command center that composes the
finished parts of this repo instead of duplicating them: the operator recipes
policy gate, compact memory plus the context pack, the Obsidian vault, agent
lanes and file locks, the prompt bus and relay pairs, the Ollama local model
probe, and a suggestion-only worker. Everything runs on this machine, every
output is a repo-local file under `14_context/agent_os/`, and no agent is ever
launched by Ghoti: handoff packets are copy-paste only and every live step is
performed by a human.

## What it composes (all existing, all verified)

| Part | Location | Role in the Agent OS |
|------|----------|----------------------|
| Operator recipes policy gate | `03_scripts/operator_recipes/ghoti_operator_recipes.py` + `23_configs/operator_recipe_policy.example.json` | Deny-by-default capability check before every workflow plan or worker suggestion |
| Compact memory | `14_context/compact_memory/` (canonical `*.md`; `generated/` is machine-owned) | Source of verified memory pointers |
| Context pack | `03_scripts/ghoti_context_pack_builder.py` -> `14_context/compact_memory/generated/ghoti_current_context_pack.json` | Single rebuildable context snapshot |
| Obsidian vault | `14_context/obsidian_vault/` (start note `00_Index.md`) | Human-readable curated memory, searched read-only |
| Agent lanes and locks | `14_context/agent_lanes/agent_lane_registry.json`, `active_locks.jsonl` | Role-to-lane mapping and file ownership truth |
| Prompt bus and relay pairs | `14_context/prompt_bus/outbox/`, `14_context/agent_relay/pairs/` | Existing copy-paste handoff channels |
| Local model probe | Ollama at `http://127.0.0.1:11434/api/tags` (read-only, never pulls) | Honest local model availability status |
| Suggestion-only worker | `03_scripts/agent_os/local_worker.py` | Writes proposals; never executes anything |

## Architecture

```
+---------------------------------------------------------------------+
|                Human operator (approves and runs everything)        |
+----------------------------------+----------------------------------+
                                   |
               +-------------------+--------------------+
               |                                        |
   +-----------v------------+              +------------v------------+
   | Dashboard "Agent OS"   |              | CLI                     |
   | http://127.0.0.1:3210  |              | 03_scripts/agent_os/    |
   | (left-nav panel)       |              |   ghoti_agent_os.py     |
   +-----------+------------+              +------------+------------+
               |                                        |
               +-------------------+--------------------+
                                   |
                  +----------------v-----------------+
                  |  Ghoti Agent OS command center   |
                  |  - workflow_templates.py (data)  |
                  |  - local_worker.py (suggestion)  |
                  +--+------+-------+-------+-----+--+
                     |      |       |       |     |
      +--------------+   +--+--+    |   +---+--+  +-----------------+
      | Policy gate  |   |Memory|   |   |Lanes |  | Local model     |
      | (deny by     |   |+pack |   |   |+locks|  | probe (Ollama,  |
      | default,     |   |+vault|   |   |      |  | read-only)      |
      | Rust+Python) |   +------+   |   +------+  +-----------------+
      +--------------+              |
                     +--------------v---------------+
                     | Repo-local outputs only:     |
                     | 14_context/agent_os/         |
                     |   workflows/ handoffs/       |
                     |   runs/ evidence/            |
                     | + prompt bus / relay pairs   |
                     |   (copy-paste channels)      |
                     +------------------------------+
```

## The three honesty labels

Every Agent OS surface labels what it really is. There are exactly three
labels, and nothing in this milestone goes beyond the second one without the
third one's explicit approval file.

| Label | Meaning | Where it applies |
|-------|---------|------------------|
| `simulation` | Visual only; nothing real happens | The agent arena visual swarm (`docs/GHOTI_N6_21A_AGENT_ARENA_VISUAL_SIMULATOR.md`); `cmd_status` reports it under `simulation_only_remaining` |
| `suggestion_only` | Reads verified local sources, writes proposed plans/handoffs into `14_context/agent_os/`; never executes a command, never opens a network connection, never edits other files | The local worker (`local_worker.py`), all 7 workflow templates, all 6 roster roles |
| `approved_local_action` | A bounded extra capability unlocked only by an explicit human approval artifact | `14_context/agent_os/APPROVED_ACTIONS.json` can extend the worker's allowed output directories; entries are repo-local only - paths outside the repo are never approvable |

The worker enforces the labels in code: `local_worker.py` contains no
`subprocess` import (a self-check fails if one appears), refuses writes
outside its allowed roots, and ASCII-sanitizes everything it writes.

## Deny-by-default policy

- Manifest: `23_configs/operator_recipe_policy.example.json`. Default
  decision is `deny`; a capability not in `allowed_capabilities` is denied,
  including unknown future capabilities.
- Rust enforcement: `rust/ghoti_policy_checker` mirrors the manifest. It
  supports `--check`, `--input <plan.json>` (capability verdicts), and now
  `--ownership-input <wave.json>` (file-ownership overlap checks across
  agent assignments).
- When a built binary exists under `rust/target/{release,debug}/`, the Agent
  OS invokes it for real; otherwise a Python mirror enforces the identical
  policy and the output says which checker ran.
- Every workflow template declares its capabilities, and the policy gate
  runs before any plan or suggestion is written. The gate fails closed: if
  the policy module cannot be imported, the decision is `deny`.

## What the Agent OS will not do

No posting, no purchases, no account access, no provider API calls, no
browser control, no computer-use, no background execution, no agent launch.
Workflows produce plans, drafts, and checklists; a human reviews them and
performs every live step manually.

## Related docs

- Quickstart: `docs/GHOTI_COMMAND_CENTER_QUICKSTART.md`
- Memory and handoffs: `docs/GHOTI_MEMORY_AND_HANDOFFS.md`
- Workflow templates: `docs/GHOTI_WORKFLOW_LAUNCHPAD.md`
- Roadmap: `docs/GHOTI_ROADMAP_TO_FULL_COMPUTER_USE.md`
