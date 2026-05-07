# Codex N+3.34 Compact Memory Contract

Status: codex_planning_only / compact_memory_contract / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack

## Purpose

Specify the compact memory layer used in prompts and handoffs. Compact memory is a compressed pointer layer, not an excuse to delete original durable records.

Existing truth: `14_context/compact_memory/` already exists with older compact handoff files. N+3.34 proposes a clearer next-generation contract and file set. Future implementation should merge carefully, not overwrite.

## Intended Folder

```text
14_context/compact_memory/
```

## Strict Rule

Compact memory is a compressed pointer layer.

It must never replace or delete:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- milestone docs
- schemas
- logs
- runtime data
- money workflow trackers
- Obsidian vault notes

If compact memory conflicts with durable source records, the durable source wins until reviewed.

## Proposed Compact Files

```text
14_context/compact_memory/project_state.md
14_context/compact_memory/repo_and_tool_index.md
14_context/compact_memory/money_os_memory.md
14_context/compact_memory/agent_routing_memory.md
14_context/compact_memory/safety_rules.md
14_context/compact_memory/dirty_state_warning.md
```

## Shared Metadata Header

Every compact memory file should start with:

```markdown
---
memory_type: compact_pointer
status: draft|reviewed|stale
last_updated: YYYY-MM-DD
source_files:
  - path/to/source.md
generated_by: human|gemma|claude|codex|mixed
reviewed_by: human|claude|codex|none
review_required_before_canonical_use: true
---
```

## project_state.md

Target size:

- 400 to 700 words

Source of truth:

- `14_context/current_state.md`
- latest milestone docs
- `14_context/codex_n3_33_claude_resume_pack.md`

Compression rules:

- include latest pushed HEAD
- include actual working capabilities
- include major blocked areas
- include current dirty-state headline
- avoid historical milestone detail unless needed for current action

Stale data handling:

- mark `status: stale` if latest commit or dirty-state warning differs from `git status`

Allowed Gemma role:

- draft a compressed summary from source docs

Required review:

- Codex or Claude review before use in implementation prompts
- human review if it changes safety or money-facing truth

Use in future Claude prompts:

- paste only the compact summary plus source file paths
- do not paste full `current_state.md` unless Claude explicitly needs it

## repo_and_tool_index.md

Target size:

- 300 to 600 words

Source of truth:

- `14_context/obsidian_vault/04_Tools.md`
- `14_context/tooling_intake_priority_n3_17.md`
- Paperclip/OpenClaw/n8n/CUA docs
- Docker/Ollama/Gemma verification docs

Compression rules:

- list tool status as `installed`, `cloned`, `planning_only`, `not_wired`, `blocked`, or `unknown`
- include repo paths for local clones
- include "do not install/run" gates

Stale data handling:

- mark stale if any install/run/clone status changed

Allowed Gemma role:

- summarize local tool docs only

Required review:

- Codex review before tool truth is used in prompts
- human approval before any install/run/pull/action

Use in future Claude prompts:

- cite this file for tool status instead of repeating every tool audit

## money_os_memory.md

Target size:

- 500 to 900 words

Source of truth:

- `14_context/money_workflows/money_os_index.md`
- `14_context/money_workflows/experiment_tracker.jsonl`
- N+3.15 through N+3.33 Money OS docs

Compression rules:

- include numbers-game principle
- include current money workflow files
- include no-live-action rules
- include next implementation dependency on N+3.18
- do not include unverified revenue or fake proof

Stale data handling:

- mark stale if experiment tracker changes or N+3.18 is resolved

Allowed Gemma role:

- draft summaries, product idea clusters, and risk labels from local files

Required review:

- human or Codex review before use in money-facing prompts
- human approval before any public action

Use in future Claude prompts:

- provide as context for money workflow implementation instead of many milestone docs

## agent_routing_memory.md

Target size:

- 300 to 600 words

Source of truth:

- `14_context/agent_registry/agent_routing_policy_n3_14.md`
- `14_context/n3_14_api_saving_agent_routing_summary.md`
- `14_context/api_saving_memory_workflow_n3_17.md`
- `23_configs/local_brain_router_policy.example.json`

Compression rules:

- state which agent/model handles which class of task
- clearly label future candidates as not wired
- include "not cap bypass" note

Stale data handling:

- mark stale if local brain policy, worker registry, or model availability changes

Allowed Gemma role:

- draft low-risk routing summary

Required review:

- Codex/Claude review before implementing routing
- human review before autonomous routing is enabled

Use in future Claude prompts:

- paste as routing context so Claude knows what to implement vs leave to Gemma/Codex/ChatGPT

## safety_rules.md

Target size:

- 400 to 800 words

Source of truth:

- `14_context/decisions.md`
- `14_context/obsidian_vault/05_Safety_Gates.md`
- latest safety gate docs
- current user prompt constraints

Compression rules:

- include absolute no-go rules
- include approval gates
- include model-output execution ban
- include dirty-file staging warnings
- include "no secrets" rule

Stale data handling:

- mark stale if operator changes approval policy or safety boundaries

Allowed Gemma role:

- draft from reviewed safety sources only

Required review:

- human review before canonical use

Use in future Claude prompts:

- include this compact file in every implementation prompt touching runtime, dashboard, money workflows, tools, accounts, or automation

## dirty_state_warning.md

Target size:

- 200 to 400 words

Source of truth:

- `git status --short`
- `14_context/codex_n3_33_n3_18_dirty_diff_audit.md`
- `14_context/codex_n3_33_claude_resume_pack.md`

Compression rules:

- list dirty files by class
- name files not to stage
- state exact next recovery action
- do not paste full diffs

Stale data handling:

- always stale after a commit, rebase, stash, reset, or changed `git status`

Allowed Gemma role:

- draft from pasted `git status` and audit docs

Required review:

- human/Codex review before staging guidance is trusted

Use in future Claude prompts:

- always include before asking Claude to stage/commit while dirty N+3.18 files exist

## Promotion Workflow

1. Generate draft compact memory with Gemma or human.
2. Include metadata header with source files.
3. Review against durable sources.
4. Promote by replacing or appending with timestamp.
5. Never delete source documents.

## Verdict

Compact memory should make prompts smaller and sharper. It must remain humble: links, summaries, warnings, and pointers, not a new source of truth.
