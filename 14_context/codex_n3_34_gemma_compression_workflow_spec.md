# Codex N+3.34 Gemma Compression Workflow Spec

Status: codex_planning_only / gemma_compression_workflow / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack

## Purpose

Define the local Gemma/Ollama workflow for compressing larger Ghoti docs into compact memory drafts. This saves paid model context by routing easy local summarization to local compute.

This workflow is not cap bypass. It is legitimate local processing of repo-local files.

## Inputs

Allowed inputs:

- larger markdown docs under `14_context/`
- compact memory source docs
- money workflow docs
- status files
- local logs that contain no secrets
- manually provided transcript/notes markdown

Disallowed inputs:

- secrets
- API keys
- credentials
- 2FA data
- customer private data
- scraped private content
- live account exports unless explicitly reviewed
- binary files
- files outside repo root

## Outputs

Output should be a compact memory draft, not an automatic canonical overwrite.

Recommended output locations:

```text
05_logs/local_brain_runs/<run_id>/response.txt
05_logs/memory_compression_drafts/<run_id>/draft.md
05_logs/memory_compression_drafts/<run_id>/run_summary.json
```

Future canonical targets, only after review:

```text
14_context/compact_memory/project_state.md
14_context/compact_memory/repo_and_tool_index.md
14_context/compact_memory/money_os_memory.md
14_context/compact_memory/agent_routing_memory.md
14_context/compact_memory/safety_rules.md
14_context/compact_memory/dirty_state_warning.md
```

## Draft Output Format

Every draft should use this metadata header:

```markdown
---
memory_type: compact_memory_draft
target_file: 14_context/compact_memory/<name>.md
source_files:
  - path/to/source.md
generated_by: gemma3:4b_via_ollama
generated_at: YYYY-MM-DDTHH:MM:SSZ
review_status: needs_human_or_codex_review
canonical_overwrite_allowed: false
unknowns_must_remain_unknown: true
model_output_executed: false
---
```

Then:

```markdown
# Draft Compact Memory: <Topic>

## Summary

## Source References

## Unknowns

## Stale-Risk Notes

## Safety Notes
```

## Proposed Commands

Existing compression route:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/current_state.md --max-chars 12000
```

Future helper concept, not implemented in this milestone:

```powershell
python 03_scripts/memory_compress_draft.py --dry-run --target 14_context/compact_memory/project_state.md --source 14_context/current_state.md --source 14_context/next_actions.md --max-chars 20000
```

Future promote command, only if explicitly approved:

```powershell
python 03_scripts/memory_compress_draft.py --promote-reviewed --draft 05_logs/memory_compression_drafts/<run_id>/draft.md
```

Promotion should fail unless the draft contains `review_status: reviewed`.

## Required Behavior

The workflow must:

- stay repo-local
- use local Ollama/Gemma only
- write artifacts only by default
- support dry-run first
- never overwrite canonical compact memory automatically
- never delete durable sources
- never execute model output
- never call web APIs
- never fetch URLs
- never post/send/sell/pay/login/scrape
- mark missing or unknown facts as `unknown`
- preserve source references
- mark stale-risk notes
- require review before canonical promotion

## Prompt Requirements

Compression prompt should instruct Gemma:

- compress, do not invent
- if the source does not say it, write `unknown`
- do not invent commit hashes
- do not invent validation results
- do not invent revenue, metrics, users, sales, or proof
- do not create action commands except as quoted source references
- do not remove safety gates
- keep dirty-state warnings visible
- include source file paths
- keep output short and structured

## Suggested Prompt Template

```text
You are compressing local Ghoti project memory.

Rules:
- Use only the provided source excerpt.
- Do not invent commit hashes, validation results, revenue, metrics, or tool status.
- If a fact is missing, write unknown.
- Preserve safety gates and dirty-state warnings.
- Do not write commands that perform live actions.
- Do not execute or instruct execution of model output.
- Return markdown only with the required metadata header and sections.

Target compact file: <target>
Source files: <sources>

SOURCE EXCERPT:
<excerpt>
```

## Stale Data Handling

A compact draft is stale if:

- source file changed after draft generation
- latest pushed HEAD changed
- dirty-state file list changed
- model/tool install status changed
- money workflow tracker changed
- operator changed safety rules

Future helper should record source mtimes and commit hash in `run_summary.json`.

## Review And Promotion

Drafts can be created by Gemma.

Canonical compact files should be promoted only by:

- human approval
- Claude implementation milestone
- Codex docs/audit milestone, if explicitly scoped

Promotion must preserve prior content through:

- append with timestamp
- backup file
- or source-controlled diff review

## Verdict

Gemma compression should turn big local docs into small reviewed memory drafts. It must never become an automatic memory rewriter or executor.
