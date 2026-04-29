# Codex N+3.29 Claude Implementation Checklist

Status: codex_planning_only / claude_handoff / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Goal

Add a local `weekly_money_review` artifact generator that reads Money OS files and writes review artifacts under `05_logs/money_reviews/<run_id>/`.

## Step 1: Resolve Dirty N+3.18 Boundary

Before implementing N+3.29, Claude must choose one:

- finish N+3.18 dirty partial implementation
- consciously pause N+3.18 and avoid staging those dirty files

Do not mix N+3.29 artifact generator work with N+3.18 runtime/scoring changes unless the operator explicitly expands the milestone scope.

## Step 2: Repo Truth

Run:

```powershell
git status --short
git branch --show-current
git log --oneline --graph --decorate --all -12
git fetch origin feat/ghoti-visible-operator-stack
git diff --cached --name-status
```

Record:

- starting HEAD
- origin HEAD
- dirty files
- staged files
- whether N+3.18 is dirty, finished, or paused

## Step 3: Add `weekly_money_review` Task

Modify only when implementation is approved:

```text
01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
```

Add:

- `run_weekly_money_review(policy, input_arg, max_chars)`
- `weekly_money_review` dispatch in `main`
- help text for the new task

The task should:

- require `--input`
- validate repo-root-only input
- accept `.jsonl`, `.json`, `.md`, and `.txt` for local notes/tracker input
- create `05_logs/money_reviews/<run_id>/`
- write required artifacts
- return nonzero only on real implementation errors

## Step 4: Add Tolerant Readers

Add focused helpers:

- `_read_jsonl_tolerant(path, label, max_records)`
- `_load_optional_json(path, label)`
- `_latest_money_review_run()`
- `_build_money_review_snapshot(...)`

Rules:

- missing optional files are warnings
- malformed JSONL lines are warnings
- blank lines are ignored
- parser never mutates sources
- parser caps records sent to Gemma

## Step 5: Add Prompt Template

Add prompt template from:

```text
14_context/codex_n3_29_weekly_review_prompt_template.md
```

The prompt must include:

- WEEKLY SUMMARY
- TOP EXPERIMENTS
- KILL / PAUSE LIST
- DISTRIBUTION GAPS
- EMAIL LIST OPPORTUNITIES
- CONTENT BATCH IDEAS
- NEXT 10 SHOTS
- RISK REVIEW
- MANUAL OPERATOR ACTIONS
- DECISION CANDIDATES

## Step 6: Add Artifact Writer

Write:

- `request.json`
- `tracker_snapshot.json`
- `weekly_summary.md`
- `top_experiments.md`
- `decisions_recommended.jsonl`
- `distribution_gaps.md`
- `email_list_opportunities.md`
- `next_10_shots.md`
- `risk_review.md`
- `run_summary.json`

Also save:

- `raw_model_response.txt`
- `parse_warnings.json` if parsing problems occur

## Step 7: Candidate Decision Handling

Extract `DECISION CANDIDATES` best-effort.

Rules:

- only save candidates to `decisions_recommended.jsonl`
- never append to `manual_decision_queue.jsonl`
- force `status: candidate`
- force live action flags false if included
- reject candidates that imply automatic posting, selling, outreach, payment, scraping, account login, fake proof, or fake engagement
- record invalid candidate lines in `parse_warnings.json`

## Step 8: Zero-State Smoke

Run a smoke using the existing sample tracker only:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task weekly_money_review --input 14_context/money_workflows/experiment_tracker.jsonl --max-chars 25000
```

Verify:

- `05_logs/money_reviews/<run_id>/` exists
- all required artifacts exist
- `run_summary.json` says tracker and queue were not mutated
- missing future files show warnings, not failure
- no live action was taken

## Step 9: Static Validation

Run:

```powershell
python -m py_compile 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py
python -m py_compile 03_scripts/money_workflow_new_experiment.py
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json
git diff --check
```

If dashboard files are touched in a later milestone, run Node checks too. N+3.29 should not require dashboard edits.

## Step 10: Update State Docs

If implementation happens, update:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- optionally `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py`

Only update wait/resume if adding a concrete seed.

## Step 11: Stage Intentional Files Only

Likely stage:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- new `05_logs/money_reviews/<run_id>/` smoke artifacts if the milestone wants to keep them
- state/log docs
- optional wait/resume seed

Do not stage:

- unrelated dirty files
- `.claude/skills/`
- CV docs
- `output/`
- third-party files
- prompt scratch files
- old local brain logs
- N+3.18 files unless the milestone explicitly finishes them

Check:

```powershell
git diff --cached --name-status
git diff --cached --check
```

## Step 12: Commit And Push

Commit:

```text
feat/ghoti milestone N+3.29 — add weekly money review artifact generator
```

Push:

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
- weekly review artifact generator truth
- generated artifact paths
- decision candidates truth
- zero-state/tolerant parsing truth
- runtime wiring truth
- install/run truth
- live account/action truth
- dirty files intentionally left unstaged
- next milestone recommendation

## Recommended Next Future Milestone

After N+3.29:

```text
N+3.30 - Weekly Review Dashboard Reads Generated Artifacts
```

That milestone should connect the read-only dashboard card to the generated `05_logs/money_reviews/<run_id>/` artifacts without adding mutation buttons or live actions.
