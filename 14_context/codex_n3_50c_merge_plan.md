# Codex N+3.50C - Merge Plan

Milestone: N+3.50C - Dashboard/Ruflo/Gemma parallel audit lane

Date: 2026-05-06

## Current Branch Truth

- Base branch: `feat/ghoti-visible-operator-stack`
- Base origin HEAD at audit start: `e7e946a26bea677d37d00370590d827f3ec82b3a`
- Expected Claude branch: `feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma`
- Claude branch status at audit start: not found on origin.
- Codex audit branch: `audit/ghoti-agent-codex-n3-50-dashboard-ruflo-gemma-audit`

## Validation Commands For Claude Branch After It Is Pushed

Run after Claude pushes `feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma`:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
git fetch origin
git rev-parse origin/feat/ghoti-visible-operator-stack
git rev-parse origin/feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma
git diff --name-status origin/feat/ghoti-visible-operator-stack..origin/feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma
```

Use a temporary worktree for validation:

```powershell
git worktree add --detach C:\Users\ai_sandbox\Documents\AI_Managed_Only_n3_50a_validate origin/feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only_n3_50a_validate
```

Python validation:

```powershell
python -m py_compile 03_scripts/ghoti_dashboard.py
python -m py_compile 03_scripts/ruflo_install_gate.py
python -m py_compile 03_scripts/gemma_compact_memory_worker.py
python -m py_compile 03_scripts/ghoti_local_orchestrator.py
python -m py_compile 03_scripts/prompt_bus.py
python -m py_compile 03_scripts/local_worker_router.py
```

Node validation:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
```

Config validation:

```powershell
python -m json.tool 23_configs/ruflo_install_gate.example.json
python -m json.tool 23_configs/gemma_compact_memory_worker.example.json
python -m json.tool 23_configs/local_worker_routing.example.json
```

JSONL validation:

```powershell
python - <<'PY'
import json, pathlib
for p in [pathlib.Path("14_context/agent_lanes/active_locks.jsonl"), pathlib.Path("14_context/agent_lanes/lane_status.jsonl")]:
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            json.loads(line)
    print("JSONL OK", p)
PY
```

Smoke commands:

```powershell
python 03_scripts/ghoti_dashboard.py --help
python 03_scripts/ghoti_dashboard.py --status
python 03_scripts/ghoti_dashboard.py --card --dry-run
python 03_scripts/ruflo_install_gate.py --help
python 03_scripts/ruflo_install_gate.py --check
python 03_scripts/ruflo_install_gate.py --install --dry-run
python 03_scripts/gemma_compact_memory_worker.py --help
python 03_scripts/gemma_compact_memory_worker.py --check
python 03_scripts/gemma_compact_memory_worker.py --draft --dry-run
python 03_scripts/ghoti_local_orchestrator.py --status
python 03_scripts/prompt_bus.py --status-json
python 03_scripts/agent_lane_status.py --check
```

Dashboard route validation after merge or in a safe local server context:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
```

Do not start a browser operator, external MCP, or live account session during validation.

## Merge Plan If Claude Passes

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git fetch origin
git merge --no-ff origin/feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma -m "merge(ghoti): land N+3.50 dashboard Ruflo Gemma work"
```

Run the validation commands above, then:

```powershell
git diff --check
git push origin feat/ghoti-visible-operator-stack
```

## Merge Plan For Codex Audit Docs

After Claude branch is merged and pushed:

```powershell
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git merge --no-ff origin/audit/ghoti-agent-codex-n3-50-dashboard-ruflo-gemma-audit -m "merge(ghoti): land N+3.50C dashboard Ruflo Gemma audit"
git diff --check
git push origin feat/ghoti-visible-operator-stack
```

## Rollback If Merge Fails

If merge conflicts occur:

```powershell
git status --short
git merge --abort
```

Do not run `git reset --hard` without explicit human approval.

If validation fails after merge but before push:

- document the exact failing command
- either fix only that issue on a Claude recovery branch or abort if still in merge state
- do not stage unrelated local dirt

## Percentage Estimate

If Claude N+3.50 lands cleanly:

- current: about 73-75%
- after successful merge: about 82-87%

Why: dashboard visibility plus prompt context packs plus Gemma draft compression plus Ruflo install gate would move Ghoti from mostly local scaffolding into an actual supervised local operator workbench.
