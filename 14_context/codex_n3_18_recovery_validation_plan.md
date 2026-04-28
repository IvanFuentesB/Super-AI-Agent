# Codex N+3.18 Recovery Validation Plan

Status: codex_recovery_plan / continue_partial_work / no_runtime_changes

## Goal

When Claude Code returns, continue the dirty N+3.18 implementation instead of restarting. The validation target is a safe local Gemma video-to-money runner plus money experiment scoring, with artifact-only outputs and no live account, posting, scraping, selling, payment, app-store, Docker, or CUA actions.

## Static Checks

Run:

```powershell
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py', encoding='utf-8').read()); print('LOCAL ROUTER AST OK')"
python -c "import ast; ast.parse(open('03_scripts/money_workflow_new_experiment.py', encoding='utf-8').read()); print('MONEY SCRIPT AST OK')"
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json > NUL
git diff --check
```

Expected result:

- Both Python files parse successfully.
- Schema JSON parses successfully.
- `git diff --check` has no whitespace errors.

## Gemma Video-to-Money Smoke

Run only if Ollama and `gemma3:4b` are still locally available. Do not pull models in the recovery continuation unless the user explicitly approves a new pull.

Suggested command:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task video_to_money --input 14_context/money_workflows/sample_video_notes_n3_18.md --max-chars 12000
```

Expected result:

- A local artifact folder is created under the chosen N+3.18 money run root.
- Required files exist:
  - `request.json`
  - `source_excerpt.md`
  - `source_summary.md` or documented equivalent
  - `product_ideas.md`
  - `content_angles.md`
  - `experiment_candidates.jsonl`
  - `distribution_plan.md`
  - `risk_review.md`
  - `run_summary.json`
- `run_summary.json` records:
  - no external API use
  - model output was not executed
  - no posting
  - no selling
  - no email/outreach
  - approval required for public or money-facing use

## Experiment Scoring Smoke

Run a dry-run first:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --hypothesis "A prompt pack for AI build logs can attract early buyers" --product-or-offer "AI build-log prompt pack" --audience "AI builders and students" --channel "short-form plus email list" --cost 0 --time-budget "2 hours" --risk-level low --approval-required true --speed-to-ship 5 --pain-intensity 3 --buyer-access 3 --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 --legal-tos-risk 1 --monetization-clarity 4 --content-volume-potential 4 --email-list-potential 4
```

Expected result:

- Dry-run prints a valid JSON record.
- Scoring includes raw scores, adjusted scores, total score, and priority bucket.
- No append occurs during dry-run.

Only run a real append if the milestone explicitly intends to add an experiment record:

```powershell
python 03_scripts/money_workflow_new_experiment.py --workflow-type digital_product --hypothesis "A prompt pack for AI build logs can attract early buyers" --product-or-offer "AI build-log prompt pack" --audience "AI builders and students" --channel "short-form plus email list" --cost 0 --time-budget "2 hours" --risk-level low --approval-required true --speed-to-ship 5 --pain-intensity 3 --buyer-access 3 --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 --legal-tos-risk 1 --monetization-clarity 4 --content-volume-potential 4 --email-list-potential 4
```

## Node Checks

If dashboard or Node files remain untouched, Node checks are not required. If Claude unexpectedly edits dashboard files, run the existing project-specific Node validation before staging.

## Required Docs To Finish

Create or update:

- `14_context/gemma_video_to_money_runner_n3_18.md`
- `14_context/money_experiment_scoring_n3_18.md`
- `14_context/money_runner_safety_review_n3_18.md`
- `14_context/distribution_exposure_system_n3_18.md`

## State Updates

Update only if part of the final Claude implementation:

- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`

## Staging Whitelist

Stage only intentional N+3.18 implementation files, likely:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `03_scripts/money_workflow_new_experiment.py`
- `14_context/money_workflows/experiment_tracker.schema.json`
- `14_context/money_workflows/sample_video_notes_n3_18.md`
- `14_context/gemma_video_to_money_runner_n3_18.md`
- `14_context/money_experiment_scoring_n3_18.md`
- `14_context/money_runner_safety_review_n3_18.md`
- `14_context/distribution_exposure_system_n3_18.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` if intentionally updated
- `14_context/current_state.md` if intentionally updated
- `14_context/next_actions.md` if intentionally updated
- `14_context/ghoti_finish_line_log.md` if intentionally updated
- small N+3.18 smoke artifacts if intentionally committed

## Do Not Stage

- `14_context/ghoti_external_repo_tool_intake.md` unless separately approved.
- `21_repos/third_party/.gitkeep`.
- `.claude/skills/`.
- `01_projects/mcp_server/test.txt`.
- `14_context/ghoti_current_prompt_N1_6.md`.
- local CV `.docx` files.
- `output/`.
- unrelated local brain run artifacts.
- third-party repo contents.

## Commit And Push

After validation passes and the staged file list is clean:

```powershell
git diff --cached --name-status
git commit -m "feat/ghoti milestone N+3.18 - add Gemma video-to-money runner and experiment scoring"
git push origin feat/ghoti-visible-operator-stack
```
