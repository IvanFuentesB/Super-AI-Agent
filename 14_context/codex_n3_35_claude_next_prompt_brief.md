# Codex N+3.35 Claude Next Prompt Brief

Status: codex_audit_only / claude_prompt_brief / no_runtime_edits

Date: 2026-05-01
Branch: feat/ghoti-visible-operator-stack
Current HEAD: 2e81aa0

## Recommended Claude Target

Because N+3.18 is still dirty and unresolved, the next Claude Code action should be:

```text
N+3.18 Follow-Up Recovery - Finish or Consciously Pause Gemma Video-to-Money Runner + Experiment Scoring
```

Do not start N+3.29 yet.

## Current Truth

Current HEAD and origin:

```text
2e81aa0 docs(ghoti): specify Obsidian local memory layer
```

No new Claude commit was found after N+3.34.

Dirty N+3.18 files still present:

```text
01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
03_scripts/money_workflow_new_experiment.py
14_context/money_workflows/experiment_tracker.schema.json
14_context/money_workflows/sample_video_notes_n3_18.md
```

Other unrelated dirty files are also present and must not be staged.

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

Read:

```text
14_context/codex_n3_35_post_n3_18_audit.md
14_context/codex_n3_35_n3_18_validation_gap_report.md
14_context/codex_n3_35_next_sequence_lock.md
14_context/codex_n3_33_claude_resume_pack.md
14_context/codex_n3_33_validation_matrix.md
```

## If Finishing N+3.18

Complete the dirty implementation without restarting from scratch.

Required implementation decisions:

1. Review and harden `video_to_money` candidate parsing if needed.
2. Confirm `.md`/`.txt` repo-local input restriction.
3. Confirm all output is artifact-only under `05_logs/money_runs/<run_id>/`.
4. Confirm no tracker mutation from `video_to_money`.
5. Confirm no model output execution.
6. Confirm no posting/selling/emailing/payments/live-account actions.
7. Decide whether to tighten inner scoring requirements in `experiment_tracker.schema.json`.
8. Update policy/state/log/wait-resume docs if the repo flow still requires them.

Create or update implementation docs:

```text
14_context/gemma_video_to_money_runner_n3_18.md
14_context/money_experiment_scoring_n3_18.md
14_context/money_runner_safety_review_n3_18.md
14_context/distribution_exposure_system_n3_18.md
```

## Required Validation Commands

Static checks:

```powershell
python -m py_compile 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python -m py_compile 03_scripts/money_workflow_new_experiment.py
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json > $null
python -c "import json, pathlib; p=pathlib.Path('14_context/money_workflows/experiment_tracker.jsonl'); rows=[json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()] if p.exists() else []; print(f'experiment_tracker jsonl ok: {len(rows)} rows')"
git diff --check
```

CLI help:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python 03_scripts/money_workflow_new_experiment.py --help
```

Gemma smoke if local model approval still applies:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task video_to_money --input 14_context/money_workflows/sample_video_notes_n3_18.md --max-chars 12000
```

Scoring dry-run:

```powershell
python 03_scripts/money_workflow_new_experiment.py --dry-run --workflow-type digital_product --source "local smoke" --product-idea "AI operator prompt pack" --target-customer "solo AI builders" --pain-point "They waste time rebuilding prompts" --offer "Prompt pack draft artifact" --next-action "Draft local product outline only" --risk-level low --channel manual_review_first --speed-to-ship 5 --pain-intensity 4 --buyer-access 3 --distribution-leverage 4 --proof-difficulty 2 --build-complexity 2 --legal-tos-risk 2 --monetization-clarity 4 --content-volume-potential 5 --email-list-potential 4
```

Staged checks:

```powershell
git diff --cached --name-status
git diff --cached --check
```

## If Pausing N+3.18 Instead

Do not leave ambiguity.

Create a pause doc such as:

```text
14_context/n3_18_pause_record.md
```

It should state:

- why N+3.18 is paused
- what dirty files remain
- whether the dirty diff should be preserved for a later Claude pass
- what validations did and did not pass
- what later milestones must not depend on until N+3.18 is resumed

Do not start N+3.29 runtime implementation while N+3.18 is paused unless the operator explicitly accepts that dependency gap.

## Staging Rules

If finishing, likely intentional files:

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

Do not stage unrelated local dirt:

```text
.claude/skills/
05_logs/local_brain_runs/
CV_*.docx
output/
21_repos/third_party/.gitkeep
14_context/ghoti_current_prompt_N1_6.md
01_projects/mcp_server/test.txt
14_context/ghoti_external_repo_tool_intake.md
```

Stage smoke artifacts only if the operator explicitly wants them committed.

## Commit Message Suggestion

If finishing:

```text
feat(ghoti): finish N+3.18 video-to-money runner and experiment scoring
```

Alternative matching older plan:

```text
feat/ghoti milestone N+3.18 - add Gemma video-to-money runner and experiment scoring
```

If pausing:

```text
docs(ghoti): pause N+3.18 video-to-money runner recovery
```

## Safety Gates

Preserve:

- no live accounts
- no posting
- no selling
- no outreach
- no payments
- no scraping
- no app-store actions
- no fake proof
- no fake engagement
- no model-output execution
- human approval before public or money-facing action

## Next Milestone After Completion

If N+3.18 is finished and pushed, the next Claude milestone should be:

```text
N+3.29 Claude - Weekly Money Review Artifact Generator
```

If N+3.18 is paused, the next milestone should remain a recovery/resolution milestone, not a dependent Money OS runtime layer.
