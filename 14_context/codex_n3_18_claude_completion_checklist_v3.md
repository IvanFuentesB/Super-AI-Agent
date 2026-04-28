# Codex N+3.18 Claude Completion Checklist v3

Status: claude_completion_checklist / continue_dirty_work / no_codex_runtime_changes

## First Rule

Continue from the dirty partial N+3.18 files. Do not reset, delete, clean, or restart from scratch.

## Exact Claude Steps

1. Run repo truth:

```powershell
git status --short
git branch --show-current
git log --oneline -8
git diff --cached --name-status
```

2. Confirm the dirty implementation files are still present:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `03_scripts/money_workflow_new_experiment.py`
- `14_context/money_workflows/experiment_tracker.schema.json`
- `14_context/money_workflows/sample_video_notes_n3_18.md`

3. Run static checks:

```powershell
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py', encoding='utf-8').read()); print('local_brain_router AST OK')"
python -c "import ast; ast.parse(open('03_scripts/money_workflow_new_experiment.py', encoding='utf-8').read()); print('money script AST OK')"
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py', encoding='utf-8').read()); print('wait supervisor AST OK')"
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json > NUL
```

4. Run the Gemma video-to-money smoke only if local Gemma/Ollama is available:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task video_to_money --input 14_context/money_workflows/sample_video_notes_n3_18.md --max-chars 12000
```

5. Inspect artifacts under:

```text
05_logs/money_runs/<run_id>/
```

6. Confirm required artifacts:

- `request.json`
- `source_excerpt.md`
- `source_summary.md`
- `product_ideas.md`
- `content_angles.md`
- `experiment_candidates.jsonl`
- `distribution_plan.md`
- `risk_review.md`
- `run_summary.json`

7. Inspect `experiment_candidates.jsonl`:

- Records should be valid JSONL.
- Records should be useful candidate experiments.
- `approval_required` should be boolean true.
- If records collapse or parse poorly, fix `_candidates_to_jsonl`.

8. Run the scoring dry-run:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --source "sample_video_notes_n3_18" --product-idea "AI operator prompt pack" --target-customer "solo founders and AI builders" --pain-point "They waste time rebuilding prompts from scratch" --offer "A reusable operator prompt pack with content and business prompts" --next-action "Draft the first 10 prompts and one opt-in page outline" --risk-level low --channel "short-form video" --channel "email list" --speed-to-ship 5 --pain-intensity 3 --buyer-access 3 --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 --legal-tos-risk 1 --monetization-clarity 4 --content-volume-potential 4 --email-list-potential 4
```

9. Confirm scoring output:

- `raw_scores`
- `adjusted_scores`
- `total_score`
- `priority_bucket`
- no append during dry-run
- no external API
- no live action

10. Create implementation docs:

- `14_context/gemma_video_to_money_runner_n3_18.md`
- `14_context/money_experiment_scoring_n3_18.md`
- `14_context/money_runner_safety_review_n3_18.md`
- `14_context/distribution_exposure_system_n3_18.md`

11. Update state/supervisor files only if intentional:

- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`

12. Run final validation:

```powershell
git diff --check
git status --short
```

13. Stage only intentional N+3.18 implementation files.

14. Commit:

```powershell
git commit -m "feat/ghoti milestone N+3.18 - add Gemma video-to-money runner and experiment scoring"
```

15. Push:

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## Files Claude May Stage If Intentionally Updated

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `03_scripts/money_workflow_new_experiment.py`
- `14_context/money_workflows/experiment_tracker.schema.json`
- `14_context/money_workflows/sample_video_notes_n3_18.md`
- `14_context/gemma_video_to_money_runner_n3_18.md`
- `14_context/money_experiment_scoring_n3_18.md`
- `14_context/money_runner_safety_review_n3_18.md`
- `14_context/distribution_exposure_system_n3_18.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- small N+3.18 smoke artifacts if deliberately included

## Files Claude Must Not Stage

- `14_context/ghoti_external_repo_tool_intake.md`
- `21_repos/third_party/.gitkeep`
- `.claude/skills/`
- `01_projects/mcp_server/test.txt`
- `14_context/ghoti_current_prompt_N1_6.md`
- local CV `.docx` files
- `output/`
- unrelated `05_logs/local_brain_runs/*`
- third-party repo contents
- dashboard files unless explicitly scoped

## Expected Final Report Fields

Claude should report:

- branch
- previous HEAD
- new commit hash
- pushed yes/no
- files changed
- validation pass/fail
- Gemma video-to-money smoke truth
- artifact path
- experiment scoring dry-run truth
- safety gate truth
- runtime wiring truth
- install/run truth
- live account/action truth
- dirty files intentionally left unstaged
- next milestone: `N+3.19 - Money Workflow Dashboard Read View + Shot Counter`
