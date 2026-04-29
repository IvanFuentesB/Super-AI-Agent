# Codex N+3.21 Shot Production Data Model

Status: codex_planning_only / content_shot_data_model / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

The shot production model should track every content piece as a measurable experiment. The goal is not to make one perfect post. The goal is to create many ethical shots, connect them to products or experiments, measure feedback, and decide what to scale, iterate, pause, or kill.

## Proposed File

Future implementation can add:

```text
14_context/money_workflows/content_shots.jsonl
```

Each line should be one JSON object. The file should be append-only at first and read-only from the dashboard until explicit approval exists for editing workflows.

## JSONL Fields

Recommended fields:

- `shot_id`
- `created_at`
- `source_experiment_id`
- `workflow_type`
- `product_idea`
- `target_customer`
- `pain_point`
- `platform`
- `format`
- `hook`
- `script_outline`
- `cta`
- `status`
- `approval_required`
- `metrics`
- `repurposed_from`
- `safety`
- `files`
- `notes`

Recommended `metrics` object:

- `impressions`
- `views`
- `clicks`
- `opt_ins`
- `replies`
- `sales`

Recommended `safety` object:

- `claims_checked`
- `no_fake_proof`
- `no_spam`
- `human_approved_before_posting`
- `live_action_taken`

## Status Values

Suggested initial statuses:

- `draft`
- `needs_review`
- `approved_to_post`
- `posted_manually`
- `measuring`
- `repurposed`
- `paused`
- `killed`

`approved_to_post` must only be set after explicit operator approval. No script should post just because this status exists.

## Relationship To Experiment Tracker

`content_shots.jsonl` should connect to `experiment_tracker.jsonl` through `source_experiment_id`.

Recommended pattern:

- One money experiment can produce many content shots.
- Each shot can have one platform and one format.
- Metrics from published shots can later roll back into the experiment tracker.
- Dashboard read views can count total shots, shots by platform, shots by status, and shots by experiment.

## Example Draft Record

```json
{"shot_id":"shot_20260429_001","created_at":"2026-04-29T00:00:00Z","source_experiment_id":"exp_video_to_business_system_extractor","workflow_type":"short_form_content","product_idea":"AI Operator Starter Kit","target_customer":"solo builder learning AI workflows","pain_point":"too many AI ideas and no safe execution system","platform":"YouTube Shorts","format":"short_script","hook":"Most people use AI like a chat box. The leverage starts when it becomes an operating system.","script_outline":"Problem, shift, three-step safe workflow, CTA to checklist.","cta":"Download the free AI Operator checklist when available.","status":"draft","approval_required":true,"metrics":{"impressions":0,"views":0,"clicks":0,"opt_ins":0,"replies":0,"sales":0},"repurposed_from":null,"safety":{"claims_checked":true,"no_fake_proof":true,"no_spam":true,"human_approved_before_posting":false,"live_action_taken":false},"files":[],"notes":"Draft only. No live platform action."}
```

## Dashboard Read Model

A future dashboard card can show:

- total shots
- shots by platform
- shots by status
- shots awaiting approval
- shots with missing CTA
- shots without email-list angle
- latest drafted shots
- top shots by views, clicks, opt-ins, or sales after manual metric entry

## Data Quality Risks

- Missing `source_experiment_id` makes it harder to learn from experiments.
- Mixed platform names make counts noisy.
- Metrics may be manually entered and incomplete.
- Public posting status must not imply automation occurred.
- Generated hooks may contain claims that need human review.

## Verdict

Use a simple JSONL content shot model first. It is enough for tracking many shots and connecting content production to the money OS without building a database or live platform automation.
