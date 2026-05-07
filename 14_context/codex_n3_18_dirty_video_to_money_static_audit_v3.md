# Codex N+3.18 Dirty Video-to-Money Static Audit v3

Status: codex_static_audit_only / dirty_implementation_not_staged / no_runtime_changes

## Repo State

| Item | Truth |
| --- | --- |
| Branch | `feat/ghoti-visible-operator-stack` |
| Starting HEAD | `c5d9f58 docs/analysis milestone N+3.18 - follow up dirty video-to-money implementation audit` |
| Origin HEAD | `c5d9f58 docs/analysis milestone N+3.18 - follow up dirty video-to-money implementation audit` |
| Local/origin match | yes, `0 0` ahead/behind |
| Staged files before this doc pass | none |

## Dirty Files Observed

Interrupted Claude N+3.18 files:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `03_scripts/money_workflow_new_experiment.py`
- `14_context/money_workflows/experiment_tracker.schema.json`
- `14_context/money_workflows/sample_video_notes_n3_18.md`

Unrelated/local-only dirty files that should remain unstaged:

- `14_context/ghoti_external_repo_tool_intake.md`
- `21_repos/third_party/.gitkeep`
- `.claude/skills/`
- `01_projects/mcp_server/test.txt`
- `05_logs/local_brain_runs/*`
- `14_context/ghoti_current_prompt_N1_6.md`
- local CV `.docx` files
- `output/`

## Static Review Of `local_brain_router.py`

The dirty implementation adds a `video_to_money` task to the local brain router. Based on static inspection only, it appears to:

- Add `_VIDEO_MONEY_ALLOWED_EXT = {".md", ".txt"}`.
- Add `_MONEY_RUNS_ROOT = 05_logs/money_runs`.
- Add a structured prompt that asks Gemma to produce source summary, product ideas, content angles, experiment candidates, distribution plan, and risk review.
- Parse model output into `##` sections.
- Write artifacts under `05_logs/money_runs/<run_id>/`.
- Resolve input through the existing repo-root input resolver before reading.
- Reject input extensions outside `.md` and `.txt`.
- Record no external API usage, no model-output execution, no auto-posting, no auto-selling, no auto-email, and approval required in the run summary.

## Expected Artifact Outputs

Expected successful output folder:

`05_logs/money_runs/<run_id>/`

Expected files:

- `request.json`
- `source_excerpt.md`
- `source_summary.md`
- `product_ideas.md`
- `content_angles.md`
- `experiment_candidates.jsonl`
- `distribution_plan.md`
- `risk_review.md`
- `run_summary.json`

Required `run_summary.json` truth fields:

- `task_type: video_to_money`
- `input_file`
- `provider`
- `model`
- `api_usage: none`
- `external_calls: none`
- `model_output_executed: false`
- `auto_post: false`
- `auto_sell: false`
- `auto_email: false`
- `auto_commit_from_model: false`
- `approval_required_for_any_use: true`

## Risks And Brittle Points

- Artifact root naming differs from earlier specs that used `05_logs/money_workflow_runs/<run_id>/`; Claude should either align or document `05_logs/money_runs`.
- `source_summary.md` is clear enough, but earlier planning used names like `business_model_summary.md`. Claude should choose one convention.
- `_candidates_to_jsonl` likely depends on blank lines to separate candidates. Gemma may output all `- key:` lines continuously, producing one collapsed candidate instead of several.
- `approval_required: true` may be parsed as a string and override the default boolean true in candidate JSONL records.
- The parser assumes exact `##` headers. This is acceptable for a first smoke but should be verified against real Gemma output.
- The runner calls Ollama only after writing request/source artifacts. That is useful for recovery, but Claude should verify failed runs still produce clear failure summaries.

## Static Validation Results

Codex ran static-only validation and did not run Ollama/Gemma generation.

| Command | Result |
| --- | --- |
| AST parse `local_brain_router.py` | PASS |
| AST parse `money_workflow_new_experiment.py` | PASS |
| JSON parse `experiment_tracker.schema.json` | PASS |
| `git diff --check` | PASS with CRLF warnings only on existing dirty files |

## What Claude Must Validate

Claude must still run a real local smoke when credits/tooling allow:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task video_to_money --input 14_context/money_workflows/sample_video_notes_n3_18.md --max-chars 12000
```

Then Claude must inspect:

- Whether all expected artifacts are created.
- Whether `experiment_candidates.jsonl` has useful structured records.
- Whether `approval_required` remains boolean true.
- Whether `run_summary.json` records the correct safety truth.
- Whether no live posting, selling, outreach, scraping, account, payment, app-store, Docker, or CUA action occurred.
