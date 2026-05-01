# Codex N+3.35 N+3.18 Validation Gap Report

Status: codex_audit_only / validation_gap_report / no_code_fixes

Date: 2026-05-01
Branch: feat/ghoti-visible-operator-stack
Current HEAD: 2e81aa0

## Summary

N+3.18 has partial dirty implementation work, but the full validation chain is not proven.

Codex found static validation passes for the dirty files, but no Claude commit, no recorded Gemma smoke artifacts, no implementation docs, and no final staged/committed/pushed N+3.18 result.

## Validators Claude Appears To Have Run

No committed evidence was found that Claude ran the final N+3.18 validators.

Late in the audit, an untracked `05_logs/money_runs/vm_20260501_082950_958735/` artifact directory appeared with a PASS `video_to_money` `run_summary.json`. It was not staged by Codex and is not a substitute for a finished N+3.18 commit.

There are still no N+3.18 implementation docs recording the smoke results.

## Validators Codex Ran During This Audit

Codex ran these non-mutating or safe static checks:

```powershell
python -m py_compile 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python -m py_compile 03_scripts/money_workflow_new_experiment.py
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json > $null
python -c "import json, pathlib; p=pathlib.Path('14_context/money_workflows/experiment_tracker.jsonl'); rows=[json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()] if p.exists() else []; print(f'experiment_tracker jsonl ok: {len(rows)} rows')"
```

Observed results:

```text
local_brain_router.py: compiles
money_workflow_new_experiment.py: compiles
experiment_tracker.schema.json: parses
experiment_tracker.jsonl: parses, 3 rows
```

These checks are helpful, but they do not prove N+3.18 complete.

## Late Smoke Artifact Evidence

Observed untracked artifact directory:

```text
05_logs/money_runs/vm_20260501_082950_958735/
```

Observed files:

```text
request.json
source_excerpt.md
source_summary.md
product_ideas.md
content_angles.md
experiment_candidates.jsonl
distribution_plan.md
risk_review.md
run_summary.json
```

Observed `run_summary.json` fields:

```text
status: PASS
provider: ollama
model: gemma3:4b
exit_code: 0
api_usage: none
external_calls: none
model_output_executed: false
auto_post: false
auto_sell: false
auto_email: false
auto_commit_from_model: false
approval_required_for_any_use: true
```

Remaining caveat:

This proves one local smoke artifact exists, but Claude still needs to inspect artifact quality, decide whether artifacts should remain untracked or be committed, and document the result in N+3.18 implementation docs.

## Validation Still Missing

Claude still needs to run or record:

```powershell
git status --short
git diff --stat
git diff --check
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python 03_scripts/money_workflow_new_experiment.py --help
```

If local Gemma/Ollama remains available and the operator still approves local model smoke, Claude may either inspect the existing untracked smoke run or rerun:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task video_to_money --input 14_context/money_workflows/sample_video_notes_n3_18.md --max-chars 12000
```

Inspect latest money run:

```powershell
Get-ChildItem 05_logs/money_runs | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

Verify required artifacts:

```text
request.json
source_excerpt.md
source_summary.md
product_ideas.md
content_angles.md
experiment_candidates.jsonl
distribution_plan.md
risk_review.md
run_summary.json
```

Verify `run_summary.json` fields:

```text
status: PASS
api_usage: none
external_calls: none
model_output_executed: false
auto_post: false
auto_sell: false
auto_email: false
auto_commit_from_model: false
approval_required_for_any_use: true
```

## Scoring Dry-Run Still Needed

Run:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --source "local smoke" --product-idea "AI operator prompt pack" --target-customer "solo AI builders" --pain-point "They waste time rebuilding prompts" --offer "Prompt pack draft artifact" --next-action "Draft local product outline only" --risk-level low --channel manual_review_first --speed-to-ship 5 --pain-intensity 4 --buyer-access 3 --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 --legal-tos-risk 2 --monetization-clarity 4 --content-volume-potential 5 --email-list-potential 4
```

Expected:

- dry-run prints JSON
- no append to `experiment_tracker.jsonl`
- `scoring.raw_scores` contains all ten dimensions
- `scoring.adjusted_scores.proof_difficulty` equals `4`
- `scoring.adjusted_scores.build_complexity` equals `4`
- `scoring.adjusted_scores.legal_tos_risk_score` equals `4`
- `total_score` and `priority_bucket` are printed

Partial-score failure smoke:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --source "local smoke" --product-idea "bad partial score" --target-customer "test" --pain-point "test" --offer "test" --next-action "test" --speed-to-ship 5
```

Expected:

- exits non-zero
- reports that all 10 scoring args are required if any are provided
- does not write to tracker

Out-of-range failure smoke:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --source "local smoke" --product-idea "bad score" --target-customer "test" --pain-point "test" --offer "test" --next-action "test" --speed-to-ship 6 --pain-intensity 4 --buyer-access 3 --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 --legal-tos-risk 2 --monetization-clarity 4 --content-volume-potential 5 --email-list-potential 4
```

Expected:

- exits non-zero
- reports score must be 1-5
- does not write to tracker

## Schema Gap

`experiment_tracker.schema.json` parses and includes top-level `scoring.required`.

Remaining question:

Should `raw_scores` and `adjusted_scores` each require all ten score fields inside the schema?

Recommendation:

- If the schema is meant to fully validate records independent of the helper script, add inner `required` arrays for all ten score fields.
- If script-level validation is canonical, document that the schema is intentionally looser internally.

## Candidate Parser Gap

The current `video_to_money` parser may be brittle around model output formatting.

Risk cases:

- candidates collapse into one record if Gemma omits blank lines
- repeated keys may overwrite previous candidate fields
- generated candidate JSONL may not be directly compatible with the main tracker schema
- parser may not record parse warnings when structure is lossy

Recommended Claude fixes if smoke shows parser issues:

- split candidates on repeated `workflow_type` or `product_idea`
- force `approval_required` to boolean `true`
- write parse warnings to `run_summary.json`
- keep generated candidates as review-only draft artifacts

## Policy / State Gaps

No dirty or committed updates were found for:

```text
23_configs/local_brain_router_policy.example.json
01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py
14_context/current_state.md
14_context/next_actions.md
14_context/ghoti_finish_line_log.md
```

Claude should update these if N+3.18 is finished, or explicitly document why the milestone is paused.

## Commit Gate

Before committing N+3.18, Claude should run:

```powershell
git diff --check
git diff --cached --name-status
git diff --cached --check
```

Commit only after:

- static validation passes
- smoke tests are recorded
- parser/schema decisions are resolved
- state docs are updated or pause rationale is documented
- unrelated dirt remains unstaged

## Validation Gap Verdict

Static checks pass, and one untracked `video_to_money` PASS artifact exists. N+3.18 is still not validated enough to commit as complete. The missing items are scoring dry-run proof, parser/artifact-quality review, implementation docs, state/wait-resume updates, careful staging, commit, and push.
