# Ghoti Merge Assistant — Merge Plan — N+3.58A

Generated: 20260506T211643Z
Current branch: `feat/ghoti-agent-claude-n3-58-language-truth-rust-readiness-merge-assistant`
Main branch: `feat/ghoti-visible-operator-stack`
Main local HEAD: `e7e946a`
Main remote HEAD: `e7e946a`
Target branch: `origin/feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass`
Target exists: True
Target HEAD: `874aefd`
Primary worktree dirty: YES (16 files)

## Pre-Merge Checklist

- [ ] Codex N+3.56-FIX audit must say PASS (not CONDITIONAL PASS, not BLOCKED)
- [ ] **Do not merge if Codex says BLOCKED**
- [ ] Primary worktree is clean or dirty files are intentionally unstaged
- [ ] Target branch is fetched and up-to-date with remote
- [ ] All validation scripts pass on target branch
- [ ] Codex N+3.56-FIX clean-pass audit (N+3.57) PASS confirmed before merge

## Phase-by-Phase Merge Commands (PowerShell — Operator Executes Manually)

### Phase 1 — Fetch

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
git fetch origin
```

### Phase 2 — Switch to Main

```powershell
git switch feat/ghoti-visible-operator-stack
```

### Phase 3 — Pull Fast-Forward Only

```powershell
git pull --ff-only origin feat/ghoti-visible-operator-stack
```

### Phase 4 — Merge Target Branch (no fast-forward, preserve history)

```powershell
git merge --no-ff origin/feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass -m "merge: land origin/feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass into feat/ghoti-visible-operator-stack"
```

### Phase 5 — Run Validations

```powershell
python -c "import ast, pathlib; files=['03_scripts/repo_language_inventory.py','03_scripts/rust_readiness_probe.py','03_scripts/ghoti_merge_assistant.py','03_scripts/ghoti_dashboard.py','03_scripts/local_worker_router.py','03_scripts/agent_lane_status.py']; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8')) for f in files]; print('AST OK')"
python 03_scripts/ghoti_dashboard.py --status
python 03_scripts/ghoti_dashboard.py --json
python 03_scripts/repo_language_inventory.py --status
python 03_scripts/rust_readiness_probe.py --status
python 03_scripts/local_worker_router.py --recommend --task "check Rust readiness for future runtime core"
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
git diff --check
```

### Phase 6 — Push Main (only after validations pass and operator approves)

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## Safety Notes

- **Do not merge if Codex says BLOCKED.**
- Codex N+3.56-FIX clean-pass audit (N+3.57) should PASS before merging.
- Do not force-push main.
- Do not skip the validation phase.
- If merge conflicts arise, resolve them manually before pushing.
- Primary worktree dirt should be stashed or committed separately before merging.
- This script generates commands only. It does NOT execute the merge.
