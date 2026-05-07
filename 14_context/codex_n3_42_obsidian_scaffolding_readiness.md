# N+3.42 Obsidian Scaffolding Readiness

Status: Codex readiness audit only.
Date: 2026-05-05

## Verdict

N+3.34 Obsidian Vault + Compact Memory Scaffolding can safely start next after N+3.32 is pushed.

Reason:

- The Money OS local loop now has the core local artifacts: video-to-money, weekly review, weekly dashboard read card, manual queue draft intake, manual queue read view, and operator work session planner.
- The next bottleneck is memory durability and prompt compression, not another external connector.
- N+3.34 can be implemented as docs/file scaffolding and local memory hygiene without touching Money OS runtime behavior.

## Existing Memory Specs

Specs already exist:

- `14_context/codex_n3_34_obsidian_vault_structure_spec.md`
- `14_context/codex_n3_34_compact_memory_contract.md`
- `14_context/codex_n3_34_gemma_compression_workflow_spec.md`
- `14_context/codex_n3_34_memory_safety_gate_review.md`
- `14_context/codex_n3_34_claude_implementation_checklist.md`
- `14_context/codex_n3_34_next_milestone_recommendation.md`

Existing vault scaffold:

```text
14_context/obsidian_vault/
  00_Index.md
  01_Current_State.md
  04_Tools.md
  05_Safety_Gates.md
```

Existing compact memory scaffold:

```text
14_context/compact_memory/
```

This folder already has older compact files such as approval inbox, blocker state, compact build context, current loop state, manual execution queue, next exact step, plan extracts, and task summaries.

## Repo State To Feed Obsidian

N+3.34 should summarize and link to:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- N+3.18 implementation docs
- N+3.29 weekly money review docs
- N+3.30 weekly review dashboard docs
- N+3.31 manual queue intake docs
- N+3.32 manual queue read view/work session docs
- N+3.38 through N+3.41 tool, budget, connector, jobs, and agent lane backlogs
- `14_context/money_workflows/`
- `05_logs/money_reviews/` as generated artifact source, not canonical memory

## What Must Be Scaffolded

N+3.34 should create or merge toward:

```text
14_context/obsidian_vault/
  00_Index.md
  01_Current_State.md
  02_Next_Actions.md
  03_Decisions.md
  04_Tools_And_Repos.md
  05_Money_OS.md
  06_Safety_Gates.md
  07_Agent_Routing.md
  08_Dirty_State.md
  09_Migration_Handoff.md
```

And compact memory files:

```text
14_context/compact_memory/project_state.md
14_context/compact_memory/repo_and_tool_index.md
14_context/compact_memory/money_os_memory.md
14_context/compact_memory/agent_routing_memory.md
14_context/compact_memory/safety_rules.md
14_context/compact_memory/dirty_state_warning.md
```

## What Must Not Be Overwritten

N+3.34 must not overwrite without preservation:

- existing Obsidian vault notes
- existing compact memory files
- `current_state.md`
- `next_actions.md`
- `ghoti_finish_line_log.md`
- milestone docs
- JSONL trackers
- generated logs
- user notes

If a target file exists, Claude should append a dated section, create a draft file, or merge with an explicit source-reference block.

## No Data Loss Rule

Obsidian and compact memory are navigation and compression layers.

They must never delete, replace, or hide:

- durable milestone records
- original source docs
- schemas
- JSONL trackers
- logs
- tool risk registers
- safety gate docs
- dirty-state warnings

If compact memory conflicts with durable records, durable records win until reviewed.

## Compact Memory Pointer Rule

Compact memory is a compressed pointer layer, not a new source of truth.

Each compact file should include:

- metadata header
- source files
- review status
- stale data note
- unknowns marked as `unknown`
- source pointers for claims

Compact files should make future Claude/Codex/ChatGPT prompts smaller without erasing context.

## Gemma Compression Draft Role

Gemma/Ollama may draft compact summaries from repo-local source docs only.

Gemma must not:

- invent commit hashes
- invent validation results
- invent revenue, sales, or proof
- overwrite canonical memory automatically
- execute model output
- pull web data
- process secrets
- authorize public or money-facing actions

Gemma output should go to draft artifacts first, then be reviewed before canonical promotion.

## Human Promotion To Canonical Memory

Canonical vault or compact memory updates require review when they affect:

- current state
- safety rules
- money workflow truth
- dirty-state warnings
- tool install/connect status
- public/live/account action boundaries

Promotion should be explicit and diff-visible.

## Dirty-State File Needs

N+3.34 should include a visible dirty-state note:

```text
14_context/obsidian_vault/08_Dirty_State.md
14_context/compact_memory/dirty_state_warning.md
```

It should classify:

- intentional dirty local files
- generated logs
- third-party placeholders
- prompt scratch files
- files not to stage

It must not include reset/delete commands unless explicitly approved by the operator.

## Agent Lane File Needs

N+3.34 should prepare memory for future lane locks, but full lane lock implementation can follow after N+3.34.

Future folder:

```text
14_context/agent_lanes/
```

Useful notes:

- lane identity and ownership
- active lock pattern
- status beacon pattern
- pull/fetch protocol
- shared file lock list
- merge checklist

## N+3.34 Safety Scope

N+3.34 should be docs/scaffolding/local files only:

- no installs
- no connectors
- no MCP changes
- no live accounts
- no posting/emailing/selling/payments
- no scraping
- no external tool integration
- no runtime behavior changes unless explicitly approved

## Readiness Decision

Ready after N+3.32 is pushed.

Recommended next Claude target:

```text
N+3.34 Claude - Obsidian Vault + Compact Memory Scaffolding
```
