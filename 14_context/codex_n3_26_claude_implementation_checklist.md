# Codex N+3.26 Claude Implementation Checklist

Status: codex_planning_only / claude_execution_checklist / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Recommended Order

Claude Code should finish or consciously pause N+3.18 first. If the product build pack generator from N+3.24 is not implemented yet, Claude should implement that before building a launch checklist or metrics dashboard, unless the operator explicitly wants templates only.

## Implementation Goal

Add local manual launch review templates and manual metrics intake structures. Optionally add a read-only launch metrics dashboard route/card after schemas and sample data exist.

No automatic launch, posting, selling, payment, outreach, app-store submission, account action, scraping, or live metrics fetch is allowed.

## Suggested Implementation Sequence

1. Finish or pause N+3.18.
2. Optionally implement N+3.24 `product_build_pack`.
3. Add local manual launch checklist template.
4. Add product metrics JSONL schema/sample if approved.
5. Add read-only dashboard route/card for launch metrics if approved.
6. Update wait/resume and state docs only if implementation happens.
7. Validate.
8. Stage intentional files only.
9. Commit and push.

## Likely Files To Create Or Modify Later

Templates and schemas:

- `14_context/money_workflows/manual_launch_approval_checklist_template.md`
- `14_context/money_workflows/product_metrics.schema.json`
- `14_context/money_workflows/product_metrics.example.jsonl`

Dashboard, only if implementing the read-only view:

- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/styles.css` only if needed

State/log docs, only if implementation happens:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` only if adding a concise seed

## Files To Avoid

- unrelated dirty N+3.18 implementation files unless intentionally completing N+3.18
- third-party repo contents
- `.claude/skills/`
- prompt scratch files
- CV files
- `output/`
- Whop/Gumroad/Stripe/Shopify/email/social credentials
- live account files

## Validation Commands

```powershell
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json
python -m json.tool 14_context/money_workflows/product_metrics.schema.json
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
git diff --check
git status --short
```

If product metrics JSONL is added:

```powershell
python -c "import json; [json.loads(line) for line in open('14_context/money_workflows/product_metrics.example.jsonl', encoding='utf-8') if line.strip()]; print('product metrics jsonl ok')"
```

## Stage / Commit / Push

Stage only intentional N+3.26 files.

Recommended commit:

```text
feat/ghoti milestone N+3.26 — add manual launch checklist and metrics intake
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
- launch checklist truth
- metrics intake truth
- dashboard route/card truth
- no-live-action truth
- dirty files intentionally left unstaged
- next recommended milestone

## Next Future Milestone

After N+3.26, a strong next milestone is:

```text
N+3.27 — Weekly Money OS Review Dashboard And Manual Decision Queue
```

That milestone should summarize product, content, launch, and metrics state into a weekly operator review without taking live action.
