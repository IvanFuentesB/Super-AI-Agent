# Codex N+3.25 Claude Implementation Checklist

Status: codex_planning_only / claude_execution_checklist / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Recommended Order

Claude Code should finish or consciously pause N+3.18 first. Then, if the operator wants product pack visibility, Claude should implement N+3.24 `product_build_pack` before the N+3.25 read view, or add approved sample `product_build_packs.jsonl` data for a read-only zero/smoke route.

## Implementation Goal

Add a read-only product build pack route and dashboard card.

No mutation buttons. No publishing. No uploading. No selling. No payments. No account actions. No outreach. No email sending. No scraping. No live metrics fetching.

## Likely Files To Modify Later

- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/styles.css` only if needed
- `14_context/money_workflows/product_build_packs.schema.json` only if approved
- `14_context/money_workflows/product_build_packs.jsonl` only if sample data is approved
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` only if adding a concise seed

## Backend Checklist

- [ ] Add `GET /api/ghoti/money/product-build-packs/summary`.
- [ ] Read `product_build_packs.jsonl` if present.
- [ ] Return zero-state if missing.
- [ ] Parse JSONL line-by-line.
- [ ] Continue after malformed lines.
- [ ] Count parse errors and capped samples.
- [ ] Compute build status counts.
- [ ] Compute approval status counts.
- [ ] Compute distribution status counts.
- [ ] Compute email-list status counts.
- [ ] Compute risk level counts.
- [ ] Return latest build packs.
- [ ] Return top ready-to-build items.
- [ ] Return blocked items and warnings.
- [ ] Include source file truth and generated timestamp.
- [ ] Do not mutate files.
- [ ] Do not call external APIs.

## Frontend Checklist

- [ ] Add `Money OS — Product Packs` read-only card.
- [ ] Fetch `/api/ghoti/money/product-build-packs/summary`.
- [ ] Show total packs, ready to build, needs approval, built locally.
- [ ] Show status counts.
- [ ] Show latest packs.
- [ ] Show blocked items.
- [ ] Show next manual action.
- [ ] Show zero-state if missing file.
- [ ] Show safety footer.
- [ ] Add refresh only if needed.
- [ ] Do not add approve/reject/publish/upload/delete buttons.

## Validation Commands

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
python -m json.tool 14_context/money_workflows/experiment_tracker.schema.json
git diff --check
git status --short
```

If product build pack schema is added:

```powershell
python -m json.tool 14_context/money_workflows/product_build_packs.schema.json
```

If product build pack JSONL is added:

```powershell
python -c "import json; [json.loads(line) for line in open('14_context/money_workflows/product_build_packs.jsonl', encoding='utf-8') if line.strip()]; print('product build packs jsonl ok')"
```

## Stage / Commit / Push

Stage only intentional N+3.25 files.

Recommended commit:

```text
feat/ghoti milestone N+3.25 — add product pack read view and build status summary
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
- product pack route truth
- dashboard card truth
- read-only/no-live-action truth
- dirty files intentionally left unstaged
- next recommended milestone

## Next Future Milestone

After N+3.25, a strong next milestone is:

```text
N+3.26 — Manual Launch Approval Checklist And Product Metrics Intake Spec
```

That milestone should still be approval-gated and should not automate live launches.
