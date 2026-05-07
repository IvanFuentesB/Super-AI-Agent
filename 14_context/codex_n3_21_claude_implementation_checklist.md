# Codex N+3.21 Claude Implementation Checklist

Status: codex_planning_only / claude_execution_checklist / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Recommended Order

Claude Code should finish or consciously pause N+3.18 before implementing this milestone. N+3.18 owns the dirty video-to-money runner and experiment scoring work. If that work remains dirty, Claude should either complete it first or explicitly state why N+3.21 is safe to implement around it.

## Implementation Goal

Implement a local Gemma-powered `content_batch` task that turns one repo-local content brief into artifact-only content batch drafts.

No posting, selling, email sending, scraping, live-account usage, or external automation is allowed.

## Files Claude May Need To Create Or Edit Later

Likely implementation files:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `14_context/money_workflows/content_batch_input_n3_21.md`
- `14_context/money_workflows/content_shots.example.jsonl`
- `14_context/money_workflows/content_shots.schema.json`
- `14_context/content_batch_planner_n3_21.md`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` only if adding a concise seed

Artifact output directory:

- `05_logs/content_batches/<run_id>/`

## Files Claude Should Not Touch Without New Approval

- dashboard implementation files unless the milestone changes
- third-party repo contents
- `.claude/skills/`
- prompt scratch files
- CV files
- `output/`
- live account credentials
- Paperclip/OpenClaw/n8n/Unity-MCP/Mythos runtime files

## Required Behavior

The `content_batch` task should:

1. Accept a repo-local `.md`, `.txt`, or `.json` input.
2. Enforce repo-root-only path safety.
3. Enforce max input characters.
4. Use local Gemma/Ollama only if available.
5. Produce artifacts only under `05_logs/content_batches/<run_id>/`.
6. Write `request.json`, source excerpt, model response, split markdown artifacts, and `run_summary.json`.
7. Include 30 hooks, 10 long-form ideas, 10 email ideas, 10 community post ideas, 5 lead magnets, 5 CTAs, repurposing map, safety review, weekly calendar, and next 10 shots.
8. Never execute model output.
9. Never post, send, sell, scrape, browse, or use live accounts.
10. Require human approval for all public or money-facing actions.

## Suggested Smoke

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task content_batch --input 14_context/money_workflows/content_batch_input_n3_21.md --max-chars 20000
```

After the smoke, inspect:

- `05_logs/content_batches/<run_id>/request.json`
- `05_logs/content_batches/<run_id>/response.txt`
- `05_logs/content_batches/<run_id>/next_10_shots.md`
- `05_logs/content_batches/<run_id>/safety_claims_review.md`
- `05_logs/content_batches/<run_id>/run_summary.json`

## Validation Commands

```powershell
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py', encoding='utf-8').read()); print('LOCAL ROUTER AST OK')"
python -c "import ast; ast.parse(open('03_scripts/money_workflow_new_experiment.py', encoding='utf-8').read()); print('MONEY SCRIPT AST OK')"
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json
git diff --check
git status --short
```

If `content_shots.schema.json` is added, validate it with:

```powershell
python -m json.tool 14_context/money_workflows/content_shots.schema.json
```

If `content_shots.example.jsonl` is added, validate it with a JSONL parse.

## Stage / Commit / Push

Stage only intentional N+3.21 files. Do not stage unrelated dirty files from interrupted N+3.18 work unless explicitly finishing that milestone at the same time.

Recommended commit:

```text
feat/ghoti milestone N+3.21 — add Gemma content batch planner
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
- Gemma smoke path
- content batch artifact truth
- safety/live-action truth
- runtime wiring truth
- dirty files intentionally left unstaged
- next recommended milestone

## Next Future Milestone

After N+3.21, a strong follow-up is:

```text
N+3.22 — Digital Product / Whop Draft Pipeline
```

That milestone should still be draft-only unless the user explicitly approves live product listings or account actions.
