# Codex N+3.53 - Merge Plan

## Merge Verdict

`PENDING TARGET BRANCH`

Do not merge N+3.51A because no remote implementation branch exists. N+3.50A may be preserved and reviewed, but it is not enough for the expected 88-92% target.

## If N+3.51A Branch Is Pushed Later

Expected branch:

```powershell
feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening
```

or versioned suffix:

```powershell
feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening-v2
feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening-v3
feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening-v4
```

## Merge Commands If Codex Later Gives PASS

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
git fetch origin
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git merge --no-ff origin/feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening -m "merge(ghoti): land N+3.51 bridge hardening"
```

## Post-Merge Validation

```powershell
python -c "import ast, pathlib; files=['03_scripts/ruflo_install_gate.py','03_scripts/gemma_compact_memory_worker.py','03_scripts/cc_codex_bridge.py','03_scripts/course_certificate_assistant.py','03_scripts/prompt_bus.py','03_scripts/ghoti_dashboard.py','03_scripts/local_worker_router.py','03_scripts/agent_lane_status.py']; existing=[f for f in files if pathlib.Path(f).exists()]; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8')) for f in existing]; print('AST OK:', existing)"
python 03_scripts/ruflo_install_gate.py --status
python 03_scripts/ruflo_install_gate.py --install --dry-run
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/gemma_compact_memory_worker.py --compress --input 14_context/compact_memory/project_state.md --dry-run
python 03_scripts/cc_codex_bridge.py --status
python 03_scripts/cc_codex_bridge.py --write-pair --title post-merge-smoke --dry-run
python 03_scripts/course_certificate_assistant.py --policy
python 03_scripts/course_certificate_assistant.py --plan --course-name "Python Automation Foundations" --dry-run
python 03_scripts/prompt_bus.py --status-json
python 03_scripts/ghoti_dashboard.py --json
python 03_scripts/agent_lane_status.py --check
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
powershell -ExecutionPolicy Bypass -File 03_scripts/open_obsidian_vault.ps1 -Check
git diff --check
```

## Push After Merge

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## Rollback-Safe Advice

- If conflicts occur before merge commit, stop and inspect.
- Use `git merge --abort` only if no unrelated work will be lost.
- Do not use `git reset --hard` without explicit human approval.
- If a bad merge is already pushed, revert with a new commit instead of rewriting history.

## Current Operator Action

Do not merge yet. Ask Claude to produce and push N+3.51A first, then run a fresh Codex PASS/FAIL audit.
