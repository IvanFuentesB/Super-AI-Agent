# Codex N+3.18 Next Claude Continuation Prompt Review

Status: continuation_prompt_review / preserve_dirty_partial_work / no_runtime_changes

## Continuation Principle

Continue from the existing dirty N+3.18 implementation. Do not restart from scratch, do not reset, do not delete, and do not overwrite Claude's partial work. The current dirty implementation already contains meaningful progress for the Gemma video-to-money runner and money experiment scoring.

## Current Dirty Implementation To Preserve

Continue from:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `03_scripts/money_workflow_new_experiment.py`
- `14_context/money_workflows/experiment_tracker.schema.json`
- `14_context/money_workflows/sample_video_notes_n3_18.md`

Leave unrelated local-only files alone.

## What Claude Code Should Finish

1. Review the existing `video_to_money` route in `local_brain_router.py`.
2. Decide whether the run output path should stay `05_logs/money_runs/<run_id>/` or be aligned with the earlier spec path `05_logs/money_workflow_runs/<run_id>/`.
3. Verify the model output parser creates usable `experiment_candidates.jsonl` records.
4. Normalize `approval_required` to a boolean if the model returns it as text.
5. Review scoring in `money_workflow_new_experiment.py`.
6. Verify `experiment_tracker.schema.json` matches the script output.
7. Keep all outputs artifact-only.
8. Keep no URL fetch, no scraping, no posting, no selling, no outreach, no payment, no app-store actions, no Docker, and no CUA execution.

## Docs Claude Should Create

Create:

- `14_context/gemma_video_to_money_runner_n3_18.md`
- `14_context/money_experiment_scoring_n3_18.md`
- `14_context/money_runner_safety_review_n3_18.md`
- `14_context/distribution_exposure_system_n3_18.md`

The docs should state:

- Gemma is used only for local text artifacts.
- Inputs are local markdown/text files only.
- No model output is executed.
- Experiment candidates are suggestions only.
- Public, money-facing, outreach, or account actions require explicit human approval.
- This is API-saving context work, not cap bypass or quota evasion.

## Smoke Tests Claude Should Run

Static checks:

```powershell
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py', encoding='utf-8').read()); print('LOCAL ROUTER AST OK')"
python -c "import ast; ast.parse(open('03_scripts/money_workflow_new_experiment.py', encoding='utf-8').read()); print('MONEY SCRIPT AST OK')"
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json > NUL
```

Gemma video-to-money smoke, only if `gemma3:4b` is locally available:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task video_to_money --input 14_context/money_workflows/sample_video_notes_n3_18.md --max-chars 12000
```

Scoring dry-run:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --hypothesis "A prompt pack for AI build logs can attract early buyers" --product-or-offer "AI build-log prompt pack" --audience "AI builders and students" --channel "short-form plus email list" --cost 0 --time-budget "2 hours" --risk-level low --approval-required true --speed-to-ship 5 --pain-intensity 3 --buyer-access 3 --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 --legal-tos-risk 1 --monetization-clarity 4 --content-volume-potential 4 --email-list-potential 4
```

Repository checks:

```powershell
git diff --check
git status --short
```

## State And Supervisor Updates

Update only after the smoke path is validated:

- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`

The finish-line log should record:

- previous HEAD
- new commit hash initially TBD
- pushed status initially TBD
- files changed
- validation commands and results
- Gemma video-to-money smoke truth
- scoring truth
- runtime wiring truth: local helper only, not autonomous money workflow
- live account/posting truth: none
- dirty files intentionally left unstaged
- next recommended milestone: `N+3.19 - Money Workflow Dashboard Read View + Shot Counter`

## Staging Checklist

Before commit:

```powershell
git diff --cached --name-status
```

Only intentional N+3.18 files should be staged. Do not stage:

- `14_context/ghoti_external_repo_tool_intake.md`
- `21_repos/third_party/.gitkeep`
- `.claude/skills/`
- `01_projects/mcp_server/test.txt`
- `14_context/ghoti_current_prompt_N1_6.md`
- CV docs
- `output/`
- unrelated local run artifacts
- third-party repo contents

## Commit And Push

If validation passes, commit:

```powershell
git commit -m "feat/ghoti milestone N+3.18 - add Gemma video-to-money runner and experiment scoring"
git push origin feat/ghoti-visible-operator-stack
```

## Recommended Claude Continuation Milestone

N+3.18 Claude Continuation - finish Gemma video-to-money runner, experiment scoring, docs, smoke tests, wait/resume seed, state updates, validation, commit, and push.
