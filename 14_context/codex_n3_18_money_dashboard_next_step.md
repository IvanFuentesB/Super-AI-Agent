# Codex N+3.18 Money Dashboard Next Step

Status: codex_followup_plan / dashboard_read_only_next / not_runtime_wired

## Recommended Next Milestone

After Claude completes N+3.18, the next milestone should be:

`N+3.19 - Money Workflow Dashboard Read View + Shot Counter`

This milestone should make the money workflow visible without adding live posting, selling, scraping, outreach, payment, account automation, or external tool wiring.

## Why This Comes Next

Ghoti's money workflow is a numbers game. The operator needs to see:

- how many shots exist
- which shots are promising
- which shots have distribution plans
- which shots need approval
- whether the email-list angle is present
- which experiments should be scaled, iterated, paused, or killed

The dashboard should reduce babysitting by making the queue legible, but it should not execute any public action.

## Read-Only Dashboard Data

The N+3.19 dashboard read view should show:

| Field | Purpose |
| --- | --- |
| Total shots | Count all experiment records |
| Shots by workflow type | Show mix across prompt packs, video-to-money, content, Whop, games, etc. |
| A/B/C/D score buckets | Show priority distribution |
| Top experiments | List highest-score shots first |
| Distribution channels | Show which channels each shot plans to use |
| Exposure checklist status | Show whether each experiment has distribution coverage |
| Email-list angle present | Show yes/no for owned-audience leverage |
| `approval_required` | Show whether public or money-facing action needs human approval |
| Status | planned, drafted, tested, published manually, scaled, iterated, paused, killed |

## Suggested Read Model

Claude can implement this as a repo-local read model first:

- Input: `14_context/money_workflows/experiment_tracker.jsonl`
- Optional input: recent `05_logs/money_runs/<run_id>/run_summary.json` files
- Output route or CLI summary: read-only only
- No writes except optional generated local summary artifact if explicitly scoped

Suggested dashboard fields:

- `ok`
- `total_experiments`
- `by_workflow_type`
- `by_priority_bucket`
- `top_experiments`
- `channels`
- `approval_required_count`
- `email_list_angle_count`
- `latest_money_run`
- `runtime_wiring_truth: read_only`

## Safety Rules

N+3.19 must remain read-only:

- No live posting.
- No outreach.
- No scraping.
- No YouTube downloading.
- No payment/selling/account/app-store actions.
- No live accounts.
- No autonomous money actions.
- No Paperclip/OpenClaw/n8n/Unity-MCP/Mythos/Dolphin/CUDA install or runtime wiring.
- No model output execution.

## Done Definition

N+3.19 is done when the operator can open or query a read-only view and answer:

- How many money workflow shots exist?
- Which shots are highest priority?
- Which shots have email-list leverage?
- Which shots need human approval?
- Which distribution lanes are being used?
- What should be drafted next?

Public actions still require explicit human approval.
