# Codex N+3.64 Content Workflow Safety Audit

## Verdict

Content workflow verdict: NOT AUDITED

Reason: the requested remote target branch is missing.

Codex cannot claim the content/money workflow is planning-only or safe until `03_scripts/content_money_workflow.py` exists on the target branch and passes the dry-run validation suite.

## Required Planning-Only Boundary

The content runway workflow may support:

- niche planning
- platform planning
- shot lists
- scripting outlines
- monetization runway notes
- safety gates
- local-only dry-run reports
- no-post content calendars
- no-upload production checklists

It must not:

- post or upload to YouTube/TikTok/Instagram/etc.
- send messages or outreach
- scrape platforms
- use social accounts
- create accounts
- call content-generation APIs
- run MoneyPrinter
- launch browser automation
- make payments
- trade or transact
- bypass platform rules

## Required Future Commands

Run these only after the target branch exists and has been no-commit merged into a clean audit worktree:

```powershell
python 03_scripts/content_money_workflow.py --status
python 03_scripts/content_money_workflow.py --plan --niche "engineering explainer shorts" --platform youtube_shorts --dry-run
python 03_scripts/content_money_workflow.py --shot-list --topic "why PID controllers overshoot" --count 10 --dry-run
python 03_scripts/content_money_workflow.py --workflow-check --dry-run
```

Required safe outcome:

- Every command is dry-run or read-only.
- No files are written unless explicitly documented and approval-gated.
- No external service is called.
- No live publishing/upload/send action exists.
- Workflow output includes human approval gates.
- MoneyPrinter is treated as a future tool candidate, not a runtime dependency.

## Router Expectations

Future router checks should map:

- `evaluate OpenFang repo for Ghoti` -> `external_repo_intake_worker`
- `use MoneyPrinter by DevBySami for YouTube Shorts workflow` -> `external_repo_intake_worker` or `content_money_workflow_worker`
- `create faceless shorts content pipeline` -> `content_money_workflow_worker`
- `use Karpathy LLM Council to compare model answers` -> `llm_council_worker`
- `create merge plan for audited branch` -> `merge_assistant_worker`
- `compress memory with local gemma` -> `gemma_local_worker`

Either MoneyPrinter route is acceptable if the explanation is explicit:

- `external_repo_intake_worker` is acceptable when evaluating the repo/tool source and risk.
- `content_money_workflow_worker` is acceptable when planning a no-post, no-upload content workflow.
