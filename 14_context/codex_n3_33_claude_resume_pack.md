# Codex N+3.33 Claude Resume Pack

Status: codex_audit_only / claude_resume_pack / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 384a5fe

## Current Truth

Latest pushed commit:

```text
384a5fe docs(ghoti): plan N+3.32 manual queue read view
```

N+3.18 dirty implementation is still uncommitted.

Known dirty N+3.18 files:

```text
01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
03_scripts/money_workflow_new_experiment.py
14_context/money_workflows/experiment_tracker.schema.json
14_context/money_workflows/sample_video_notes_n3_18.md
```

Do not restart from scratch. Continue from these dirty files if finishing.

## Inspect First

Run:

```powershell
git status --short
git diff --stat
git diff -- 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
git diff -- 03_scripts/money_workflow_new_experiment.py
git diff -- 14_context/money_workflows/experiment_tracker.schema.json
if (Test-Path 14_context/money_workflows/sample_video_notes_n3_18.md) { Get-Content -Raw 14_context/money_workflows/sample_video_notes_n3_18.md }
```

Then read:

```text
14_context/codex_n3_33_n3_18_dirty_diff_audit.md
14_context/codex_n3_33_validation_matrix.md
23_configs/local_brain_router_policy.example.json
14_context/money_workflows/video_to_money_intake_template.md
14_context/money_workflows/experiment_tracker.jsonl
```

## If Finishing N+3.18

### Step 1: Static Validation

Run:

```powershell
python -m py_compile 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python -m py_compile 03_scripts/money_workflow_new_experiment.py
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json > $null
python -c "import json, pathlib; p=pathlib.Path('14_context/money_workflows/experiment_tracker.jsonl'); [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]; print('experiment tracker jsonl ok')"
git diff --check
```

If these fail, fix only the intentional N+3.18 files.

### Step 2: Confirm CLI Help

Run:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python 03_scripts/money_workflow_new_experiment.py --help
```

Confirm:

- router help includes `--task video_to_money`
- money helper help includes scoring args and bucket thresholds

### Step 3: Video-To-Money Smoke

Run only if local Ollama/Gemma is available and the operator still approves local model smoke:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task video_to_money --input 14_context/money_workflows/sample_video_notes_n3_18.md --max-chars 12000
```

Inspect latest run:

```powershell
Get-ChildItem 05_logs/money_runs | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

Verify artifacts:

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

Open `run_summary.json` and confirm:

- `status` is `PASS`
- `api_usage` is `none`
- `external_calls` is `none`
- `model_output_executed` is `false`
- `auto_post`, `auto_sell`, `auto_email`, and `auto_commit_from_model` are `false`
- `approval_required_for_any_use` is `true`

### Step 4: Parser Review

Before committing, inspect `experiment_candidates.jsonl`.

Fix or explicitly document these likely issues:

- multiple candidates may collapse into one record if Gemma omits blank lines
- model text `approval_required: true` may become string `"true"` instead of boolean `true`
- generated candidates are not schema-compatible tracker records

Preferred fix:

- make the parser split candidates when it sees a repeated `workflow_type` or `product_idea` key
- force `approval_required` to boolean `true` after parsing
- include parse warnings in `run_summary.json` or separate artifact if candidate parsing is lossy

### Step 5: Scoring Dry-Run Smoke

Run:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --source "local smoke" --product-idea "AI operator prompt pack" --target-customer "solo AI builders" --pain-point "They waste time rebuilding prompts" --offer "Prompt pack draft artifact" --next-action "Draft local product outline only" --risk-level low --channel manual_review_first --speed-to-ship 5 --pain-intensity 4 --buyer-access 3 --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 --legal-tos-risk 2 --monetization-clarity 4 --content-volume-potential 5 --email-list-potential 4
```

Expected:

- dry-run prints JSON
- scoring object exists
- lower-is-better values are inverted
- total score and bucket print
- no file append occurs

### Step 6: Schema Alignment

Decide whether to tighten schema:

- add `required` lists for all ten `raw_scores`
- add `required` lists for all ten `adjusted_scores`
- optionally add min/max constraints to adjusted scores

If not tightening, document why script-level validation is sufficient.

### Step 7: Policy/Docs Updates

Update policy if finishing:

```text
23_configs/local_brain_router_policy.example.json
```

Recommended additions:

- include `video_to_money` in `local_task_classes`
- mention `05_logs/money_runs` as output root for video-to-money artifacts
- keep `autonomous_execution_enabled=false`
- keep no external/live actions

Write implementation docs:

```text
14_context/gemma_video_to_money_runner_n3_18.md
14_context/money_experiment_scoring_n3_18.md
14_context/money_runner_safety_review_n3_18.md
14_context/distribution_exposure_system_n3_18.md
```

Update state/log docs if still required by repo flow:

```text
14_context/current_state.md
14_context/next_actions.md
14_context/ghoti_finish_line_log.md
01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py
```

### Step 8: Stage Carefully

Likely N+3.18 files to stage if finishing:

```text
01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
03_scripts/money_workflow_new_experiment.py
14_context/money_workflows/experiment_tracker.schema.json
14_context/money_workflows/sample_video_notes_n3_18.md
23_configs/local_brain_router_policy.example.json
14_context/gemma_video_to_money_runner_n3_18.md
14_context/money_experiment_scoring_n3_18.md
14_context/money_runner_safety_review_n3_18.md
14_context/distribution_exposure_system_n3_18.md
14_context/current_state.md
14_context/next_actions.md
14_context/ghoti_finish_line_log.md
01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py
```

Stage smoke artifacts only if the operator wants them committed.

Never stage unrelated local dirt:

```text
.claude/skills/
05_logs/local_brain_runs/
CV docs
output/
21_repos/third_party/.gitkeep
14_context/ghoti_current_prompt_N1_6.md
01_projects/mcp_server/test.txt
14_context/ghoti_external_repo_tool_intake.md
```

Check:

```powershell
git diff --cached --name-status
git diff --cached --check
```

### Step 9: Commit And Push

Recommended finish commit:

```text
feat/ghoti milestone N+3.18 - add Gemma video-to-money runner and experiment scoring
```

Push:

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## If Pausing N+3.18

Do not reset or delete files without explicit operator approval.

Minimum pause path:

1. Create a pause note under `14_context/` explaining why N+3.18 is parked.
2. Record exact dirty files.
3. Record whether files are preserved in the worktree, stashed, branched, or left dirty.
4. Do not stage runtime/script/schema files unless the pause milestone explicitly includes a safe preservation mechanism.
5. Do not continue implementation-dependent milestones as if N+3.18 is complete.

Possible pause commit:

```text
docs(ghoti): record N+3.18 paused dirty implementation state
```

## Safety Gates

Never allow N+3.18 to:

- fetch YouTube URLs
- scrape platforms
- post content
- sell/list products
- send email
- outreach/DM people
- process payments
- use live accounts
- execute model output
- auto-append model candidates to tracker without review
- fake proof, testimonials, scarcity, engagement, or income claims

## What Not To Touch

Unless explicitly scoped:

- dashboard files
- third-party repos
- `.claude/skills/`
- CV docs
- `output/`
- prompt scratch files
- unrelated external tool intake docs
- old local brain logs

## Next Milestone After Completion

After N+3.18 is finished and pushed:

```text
N+3.29 Claude - Weekly Money Review Artifact Generator
```

Then:

```text
N+3.30 - Weekly Review Artifact Dashboard Read View
N+3.31 - Manual Decision Candidate Review To Queue Draft Intake
N+3.32 - Manual Decision Queue Read View And Operator Work Session Planner
```
