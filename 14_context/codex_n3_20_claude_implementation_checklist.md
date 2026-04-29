# Codex N+3.20 Claude Implementation Checklist

Status: claude_implementation_checklist / weekly_review_generator / no_codex_runtime_changes
Date: 2026-04-29

## Sequencing Rule

Preferred:

1. Finish N+3.18 Gemma video-to-money runner + experiment scoring.
2. Implement N+3.19 money dashboard read view if chosen.
3. Implement N+3.20 weekly money review generator.

If the operator explicitly asks to implement N+3.20 first, Claude should consciously pause N+3.18 and avoid staging its dirty files unless finishing them too.

## Step 1 - Repo Truth

Run:

```powershell
git status --short
git branch --show-current
git log --oneline -10
git diff --cached --name-status
```

Confirm:

- branch is `feat/ghoti-visible-operator-stack`.
- no unexpected staged files.
- dirty N+3.18 files are understood and either finished or intentionally left unstaged.

## Step 2 - Read Required Context

Read:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `03_scripts/money_workflow_new_experiment.py`
- `14_context/money_workflows/experiment_tracker.jsonl`
- `14_context/money_workflows/experiment_tracker.schema.json`
- `14_context/money_workflows/money_os_index.md`
- `14_context/money_workflows/distribution_and_exposure_checklist.md`
- `14_context/codex_n3_20_weekly_money_review_generator_spec.md`
- `14_context/codex_n3_20_gemma_weekly_review_prompt_template.md`
- `14_context/codex_n3_20_money_review_scoring_model.md`

## Step 3 - Implement `weekly_money_review`

Modify only when implementation is approved:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`

Add:

- `_MONEY_REVIEWS_ROOT = _REPO_ROOT / "05_logs" / "money_reviews"`
- `_WEEKLY_MONEY_REVIEW_PROMPT_TEMPLATE`
- deterministic JSONL summary helper.
- malformed line counter.
- recent artifact summary helper if kept small and repo-local.
- `run_weekly_money_review(policy, input_arg, max_chars)`.
- CLI dispatch for `--task weekly_money_review`.

Do not add:

- external API calls.
- internet access.
- scraping.
- posting/selling/email/outreach/payment/app-store/account actions.
- model output execution.
- auto-commit from model output.

## Step 4 - Artifact Output

Write:

- `05_logs/money_reviews/<run_id>/request.json`
- `05_logs/money_reviews/<run_id>/tracker_excerpt.jsonl`
- `05_logs/money_reviews/<run_id>/weekly_review.md`
- `05_logs/money_reviews/<run_id>/top_experiments.md`
- `05_logs/money_reviews/<run_id>/kill_or_pause.md`
- `05_logs/money_reviews/<run_id>/distribution_gaps.md`
- `05_logs/money_reviews/<run_id>/email_list_opportunities.md`
- `05_logs/money_reviews/<run_id>/next_10_shots.md`
- `05_logs/money_reviews/<run_id>/risk_review.md`
- `05_logs/money_reviews/<run_id>/run_summary.json`

## Step 5 - Smoke Test

Run only if local Gemma/Ollama is available:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task weekly_money_review --input 14_context/money_workflows/experiment_tracker.jsonl --max-chars 20000
```

Verify:

- artifacts exist.
- `run_summary.json` records no live actions.
- missing scoring is tolerated.
- current 3 sample experiments are summarized.
- no tracker mutation occurs.

## Step 6 - Static Validation

Run:

```powershell
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py', encoding='utf-8').read()); print('LOCAL ROUTER AST OK')"
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json > NUL
git diff --check
git status --short
```

If dashboard files are touched unexpectedly, also run:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
```

## Step 7 - State Updates

Update:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`

Optionally update:

- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py`

State truth to record:

- weekly money review is local artifact generation only.
- Gemma output is advisory.
- no public/live actions.
- no tracker mutation unless explicitly implemented separately.
- Paperclip/OpenClaw/n8n/Unity-MCP/Mythos remain planning-only.

## Step 8 - Staging

Stage only intentional N+3.20 files, likely:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` if intentionally updated
- small `05_logs/money_reviews/<run_id>/` smoke artifacts if intentionally committed
- implementation docs if Claude creates them

Do not stage:

- unrelated dirty N+3.18 files unless completing N+3.18 too.
- `14_context/ghoti_external_repo_tool_intake.md`.
- `21_repos/third_party/.gitkeep`.
- `.claude/skills/`.
- `01_projects/mcp_server/test.txt`.
- CV docs.
- `output/`.
- prompt scratch files.
- third-party repo contents.

## Commit And Push

Commit:

```powershell
git commit -m "feat/ghoti milestone N+3.20 - add Gemma weekly money review generator"
git push origin feat/ghoti-visible-operator-stack
```

## Final Report Format

Claude should report:

- branch.
- previous HEAD.
- new commit hash.
- pushed yes/no.
- files changed.
- validation pass/fail.
- weekly review command truth.
- artifact path.
- Gemma/Ollama truth.
- tracker mutation truth.
- safety gate truth.
- runtime wiring truth.
- install/run truth.
- live account/action truth.
- dirty files intentionally left unstaged.
- next recommended milestone.
