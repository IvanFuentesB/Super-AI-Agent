# Codex N+3.33 N+3.18 Dirty Diff Audit

Status: codex_audit_only / dirty_recovery_map / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 384a5fe
Origin HEAD: 384a5fe
Local/origin sync: synced at audit start

## Scope

This audit inspected the dirty N+3.18 partial implementation. Codex did not edit, format, stage, commit, revert, or clean the dirty runtime/script/schema files.

## Repo Truth

Current branch:

```text
feat/ghoti-visible-operator-stack
```

Current HEAD:

```text
384a5fe docs(ghoti): plan N+3.32 manual queue read view
```

Tracked dirty diff summary:

```text
01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py       284 insertions
03_scripts/money_workflow_new_experiment.py                            122 changed lines
14_context/money_workflows/experiment_tracker.schema.json               51 insertions
14_context/ghoti_external_repo_tool_intake.md                            unrelated small change
21_repos/third_party/.gitkeep                                           unrelated deletion
```

Untracked recurring local dirt includes `.claude/skills/`, local brain logs, CV docs, `output/`, prompt scratch files, `01_projects/mcp_server/test.txt`, and `14_context/money_workflows/sample_video_notes_n3_18.md`.

## Dirty File: local_brain_router.py

Path:

```text
01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
```

### What Changed

The dirty diff adds a `video_to_money` local brain task:

- new `_VIDEO_MONEY_ALLOWED_EXT = {".md", ".txt"}`
- new `_MONEY_RUNS_ROOT = 05_logs/money_runs`
- new `_VIDEO_TO_MONEY_PROMPT_TEMPLATE`
- new `_parse_sections(response_text)`
- new `_candidates_to_jsonl(candidates_text, run_id)`
- new `run_video_to_money(policy, input_arg, max_chars)`
- new `main()` dispatch for `--task video_to_money`
- new help text line for the task

The route writes these intended artifacts under `05_logs/money_runs/<run_id>/`:

- `request.json`
- `source_excerpt.md`
- `source_summary.md`
- `product_ideas.md`
- `content_angles.md`
- `experiment_candidates.jsonl`
- `distribution_plan.md`
- `risk_review.md`
- `run_summary.json`

### Intended Behavior

The change appears intended to let local Gemma/Ollama transform local video notes or transcript notes into:

- source summary
- product ideas
- content angles
- experiment candidates
- distribution plan
- risk review

It is artifact-only and includes safety flags such as no external calls, no auto-post, no auto-sell, no auto-email, no auto-commit from model output, and approval required for any use.

### Coherence

Mostly coherent and bounded.

Positive signs:

- uses existing `_resolve_input_path()` for repo-root-only path checks
- uses existing `_read_excerpt()` max-char behavior
- further restricts `video_to_money` input to `.md` and `.txt`
- writes local artifacts only
- returns nonzero on missing input, bad extension, read error, and model call failure
- records safety flags in `request.json` and `run_summary.json`

Risks and gaps:

- `23_configs/local_brain_router_policy.example.json` does not yet list `video_to_money` under `local_task_classes`
- `05_logs/money_runs/` is not reflected in the policy's output directory guidance
- `_parse_sections()` depends on exact `## ` headings from the model
- `_candidates_to_jsonl()` depends on blank lines to separate candidates; the prompt does not clearly force a blank line between candidates
- candidate parsing can overwrite repeated keys if multiple candidates are emitted without blank separators
- model line `approval_required: true` may become a string value and override the hardcoded boolean `True`
- `experiment_candidates.jsonl` records are candidate artifacts, not schema-compatible experiment tracker records
- no smoke artifact path was observed in tracked files
- no N+3.18 implementation docs/state updates were observed in tracked files

### Safety Risk

The design is low-risk if kept artifact-only. It does not post, sell, email, scrape, pay, or use live accounts.

Main safety risk is interpretation risk: downstream tools or humans could treat generated product ideas or experiment candidates as validated business instructions. The run summary says approval is required, which is good, but Claude should keep that boundary visible in the final docs and state updates.

### Dependencies

Depends on:

- local Ollama provider command from policy, default `ollama`
- local model `gemma3:4b`
- existing local path resolver and excerpt reader
- local input file `.md` or `.txt`

Missing or incomplete:

- policy example does not include `video_to_money`
- no wait/resume seed or current-state update
- no committed smoke run evidence
- no final docs explaining artifact semantics

### Finishability

Finishable by Claude. The work is bounded to one existing router file plus docs/state/log validation, with parser hardening likely needed.

## Dirty File: money_workflow_new_experiment.py

Path:

```text
03_scripts/money_workflow_new_experiment.py
```

### What Changed

The dirty diff adds experiment scoring:

- ten `_SCORING_KEYS`
- `_HIGHER_IS_BETTER`
- `_LOWER_IS_BETTER`
- `_SCORE_ARG_MAP`
- score args parsing
- `_compute_scoring(parsed)`
- scoring attached to generated experiment record
- expanded help text
- dry-run scoring summary output

Scoring fields:

- `speed_to_ship`
- `pain_intensity`
- `buyer_access`
- `distribution_leverage`
- `proof_difficulty`
- `build_complexity`
- `legal_tos_risk_score`
- `monetization_clarity`
- `content_volume_potential`
- `email_list_potential`

### Intended Behavior

If no scoring args are supplied, existing behavior continues.

If any scoring arg is supplied, all ten are required. Each must be an integer 1-5. Lower-is-better fields are inverted with `6 - raw`.

Priority buckets:

- `A` for `total_score >= 40`
- `B` for `total_score >= 32`
- `C` for `total_score >= 24`
- `D` otherwise

### Coherence

Coherent and close to finishable.

Positive signs:

- all-ten-or-none rule is implemented
- 1-5 validation is implemented
- lower-is-better inversion is implemented for proof difficulty, build complexity, and legal/TOS risk
- dry-run prints score and bucket
- scoring is optional and does not break unscored records

Risks and gaps:

- parser still silently ignores unknown args, which may hide typos
- no dry-run smoke output was recorded in tracked docs
- no tests or validation docs were committed
- schema inner `raw_scores` and `adjusted_scores` do not require all ten keys even though script does

### Safety Risk

Low safety risk. The helper remains local and does not post, sell, email, scrape, or call external APIs.

Main risk is false precision: scoring can look authoritative even with no market data. Claude should document that scores are planning heuristics only.

### Dependencies

Depends on:

- existing `experiment_tracker.jsonl`
- schema update if scoring is committed

Missing or incomplete:

- dry-run validation evidence
- JSONL parse check for existing tracker
- state docs and finish-line log update

### Finishability

Finishable by Claude. It appears bounded and mostly implemented.

## Dirty File: experiment_tracker.schema.json

Path:

```text
14_context/money_workflows/experiment_tracker.schema.json
```

### What Changed

Adds optional `scoring` object with:

- `raw_scores`
- `adjusted_scores`
- `total_score`
- `priority_bucket`

### Intended Behavior

Schema describes the scoring shape produced by `money_workflow_new_experiment.py`.

### Coherence

Mostly coherent, with one schema strictness gap:

- the `scoring` object requires `raw_scores`, `adjusted_scores`, `total_score`, and `priority_bucket`
- however, `raw_scores` and `adjusted_scores` do not require all ten inner score keys
- `adjusted_scores` does not constrain min/max

This is not necessarily a blocker if the script is the sole writer, but Claude should decide whether the schema should enforce the all-ten rule.

### Safety Risk

Low. This is local schema only.

### Dependencies

Depends on the scoring shape in `money_workflow_new_experiment.py`.

### Finishability

Finishable by Claude. Likely needs either inner `required` lists or a documented reason for keeping schema flexible.

## Dirty File: sample_video_notes_n3_18.md

Path:

```text
14_context/money_workflows/sample_video_notes_n3_18.md
```

### What Changed

This file is untracked, so `git diff -- <path>` does not show content. Codex read it directly.

It contains fictional local sample notes for the `video_to_money` smoke:

- explicitly says not scraped from YouTube
- says not real business advice
- covers a video-to-business-system extractor concept
- includes AI operator prompt pack product idea
- includes email list angle
- includes content angles
- includes distribution notes
- includes risk notes

### Intended Behavior

Safe local smoke input for:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task video_to_money --input 14_context/money_workflows/sample_video_notes_n3_18.md --max-chars 12000
```

### Coherence

Coherent and safe as sample input. It avoids scraped content and live business claims.

### Safety Risk

Low. It is local fictional test input.

### Dependencies

Depends on `video_to_money` accepting `.md` input.

### Finishability

Finishable. Claude should decide whether to stage this sample file as part of N+3.18 or keep it local-only.

## Additional Dirty Files Not Part Of N+3.18

Observed but intentionally not audited deeply:

- `14_context/ghoti_external_repo_tool_intake.md`
- `21_repos/third_party/.gitkeep`
- `.claude/skills/`
- `05_logs/local_brain_runs/`
- CV docs
- `output/`
- prompt scratch files
- `01_projects/mcp_server/test.txt`

These should remain unstaged unless the operator explicitly scopes them.

## What Could Not Be Verified In This Codex Pass

Codex did not run:

- `py_compile`
- JSON schema validation
- JSONL validation
- `video_to_money` smoke
- Ollama/Gemma generation
- dry-run scoring smoke

Reason: this milestone is docs/audit only, and final validation requested only doc diff checks unless Codex accidentally changed code.

## Overall Audit Verdict

The N+3.18 dirty implementation appears coherent, bounded, and finishable. It is not ready to commit because smokes, parser hardening decisions, policy/config updates, implementation docs, wait/resume/state updates, staging review, and final validation are still missing.
