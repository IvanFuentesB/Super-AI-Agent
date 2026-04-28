# Codex N+3.17 Next Claude Implementation Prompt Review

Status: codex_audit_only / next_claude_scope_review / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 77bfb74

## Recommended Next Claude Code Milestone

N+3.18 - Gemma Video-to-Money Intake Runner + Money Experiment Scoring

## Immediate Claude Objective

Claude Code should finish the safe repo-local foundation that turns the money workflow plans into usable templates and local helpers. The work should stay inside the repo, avoid live accounts, and avoid all external tooling installs.

## Complete N+3.17/N+3.18 Implementation Plan

1. Reconcile dirty runtime files from the interrupted Claude lane.
2. Validate and commit `compress_context` only if it passes safety checks.
3. Create `14_context/money_workflows/` structure.
4. Add money workflow templates and starter JSONL tracker.
5. Add optional `03_scripts/money_workflow_new_experiment.py` if small and safe.
6. Keep all output local and artifact-only.
7. Update state docs and finish-line log if Claude owns that milestone.
8. Validate, stage only intended files, commit, and push if allowed.

## Exact Files Claude Should Create

Money workflow docs/templates:

- `14_context/money_workflows/README.md`
- `14_context/money_workflows/money_os_index.md`
- `14_context/money_workflows/templates/experiment_tracker.schema.json`
- `14_context/money_workflows/templates/video_to_money_intake_template.md`
- `14_context/money_workflows/templates/digital_product_shot_template.md`
- `14_context/money_workflows/templates/content_batch_template.md`
- `14_context/money_workflows/templates/simple_phone_game_pipeline.md`
- `14_context/money_workflows/templates/whop_workflow_plan.md`
- `14_context/money_workflows/templates/distribution_and_exposure_checklist.md`
- `14_context/money_workflows/experiments/experiment_tracker.jsonl`

Optional helper:

- `03_scripts/money_workflow_new_experiment.py`

Optional logs/output directories:

- `05_logs/money_workflow_runs/` only if a script creates small local test artifacts

Runtime/policy files only if reconciling interrupted N+3.15 work:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `23_configs/local_brain_router_policy.example.json`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` only if adding or reconciling seeds is in scope

State files if explicitly part of Claude milestone:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`

## Exact Files Claude Should Avoid

- `14_context/ghoti_current_prompt.md`
- `14_context/ghoti_current_prompt_N1_6.md`
- `.claude/skills/`
- CV docs
- `output/`
- third-party repo contents under `21_repos/third_party/**`
- CUA smoke artifacts unless specifically requested
- prompt scratch files
- any live account config or secret file

## Validation Checklist

Core validation:

```powershell
python -m py_compile 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python -c "import json; json.load(open('23_configs/local_brain_router_policy.example.json', encoding='utf-8')); print('policy json ok')"
python -c "import json; json.load(open('14_context/money_workflows/templates/experiment_tracker.schema.json', encoding='utf-8')); print('schema json ok')"
python -c "import json; [json.loads(line) for line in open('14_context/money_workflows/experiments/experiment_tracker.jsonl', encoding='utf-8') if line.strip()]; print('tracker jsonl ok')"
git diff --check
git diff --cached --check
```

If helper script is added:

```powershell
python -m py_compile 03_scripts/money_workflow_new_experiment.py
python 03_scripts/money_workflow_new_experiment.py --dry-run --id money_test_001 --workflow-type digital_product --hypothesis "Test" --product-or-offer "Test product" --audience "builders" --channel "draft_only" --cost 0 --time-budget "30 minutes" --expected-revenue 0 --risk-level low --approval-required publish_approval
```

If Gemma compression is tested:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task compress_context --input 14_context/codex_n3_16_video_to_money_pipeline.md --max-chars 12000
```

## Stage, Commit, Push Checklist

Before staging:

- run `git status --short`
- confirm no unrelated dirty files will be staged
- confirm third-party files are not staged
- confirm prompt scratch files are not staged
- confirm `.claude/skills/`, CV docs, and `output/` are not staged

Stage only the milestone files.

Recommended commit if implementing templates and helper:

```text
feat/ghoti milestone N+3.18 - add Gemma money workflow runner and experiment scoring
```

Push only after validation passes:

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## Safety Requirements

Claude must not:

- post content
- send outreach
- scrape platforms
- use live accounts
- sell products
- create Whop/Gumroad/Shopify listings
- run Paperclip/OpenClaw/n8n/Unity-MCP
- clone leaked/proprietary code
- run Docker/CUA
- execute model output
- weaken approval gates

## Acceptance Criteria

PASS means:

- `compress_context` is validated or clearly deferred.
- money workflow folder exists.
- templates exist.
- starter tracker JSONL validates.
- optional helper is dry-run-first and local-only.
- no live actions occur.
- no external tools are installed or wired.
- state docs honestly describe planning/runtime truth.

## Exact Next Recommended Milestone

N+3.18 - Gemma Video-to-Money Intake Runner + Money Experiment Scoring

Goal:

- Let the user create many money experiment cards quickly.
- Route easy transcript/note compression to Gemma.
- Score experiments locally.
- Keep every publish, outreach, account, spend, Whop, app-store, and platform action human-approved.
