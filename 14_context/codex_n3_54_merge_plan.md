# Codex N+3.54 - Merge Plan

## Current Merge Verdict

PENDING TARGET BRANCH. Do not merge N+3.51 yet.

## Why Merge Is Blocked

The remote does not contain:

- `origin/feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening`
- `origin/feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening-v2`
- `origin/feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening-v3`
- `origin/feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening-v4`

Only prior Codex audit branches with `n3-51` were found.

## Required Operator Command Before Re-Audit

Claude or the operator must push the real implementation branch:

```powershell
git push origin feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening
```

If Claude used a fallback branch:

```powershell
git push origin feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening-v2
git push origin feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening-v3
git push origin feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening-v4
```

Push only the actual branch used.

## Merge Commands If Future Audit Passes

Replace `<n3_51_branch>` with the actual audited branch name:

```powershell
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git fetch origin
git merge --no-ff origin/<n3_51_branch> -m "merge(ghoti): land N+3.51 bridge hardening"
```

Run validation after merge:

```powershell
python -c "import ast, pathlib; files=['03_scripts/ruflo_install_gate.py','03_scripts/gemma_compact_memory_worker.py','03_scripts/cc_codex_bridge.py','03_scripts/course_certificate_assistant.py','03_scripts/prompt_bus.py','03_scripts/ghoti_dashboard.py','03_scripts/local_worker_router.py','03_scripts/agent_lane_status.py']; existing=[f for f in files if pathlib.Path(f).exists()]; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8')) for f in existing]; print('AST OK:', existing)"
python 03_scripts/ruflo_install_gate.py --status
python 03_scripts/ruflo_install_gate.py --install --dry-run
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/gemma_compact_memory_worker.py --compress --input 14_context/compact_memory/project_state.md --dry-run
python 03_scripts/cc_codex_bridge.py --status
python 03_scripts/cc_codex_bridge.py --write-pair --title post-merge-smoke --dry-run
python 03_scripts/course_certificate_assistant.py --policy
python 03_scripts/prompt_bus.py --status-json
python 03_scripts/agent_lane_status.py --check
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
git diff --check
```

If validation passes:

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## Rollback-Safe Advice

- Do not reset without explicit human approval.
- If merge conflicts appear, stop and inspect; do not auto-resolve broad implementation conflicts.
- If validation fails, keep the merge local and either abort before commit or create a specific fix branch after approval.
- Do not stage `node_modules/`, logs, `.env`, credentials, generated local smoke outputs, or unrelated dirty files.
