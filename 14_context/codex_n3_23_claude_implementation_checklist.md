# Codex N+3.23 Claude Implementation Checklist

Status: codex_planning_only / claude_execution_checklist / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Recommended Order

Claude Code should finish or consciously pause N+3.18 first. The video-to-money runner and experiment scoring implementation remains dirty/unfinished and should not be accidentally mixed into a dashboard commit unless Claude is intentionally completing it.

## Implementation Goal

Add a read-only product draft dashboard route and card for the future `product_drafts.jsonl` queue.

No publish, upload, payment, listing, outreach, email, posting, app-store, or live account action is allowed.

## Implementation Scope

If approved later, Claude Code can:

1. Add `14_context/money_workflows/product_drafts.schema.json`.
2. Add sample `14_context/money_workflows/product_drafts.jsonl` only if the operator approves sample data.
3. Add backend route `GET /api/ghoti/money/product-drafts/summary`.
4. Add a read-only dashboard card named `Money OS — Product Drafts`.
5. Add robust JSONL parser logic.
6. Add parse error and missing field warnings.
7. Update state/log docs.
8. Optionally add wait/resume seed if useful.

## Likely Files To Modify Later

- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/styles.css` only if needed
- `14_context/money_workflows/product_drafts.schema.json`
- `14_context/money_workflows/product_drafts.jsonl` only if sample data is approved
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` only if adding a concise seed

## Files To Avoid

- unrelated dirty N+3.18 implementation files unless finishing N+3.18
- third-party repo contents
- `.claude/skills/`
- prompt scratch files
- CV files
- `output/`
- live account credentials
- Whop/Gumroad/Stripe/Shopify/email/social account files

## Backend Checklist

- [ ] Define repo-relative product draft path.
- [ ] Read `product_drafts.jsonl` only if present.
- [ ] Return zero-state if missing.
- [ ] Parse JSONL line-by-line.
- [ ] Count malformed lines and keep capped samples.
- [ ] Compute total drafts.
- [ ] Compute by status.
- [ ] Compute by workflow/source.
- [ ] Compute by score bucket.
- [ ] Compute approval queue counts.
- [ ] Compute approval-required count.
- [ ] Compute distribution/email/fulfillment readiness.
- [ ] Collect risk flag counts.
- [ ] Return latest 10 drafts.
- [ ] Return top 5 scored drafts.
- [ ] Never mutate JSONL.
- [ ] Never call external APIs.

## Frontend Checklist

- [ ] Fetch `/api/ghoti/money/product-drafts/summary`.
- [ ] Add `Money OS — Product Drafts` read-only card.
- [ ] Show total drafts and approval count.
- [ ] Show A/B/C/D or unscored buckets.
- [ ] Show latest drafts.
- [ ] Show top scoring drafts.
- [ ] Show warnings for missing fields and parse errors.
- [ ] Show distribution, email-list, fulfillment readiness.
- [ ] Show safety label.
- [ ] Add refresh only.
- [ ] Do not add approve/reject/publish/delete buttons.

## Validation Commands

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json
python -m json.tool 14_context/money_workflows/product_drafts.schema.json
git diff --check
git status --short
```

If `product_drafts.jsonl` is added:

```powershell
python -c "import json; [json.loads(line) for line in open('14_context/money_workflows/product_drafts.jsonl', encoding='utf-8') if line.strip()]; print('product drafts jsonl ok')"
```

## Stage / Commit / Push

Stage only intentional N+3.23 files.

Recommended commit:

```text
feat/ghoti milestone N+3.23 — add product draft read view and approval queue
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
- product draft route truth
- dashboard card truth
- approval queue truth
- live action truth
- dirty files intentionally left unstaged
- next recommended milestone

## Next Future Milestone

After N+3.23, a strong next planning target is:

```text
N+3.24 — Manual Product Build Pack Generator
```

That milestone should generate local product folders and downloadable draft assets only. It should still avoid live store, payment, email, and social account actions.
