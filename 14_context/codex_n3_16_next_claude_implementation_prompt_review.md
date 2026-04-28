# Codex N+3.16 Next Claude Implementation Prompt Review

Status: codex_planning_audit_only / next_claude_scope_review / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Recommended Next Claude Code Milestone

N+3.16 Claude - Money Experiment Tracker + Gemma Video/Context Intake Templates

## Why This Milestone

This is the smallest practical implementation that turns the N+3.15 and N+3.16 money plans into usable local assets. It does not require Paperclip, OpenClaw, n8n, Docker, CUA, live accounts, scraping, paid tools, or posting. It also uses the existing local Gemma direction without making Gemma autonomous.

## Claude Code Should Read First

- `14_context/codex_n3_15_money_workflow_backlog.md`
- `14_context/codex_n3_15_video_to_business_system_plan.md`
- `14_context/codex_n3_15_digital_product_and_whop_plan.md`
- `14_context/codex_n3_15_content_factory_tools_and_routing.md`
- `14_context/codex_n3_16_numbers_game_money_os.md`
- `14_context/codex_n3_16_money_experiment_tracker_spec.md`
- `14_context/codex_n3_16_distribution_and_exposure_plan.md`
- `14_context/codex_n3_16_digital_product_shot_library.md`
- `14_context/codex_n3_16_video_to_money_pipeline.md`

## Implementation Scope

Claude should later implement:

- `14_context/money_workflows/README.md`
- `14_context/money_workflows/templates/experiment_tracker.example.jsonl`
- `14_context/money_workflows/templates/video_to_money_intake_template.md`
- `14_context/money_workflows/templates/digital_product_idea_card_template.md`
- `14_context/money_workflows/templates/content_batch_template.md`
- `14_context/money_workflows/templates/distribution_checklist.md`
- `14_context/money_workflows/templates/approval_checklist.md`
- `14_context/money_workflows/templates/risk_checklist.md`

Optional only if safe and small:

- local script or CLI that creates a new blank workflow folder from templates
- preview-only integration with Gemma compression artifacts
- update local brain routing policy to include money workflow draft classes

## Constraints

- No posting.
- No outreach.
- No account actions.
- No paid tools.
- No scraping.
- No live platform automation.
- No Paperclip/OpenClaw/n8n install or runtime wiring.
- No CUA/browser action.
- No Gemma autonomous execution.
- No model output execution.

## Repo Discipline

Claude Code should:

- preserve repo-root boundary
- not touch unrelated dirty files
- not stage `.claude/skills/`
- not stage CV docs
- not stage `output/`
- not stage prompt scratch files
- not edit `14_context/ghoti_current_prompt.md`
- stage only intentional milestone files

## Validation Checklist

Claude should run:

- `git status --short`
- `git diff --check`
- targeted `git diff --check -- 14_context/money_workflows`
- JSON validation for `.jsonl` examples if practical
- `git diff --cached --check`
- `git diff --cached --name-status`

If a script is added:

- run its syntax check
- run it only on synthetic/local placeholder data
- verify it does not post, send, scrape, spend, or use accounts

## Commit and Push

Recommended commit:

```text
docs/money milestone N+3.16 — add money workflow tracker templates
```

Push only after validation passes:

```text
git push origin feat/ghoti-visible-operator-stack
```

## Report Requirements

Claude should report:

- branch
- starting HEAD
- new commit hash
- pushed yes/no
- files changed
- validation results
- whether any local Gemma step ran
- whether runtime wiring occurred
- whether any install/run/post/account action occurred
- dirty files intentionally left unstaged
- next recommended milestone

## Exact Next Step

Implement the local money workflow template folder and tracker examples first. Defer dashboards, automation, Paperclip, OpenClaw, n8n, live posting, outreach, and paid tools until the user has approved a specific experiment and the tracker proves the workflow is useful.
