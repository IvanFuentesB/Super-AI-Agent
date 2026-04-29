# Codex N+3.27 Claude Implementation Checklist

Status: codex_planning_only / claude_handoff / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Recommended Order

Claude Code should finish or consciously pause N+3.18 first. The current dirty N+3.18 implementation includes the Gemma video-to-money runner and experiment scoring work. Do not lose or reset that work.

If the operator decides to proceed with N+3.27 implementation later, keep it read-only and local-only.

## Files Claude May Modify Later

Potential implementation files:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `14_context/money_workflows/manual_decision_queue.schema.json`
- `14_context/money_workflows/manual_decision_queue.jsonl`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py`

Only touch these when the implementation milestone explicitly begins.

## Files Claude Must Avoid Unless Explicitly Approved

- `.claude/skills/`
- `21_repos/third_party/**`
- `output/**`
- CV `.docx` files
- prompt scratch files
- live account exports
- third-party repo contents
- unrelated dirty files

## Implementation Steps

1. Run repo truth:

```powershell
git status --short
git branch --show-current
git log --oneline -12
git fetch origin feat/ghoti-visible-operator-stack
git diff --cached --name-status
```

2. Decide whether N+3.18 is finished or explicitly paused.

3. If implementing `weekly_money_review`, add a local-only task to the existing local brain router.

4. Enforce path and safety gates:

- repo-root-only inputs
- allowed file extensions only
- max chars
- artifact-only outputs
- no model output execution
- no external API
- no tracker mutation
- no live account actions

5. Create weekly review artifacts under:

```text
05_logs/money_reviews/<run_id>/
```

Required files:

- `request.json`
- `source_snapshot.md`
- `weekly_summary.md`
- `double_down.md`
- `iterate.md`
- `pause_or_kill.md`
- `next_10_shots.md`
- `distribution_gaps.md`
- `email_list_opportunities.md`
- `manual_decision_queue_candidates.jsonl`
- `risk_review.md`
- `run_summary.json`

6. Add the manual decision queue schema/sample only if the milestone explicitly approves it:

```text
14_context/money_workflows/manual_decision_queue.schema.json
14_context/money_workflows/manual_decision_queue.jsonl
```

7. Add read-only dashboard route later:

```text
GET /api/ghoti/money/weekly-review/summary
```

8. Add read-only dashboard card:

```text
Money OS - Weekly Review
```

9. Do not add mutation buttons:

- no approve button
- no delete button
- no post button
- no send button
- no sell button
- no publish button
- no scrape button

10. Update state docs if implementation happens:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`

11. Update wait/resume seeds only if useful:

- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py`

## Validation Commands

Run static checks:

```powershell
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py', encoding='utf-8').read()); print('LOCAL ROUTER AST OK')"
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json
git diff --check
```

If JSONL files are added, run:

```powershell
python -c "import json, pathlib; p=pathlib.Path('14_context/money_workflows/manual_decision_queue.jsonl'); [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]; print('manual decision queue jsonl ok')"
```

If a weekly review smoke is run:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task weekly_money_review --input 14_context/money_workflows/experiment_tracker.jsonl --max-chars 25000
```

Then verify:

- artifacts exist under `05_logs/money_reviews/<run_id>/`
- `run_summary.json` says no live action was taken
- `manual_decision_queue_candidates.jsonl` is draft-only
- no source tracker was mutated

## Stage Checklist

Stage only intentional N+3.27 implementation files. Before commit:

```powershell
git diff --cached --name-status
git diff --cached --check
```

Do not stage:

- dirty Claude N+3.18 partials unless this milestone explicitly finishes them
- `.claude/skills/`
- CV docs
- `output/`
- third-party repo files
- prompt scratch files
- unrelated local logs

## Commit

Recommended future commit message:

```text
feat/ghoti milestone N+3.27 — add weekly money review and manual decision queue
```

Then push:

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## Final Report Fields

Claude should report:

- branch
- starting HEAD
- new commit hash
- pushed yes/no
- files changed
- validation pass/fail
- weekly review generator truth
- decision queue truth
- dashboard read-only truth
- runtime wiring truth
- install/run truth
- live account/action truth
- dirty files intentionally left unstaged
- next milestone recommendation

## Exact Next Claude Recommendation

Continue or consciously pause N+3.18 first. Then implement N+3.27 only as a local weekly review artifact generator plus read-only dashboard summary, with no live actions and no tracker mutation unless explicitly approved.
