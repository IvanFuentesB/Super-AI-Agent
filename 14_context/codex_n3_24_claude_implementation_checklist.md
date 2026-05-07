# Codex N+3.24 Claude Implementation Checklist

Status: codex_planning_only / claude_execution_checklist / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Recommended Order

Claude Code should finish or consciously pause N+3.18 before starting N+3.24. The dirty video-to-money runner and experiment scoring work must not be accidentally staged in a product build pack commit unless Claude is intentionally finishing it.

## Implementation Goal

Optionally implement a local Gemma-powered `product_build_pack` task that turns one approved product draft or notes file into local artifact files under `05_logs/product_build_packs/<run_id>/`.

No publishing, uploading, selling, payment, account login, outreach, posting, scraping, or customer data use is allowed.

## Likely Files To Modify Later

- `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py`
- `14_context/money_workflows/product_build_pack_input_n3_24.md`
- `14_context/money_workflows/product_build_packs.schema.json` only if approved
- `14_context/product_build_pack_generator_n3_24.md`
- `14_context/product_build_pack_safety_review_n3_24.md`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` only if adding a concise seed

Artifact output directory:

- `05_logs/product_build_packs/<run_id>/`

## Required Artifacts

The task should write:

- `product_brief.md`
- `customer_avatar.md`
- `offer_stack.md`
- `mvp_deliverables.md`
- `build_steps.md`
- `product_folder_structure.md`
- `sales_page_draft.md`
- `whop_listing_draft.md`
- `gumroad_listing_draft.md`
- `lead_magnet_draft.md`
- `email_capture_plan.md`
- `content_launch_pack.md`
- `risk_review.md`
- `operator_approval_checklist.md`
- `run_summary.json`

## Required Safety Behavior

- Enforce repo-root-only input paths.
- Enforce allowed text-like extensions.
- Enforce max input characters.
- Use local Gemma only if available.
- Write artifacts only.
- Never execute model output.
- Never auto-create marketplace folders outside approved local paths.
- Never publish or upload.
- Never use Whop/Gumroad/Stripe/social/email accounts.
- Never use payment data.
- Never use customer data.
- Never send outreach.
- Never scrape.

## Suggested Smoke

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py --task product_build_pack --input 14_context/money_workflows/product_build_pack_input_n3_24.md --max-chars 20000
```

Inspect:

- `05_logs/product_build_packs/<run_id>/product_brief.md`
- `05_logs/product_build_packs/<run_id>/build_steps.md`
- `05_logs/product_build_packs/<run_id>/operator_approval_checklist.md`
- `05_logs/product_build_packs/<run_id>/risk_review.md`
- `05_logs/product_build_packs/<run_id>/run_summary.json`

## Validation Commands

```powershell
python -c "import ast; ast.parse(open('01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py', encoding='utf-8').read()); print('LOCAL ROUTER AST OK')"
python -m py_compile 03_scripts/money_workflow_new_experiment.py
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json
git diff --check
git status --short
```

If `product_build_packs.schema.json` is added:

```powershell
python -m json.tool 14_context/money_workflows/product_build_packs.schema.json
```

If `product_build_packs.jsonl` is added:

```powershell
python -c "import json; [json.loads(line) for line in open('14_context/money_workflows/product_build_packs.jsonl', encoding='utf-8') if line.strip()]; print('product build packs jsonl ok')"
```

## Stage / Commit / Push

Stage only intentional N+3.24 files. Do not stage unrelated dirty files.

Recommended commit:

```text
feat/ghoti milestone N+3.24 — add manual product build pack generator
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
- product build pack artifact truth
- safety/live-action truth
- runtime wiring truth
- install/run truth
- dirty files intentionally left unstaged
- next recommended milestone

## Next Future Milestone

After N+3.24, a strong next milestone is:

```text
N+3.25 — Product Pack Read View + Build Status Dashboard Spec
```

Keep it read-only first. Do not add live commerce actions.
