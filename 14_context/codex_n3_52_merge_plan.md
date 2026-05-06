# Codex N+3.52 - Merge Plan

## Verdict

`CONDITIONAL PASS - FIX BEFORE MERGE`

N+3.50A is useful and mostly local-safe, but it should not be merged directly until it is pushed and the hard gaps are either fixed or consciously accepted.

## First Preservation Command

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
git switch feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma
git status --short
git push origin feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma
```

If push is denied by a permission gate, the operator must approve or push manually. Do not reset the branch.

## Recommended Path

1. Push N+3.50A branch for preservation.
2. Run N+3.51A hardening from the N+3.50A branch.
3. Audit N+3.51A with Codex.
4. Merge only after hardening validations pass.

## If Operator Chooses To Merge N+3.50A As-Is

Use only if the limitations are accepted:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git merge --no-ff feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma -m "merge(ghoti): land N+3.50A bridge dashboard Ruflo Gemma gates"
python -c "import ast, pathlib; files=['03_scripts/ghoti_dashboard.py','03_scripts/ruflo_install_gate.py','03_scripts/gemma_compact_memory_worker.py','03_scripts/prompt_bus.py','03_scripts/local_worker_router.py']; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8')) for f in files]; print('AST OK')"
python 03_scripts/ghoti_dashboard.py --json
python 03_scripts/ruflo_install_gate.py --status
python 03_scripts/ruflo_install_gate.py --install --dry-run
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/gemma_compact_memory_worker.py --compress --input 14_context/compact_memory/project_state.md --max-chars 2500 --dry-run
python 03_scripts/prompt_bus.py --write-context-pack --target all --title "post-merge-smoke" --include-status --include-memory --include-next-actions --dry-run
python 03_scripts/agent_lane_status.py --check
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
git diff --check
git push origin feat/ghoti-visible-operator-stack
```

## Preferred Hardening Start

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
git switch feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma
git push origin feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma
git switch -c feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening
```

Then implement `14_context/codex_n3_52_next_claude_implementation_brief.md`.

## Rollback Notes

- Do not run `git reset --hard` without explicit human approval.
- If merge conflicts occur before commit, inspect and use `git merge --abort` only after confirming no unrelated work will be lost.
- If a bad merge is pushed, create a revert commit instead of rewriting shared history.

## Blockers To Clear

- Remote Claude N+3.50A branch is missing.
- npm is not available in PATH.
- Ruflo is not installed.
- Gemma model is not available in current validation.
- Prompt bus canonical overwrite needs stronger confirmation.
- Dashboard should label bridge state as manual/partial.
