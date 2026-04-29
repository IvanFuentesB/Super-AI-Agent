# Codex N+3.22 Claude Implementation Checklist

Status: codex_planning_only / claude_execution_checklist / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Recommended Order

Claude Code should finish or consciously pause N+3.18 before starting N+3.22. N+3.18 still owns the dirty video-to-money runner and experiment scoring implementation. N+3.22 should not accidentally stage that partial work unless Claude is intentionally finishing it.

## Implementation Goal

Add a local Gemma-powered `digital_product_draft` task that turns one repo-local product brief into draft-only product, listing, pricing, lead magnet, fulfillment, and claims-review artifacts.

No store action, payment action, upload, account action, email send, public post, or live claim publication is allowed.

## Files Claude May Need To Create Or Edit Later

Likely implementation files:

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `14_context/money_workflows/product_draft_input_n3_22.md`
- `14_context/money_workflows/product_drafts.example.jsonl`
- `14_context/money_workflows/product_drafts.schema.json`
- `14_context/digital_product_draft_pipeline_n3_22.md`
- `14_context/product_scoring_model_n3_22.md`
- `14_context/product_fulfillment_plan_n3_22.md`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` only if adding a concise seed

Artifact output directory:

- `05_logs/product_drafts/<run_id>/`

## Files Claude Should Avoid

- dashboard implementation files unless the milestone changes
- third-party repo contents
- `.claude/skills/`
- prompt scratch files
- CV files
- `output/`
- Whop, Gumroad, Stripe, Shopify, email, or payment credentials
- Paperclip/OpenClaw/n8n/Unity-MCP/Mythos runtime files

## Required Behavior

The `digital_product_draft` task should:

1. Accept repo-local `.md`, `.txt`, or `.json` input only.
2. Enforce repo-root-only path safety.
3. Enforce max input characters.
4. Use local Gemma/Ollama only if available.
5. Produce artifacts under `05_logs/product_drafts/<run_id>/`.
6. Write `request.json`, source excerpt, raw response, split markdown artifacts, and `run_summary.json`.
7. Include product positioning, name ideas, headline options, offer stack, MVP deliverables, pricing ladder, Whop listing draft, Gumroad listing draft, landing page draft, lead magnet, FAQ, fulfillment checklist, risk review, and next 10 actions.
8. Never execute model output.
9. Never publish, list, upload, price, sell, send email, scrape, browse, or use live accounts.
10. Require human approval for every public, store, platform, payment, or account action.

## Suggested Smoke

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task digital_product_draft --input 14_context/money_workflows/product_draft_input_n3_22.md --max-chars 20000
```

After the smoke, inspect:

- `05_logs/product_drafts/<run_id>/request.json`
- `05_logs/product_drafts/<run_id>/response.txt`
- `05_logs/product_drafts/<run_id>/whop_listing_draft.md`
- `05_logs/product_drafts/<run_id>/gumroad_listing_draft.md`
- `05_logs/product_drafts/<run_id>/risk_claims_review.md`
- `05_logs/product_drafts/<run_id>/run_summary.json`

## Validation Commands

```powershell
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py', encoding='utf-8').read()); print('LOCAL ROUTER AST OK')"
python -c "import ast; ast.parse(open('03_scripts/money_workflow_new_experiment.py', encoding='utf-8').read()); print('MONEY SCRIPT AST OK')"
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json
git diff --check
git status --short
```

If product draft schema is added:

```powershell
python -m json.tool 14_context/money_workflows/product_drafts.schema.json
```

If product draft JSONL is added, validate it with a line-by-line JSON parse.

## Stage / Commit / Push

Stage only intentional N+3.22 implementation files. Do not stage unrelated dirty files from N+3.18 unless the same commit explicitly completes that milestone too.

Recommended commit:

```text
feat/ghoti milestone N+3.22 — add Gemma digital product draft pipeline
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
- Gemma smoke path
- product draft artifact truth
- listing/payment/live-account truth
- runtime wiring truth
- dirty files intentionally left unstaged
- next recommended milestone

## Next Future Milestone

After N+3.22, a strong next milestone is:

```text
N+3.23 — Product Draft Read View + Approval Queue Spec
```

This should still be read-only and approval-gated. Live Whop, Gumroad, Stripe, email, or social actions should require a separate exact operator approval.
