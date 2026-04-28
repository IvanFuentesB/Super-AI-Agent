# Codex N+3.18 Next Claude Prompt Delta

Status: prompt_delta_only / continue_dirty_work / no_runtime_changes

## Core Instruction For Claude

Continue the dirty N+3.18 partial implementation. Do not restart from scratch. Do not reset, delete, or overwrite the current dirty files.

Dirty N+3.18 files to preserve and finish:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `03_scripts/money_workflow_new_experiment.py`
- `14_context/money_workflows/experiment_tracker.schema.json`
- `14_context/money_workflows/sample_video_notes_n3_18.md`

## Delta From Prior Recovery Prompt

Add these specific checks to the next Claude prompt:

1. Verify whether `05_logs/money_runs/<run_id>/` should remain the final money-run artifact path or be renamed to `05_logs/money_workflow_runs/<run_id>/`.
2. Verify whether `source_summary.md` is the final artifact name or whether a `business_model_summary.md` alias/name is needed.
3. Run the Gemma `video_to_money` smoke and inspect `experiment_candidates.jsonl`.
4. Confirm `_candidates_to_jsonl` creates useful records when Gemma emits bullet lists.
5. Normalize `approval_required` so it remains boolean true, not a text string.
6. Run the scoring dry-run with all ten score fields.
7. Confirm the generated scoring object matches `experiment_tracker.schema.json`.
8. Add explicit docs saying the runner does not fetch URLs, scrape, download YouTube, post, sell, email, or use live accounts.

## Claude Should Finish

- Implementation cleanup for the dirty `video_to_money` runner.
- Implementation cleanup for money experiment scoring.
- `14_context/gemma_video_to_money_runner_n3_18.md`
- `14_context/money_experiment_scoring_n3_18.md`
- `14_context/money_runner_safety_review_n3_18.md`
- `14_context/distribution_exposure_system_n3_18.md`
- Wait/resume seed update if appropriate.
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- Static validation.
- Gemma smoke validation.
- Scoring dry-run validation.
- Stage only intentional N+3.18 files.
- Commit and push.

## Claude Must Not Do

- Do not install Paperclip.
- Do not install OpenClaw.
- Do not install n8n.
- Do not install Unity-MCP.
- Do not install Mythos, Dolphin, CUDA, Manus, or any new external runtime.
- Do not clone leaked code.
- Do not run Docker or CUA.
- Do not scrape or download YouTube.
- Do not post, sell, email, outreach, pay, trade, submit, or use live accounts.
- Do not stage unrelated dirty files.
- Do not stage `.claude/skills/`, CV files, `output/`, prompt scratch files, local brain logs, or third-party repo contents.

## Commit Target

After validation passes:

```powershell
git commit -m "feat/ghoti milestone N+3.18 - add Gemma video-to-money runner and experiment scoring"
git push origin feat/ghoti-visible-operator-stack
```

## Exact Next Claude Recommendation

Continue N+3.18 dirty partial work and finish Gemma Video-to-Money Runner + Experiment Scoring.

## Future Milestone After That

`N+3.19 - Money Workflow Dashboard Read View + Shot Counter`
