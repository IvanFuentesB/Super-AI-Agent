# Codex N+3.50C - Gemma Compact Memory Worker Audit

Milestone: N+3.50C - Dashboard/Ruflo/Gemma parallel audit lane

Date: 2026-05-06

## Scope

This is a Codex audit/source-check doc only. No model pull, model run, or Gemma generation was executed by Codex. No external API calls, account actions, posting, scraping, payments, emails, or jobs were performed.

## Source-Check Summary

Primary source checked:

- Ollama CLI docs: `https://docs.ollama.com/cli`

Findings:

- Ollama documents local model commands including `ollama run gemma3`, `ollama pull gemma3`, `ollama list`/`ollama ls`, `ollama ps`, and `ollama stop`.
- `ollama pull gemma3` downloads a model and requires explicit operator approval in Ghoti.
- `ollama run gemma3` performs model inference locally, but still must be treated as model-output draft generation, not canonical truth.
- `ollama signin/signout` exists; Ghoti workers must not require account sign-in.

## Expected Claude-Owned Gemma Files To Audit

Claude N+3.50 may add:

- `03_scripts/gemma_compact_memory_worker.py`
- `14_context/tooling/gemma_compact_memory_worker_n3_50a.md`
- `23_configs/gemma_compact_memory_worker.example.json`

Audit checklist:

- Python stdlib only.
- Dry-run default.
- No model pull without explicit approval.
- No `ollama signin`.
- No external APIs.
- No live accounts.
- No shell command strings; use list-argument subprocess calls.
- Bounded inputs from approved local files only.
- Output is draft-only.
- No automatic overwrite of `14_context/compact_memory/*.md`.
- No automatic overwrite of Obsidian canonical notes.
- Output path should be under `05_logs/gemma_compact_memory_drafts/<run_id>/`.
- Include source file list and source hashes/timestamps in `run_summary.json`.
- Include unknown/missing fact markers instead of inventing data.
- Include promotion checklist before any draft becomes canonical memory.

## Allowed Local Commands For Future Claude Validation

Read-only checks:

```powershell
ollama --version
ollama list
ollama ps
```

Draft generation after model availability is confirmed and operator approves:

```powershell
ollama run gemma3 "Summarize this local markdown excerpt..."
```

Model download only after explicit approval:

```powershell
ollama pull gemma3
```

## Prohibited Gemma Worker Behavior

- no automatic model pull
- no account sign-in
- no web/API calls
- no tool execution from model output
- no canonical memory overwrite
- no generated public claims
- no live account actions
- no posting/email/payment/scraping/job/giveaway workflows
- no hidden background processes
- no deletion of source records

## Truth Handling Rules

Gemma worker output must be labeled:

```text
status: draft
source_files: [...]
review_required: true
canonical_memory_updated: false
```

If source data is absent or stale, the worker should write:

```text
unknown
not verified
source missing
```

It must not invent:

- commit hashes
- validation results
- revenue/metrics
- account/tool status
- installed model names
- safety approvals

## Safety Verdict

Verdict: SAFE TO AUDIT / CONDITIONAL SAFE TO IMPLEMENT AS DRAFT-ONLY LOCAL WORKER.

Gemma can be a major token-saving lane, but only after the implementation proves it writes local draft artifacts, never canonical truth, and never pulls/runs models without the correct approval gate.
