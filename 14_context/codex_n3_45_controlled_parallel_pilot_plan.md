# N+3.45 Controlled Parallel Pilot Plan

Status: future pilot plan.
Date: 2026-05-05

## Pilot Goal

Run two simultaneous lanes without touching the same files. The pilot proves branch-per-agent, lock declaration, status beacons, validation, and one-branch-at-a-time merge.

No live actions. No external tools. No account actions. No posting, sending, selling, paying, scraping, applying to jobs, entering giveaways, or installing anything.

## Lane A - Claude Code Implementation

Task: Agent Lane Dashboard Read Card.

Branch:

```text
feat/ghoti-agent-claude-n3-45-agent-lane-dashboard
```

Allowed paths:

- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/index.html`
- `14_context/agent_lane_dashboard_n3_45.md`

Forbidden paths unless Claude is explicitly designated state-doc owner:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `14_context/compact_memory/`
- `14_context/obsidian_vault/`

Suggested lock dry-run:

```powershell
python 03_scripts/agent_lane_status.py --new-lock --agent-id claude_n3_45a --lane-type claude_code_impl --task-slug agent-lane-dashboard-read-card --branch feat/ghoti-agent-claude-n3-45-agent-lane-dashboard --locked-file 01_projects/dashboard_mvp/server.js --locked-file 01_projects/dashboard_mvp/public/app.js --locked-file 01_projects/dashboard_mvp/public/index.html --locked-file 14_context/agent_lane_dashboard_n3_45.md --dry-run
```

Suggested status dry-run:

```powershell
python 03_scripts/agent_lane_status.py --new-status --agent-id claude_n3_45a --lane-type claude_code_impl --task-slug agent-lane-dashboard-read-card --branch feat/ghoti-agent-claude-n3-45-agent-lane-dashboard --current-state dry_run --dry-run
```

Validation:

- `python 03_scripts/agent_lane_status.py --check`
- `node --check 01_projects/dashboard_mvp/server.js`
- `node --check 01_projects/dashboard_mvp/public/app.js`
- `git diff --check`

## Lane B - Codex Audit

Task: External Tool Routing Source-Check Pack.

Branch:

```text
audit/ghoti-agent-codex-n3-45-external-tool-routing
```

Allowed paths:

- `14_context/codex_n3_45_*.md`

Forbidden paths:

- dashboard files
- runtime scripts
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `14_context/compact_memory/`
- `14_context/obsidian_vault/`

Suggested lock dry-run:

```powershell
python 03_scripts/agent_lane_status.py --new-lock --agent-id codex_n3_45b --lane-type codex_audit --task-slug external-tool-routing-source-check --branch audit/ghoti-agent-codex-n3-45-external-tool-routing --locked-file 14_context/codex_n3_45_external_tool_routing_source_check.md --locked-file 14_context/codex_n3_45_tool_integration_risk_gate.md --dry-run
```

Suggested status dry-run:

```powershell
python 03_scripts/agent_lane_status.py --new-status --agent-id codex_n3_45b --lane-type codex_audit --task-slug external-tool-routing-source-check --branch audit/ghoti-agent-codex-n3-45-external-tool-routing --current-state dry_run --dry-run
```

Validation:

- `python 03_scripts/agent_lane_status.py --check`
- `git diff --check`
- targeted doc diff check for N+3.45 Codex docs

## Optional Lane C - Gemma Local Worker

Task: compact summary draft only.

Branch:

```text
docs/ghoti-agent-gemma-n3-45-compact-summary-draft
```

Allowed paths:

- `05_logs/local_brain_runs/`
- draft artifact only

Forbidden paths:

- state docs
- runtime files
- dashboard files
- account/live/external actions
- canonical compact memory unless a human explicitly promotes the draft

Suggested dry-run status:

```powershell
python 03_scripts/agent_lane_status.py --new-status --agent-id gemma_n3_45c --lane-type gemma_local_worker --task-slug compact-summary-draft --branch docs/ghoti-agent-gemma-n3-45-compact-summary-draft --current-state dry_run --dry-run
```

## Merge Order

1. Merge Claude lane only after node checks and lane checks pass.
2. Merge Codex lane only after doc checks pass and no overlap exists.
3. If Gemma lane is used, review draft manually before any promotion.
4. Update `current_state.md` and `next_actions.md` only from one designated state-owner lane after both merges.

## Stop Conditions

- Any branch divergence.
- Any shared-file overlap.
- Any attempt to edit state docs from multiple lanes.
- Any live/external/account/money/public action requirement.
- Any generated artifact with secrets or credentials.
- Any failed validation that the lane cannot explain and fix safely.

## Pilot Success Definition

- Two branches complete without overlapping write sets.
- Locks/status records were dry-run or applied intentionally.
- Validation passed per lane.
- Merge happened one branch at a time.
- No live actions occurred.
