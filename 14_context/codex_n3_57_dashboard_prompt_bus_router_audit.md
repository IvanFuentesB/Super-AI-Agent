# Codex N+3.57 - Dashboard, Prompt Bus, And Router Audit

## Verdict

PENDING TARGET BRANCH.

Dashboard, prompt-bus, and router clean-pass fixes cannot be audited because the Claude N+3.56-FIX target branch is not available remotely.

## Dashboard Requirements

Once the branch exists, Codex must validate:

- `python 03_scripts/ghoti_dashboard.py --status`
- `python 03_scripts/ghoti_dashboard.py --json`
- `python 03_scripts/ghoti_dashboard.py --card --dry-run`
- `node --check 01_projects/dashboard_mvp/server.js`
- `node --check 01_projects/dashboard_mvp/public/app.js`

Expected truth:

- CC/Codex automatic false.
- Ruflo runtime wiring false.
- Human approval required true.
- Bridge helper exists.
- Course helper exists.
- Obsidian detection uses unified truth.
- `/api/ghoti/local-orchestrator/status` is read-only and does not run installs/actions.

## Prompt Bus Requirements

Once the branch exists, Codex must validate:

```powershell
python 03_scripts/prompt_bus.py --status-json
python 03_scripts/prompt_bus.py --write-context-pack --target all --title codex-audit-smoke --include-status --include-memory --include-next-actions --dry-run
python 03_scripts/prompt_bus.py --write-context-pack --target claude --title should-refuse --include-status --apply
```

Expected truth:

- Context packs are useful and file-based.
- Canonical overwrite requires explicit `--allow-canonical-overwrite`.
- The refusal test must not overwrite `14_context/ghoti_current_prompt.md`.

## Router Requirements

Once the branch exists, Codex must validate:

- bridge handoff task routes to `cc_codex_bridge_worker` or equivalent bridge helper.
- course task routes to `course_certificate_assistant`.
- Ruflo task routes to `ruflo_orchestrator_candidate`.
- Gemma task routes to `gemma_local_worker`.
- Python automation routes to `python_automation_worker`.

## Current Status

N+3.56 found the dashboard route read-only and prompt-bus overwrite protection safe by source inspection, but router bridge-handoff behavior still routed to Codex audit instead of the bridge helper. N+3.57 cannot verify the fix until the branch is pushed.
