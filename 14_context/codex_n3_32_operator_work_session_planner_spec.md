# Codex N+3.32 Operator Work Session Planner Spec

Status: codex_planning_only / operator_work_session_planner / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack

## Purpose

Design a future local-only planner that turns manual decision queue items into a human-reviewed local work session plan.

The planner should answer: "What can the operator safely work on locally in the next session?" It must not execute tasks itself.

## Future Command Concept

Possible future helper:

```powershell
python 03_scripts/operator_work_session_plan.py --queue 14_context/money_workflows/manual_decision_queue.jsonl --dry-run
```

Possible future local brain task after the queue is stable:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task operator_work_session_plan --input 14_context/money_workflows/manual_decision_queue.jsonl --max-chars 20000
```

First implementation should prefer a deterministic stdlib script. Gemma can be added later only for draft wording, not execution.

## Inputs

Primary input:

```text
14_context/money_workflows/manual_decision_queue.jsonl
```

Optional local context:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/money_workflows/money_os_index.md`
- `14_context/money_workflows/distribution_and_exposure_checklist.md`
- `14_context/money_workflows/experiment_tracker.jsonl`
- latest `05_logs/money_reviews/<run_id>/run_summary.json`
- latest `05_logs/money_reviews/<run_id>/decisions_recommended.jsonl`

All inputs must be repo-local. URLs inside files are text only.

## Outputs

Future artifact directory:

```text
05_logs/operator_work_sessions/<run_id>/
```

Required artifacts:

```text
05_logs/operator_work_sessions/<run_id>/request.json
05_logs/operator_work_sessions/<run_id>/work_session_plan.md
05_logs/operator_work_sessions/<run_id>/work_session_plan.json
05_logs/operator_work_sessions/<run_id>/risk_review.md
05_logs/operator_work_sessions/<run_id>/run_summary.json
```

Optional artifacts:

```text
05_logs/operator_work_sessions/<run_id>/queue_excerpt.jsonl
05_logs/operator_work_sessions/<run_id>/blocked_items.md
05_logs/operator_work_sessions/<run_id>/approval_questions.md
```

## Classification Buckets

Each queue item should be classified into exactly one of:

- `safe_local_work`: can be worked locally without public, account, payment, or external action
- `needs_human_approval`: public/money/account/external action is required before proceeding
- `blocked`: missing files, unclear next step, unresolved risk, or prerequisite not done
- `reject_unsafe`: implies spam, fake proof, scraping abuse, live account action, payment action, or model-output execution

## Required Work Session Plan Sections

`work_session_plan.md` should include:

- session summary
- top 3 local tasks
- why these tasks were chosen
- exact local file or artifact targets
- validation steps
- blocked items
- human approval questions
- risk notes
- what not to do
- next checkpoint

## Top 3 Local Tasks

For each task, include:

- queue item ID
- decision type
- local task title
- next local step
- target files or artifact paths
- estimated effort
- risk level
- validation command or manual check
- explicit "no live action" note

Examples of safe local work:

- draft a content batch markdown file
- draft a product build pack artifact
- update a local checklist
- review a risk note
- record manually collected metrics
- prepare questions for operator approval

## Human Approval Questions

The planner should produce explicit questions when a queue item needs approval:

- "Do you approve creating a public post draft for this product?"
- "Do you approve manually logging into Whop to create a listing draft?"
- "Do you approve using this email list platform account?"

The planner must not answer those questions or act on them.

## Forbidden Behavior

The planner must not:

- execute queue item actions
- append to the queue
- mutate the experiment tracker
- call external APIs
- call Gemma unless explicitly implemented as a local-only future task
- post or schedule content
- send email
- perform outreach
- sell or list products
- process payments
- scrape
- upload files to platforms
- log into accounts
- open browsers for live account work

## Deterministic Planner Recommendation

First version should be deterministic:

- parse queue JSONL
- classify items by status, risk, and approval flags
- rank safe local work first
- write artifacts only
- do not invoke a model

Gemma can later improve wording or produce a more narrative plan, but only from deterministic excerpts and with artifact-only output.

## Run Summary Safety Flags

`run_summary.json` should include:

```json
{
  "read_only_inputs": true,
  "queue_mutated": false,
  "tracker_mutated": false,
  "model_output_executed": false,
  "external_api_used": false,
  "posting_enabled": false,
  "selling_enabled": false,
  "outreach_enabled": false,
  "payment_actions_enabled": false,
  "scraping_enabled": false,
  "live_account_actions_enabled": false,
  "human_approval_required_for_public_actions": true
}
```

## Verdict

The Operator Work Session Planner should help the operator choose the next safe local work block. It should not become a task runner.
