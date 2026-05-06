# Codex N+3.58 - Merge Plan

## Merge Verdict

CONDITIONAL PASS, fix-first recommended.

Do not merge as a clean pass. The branch is safe from live-action risk, but the dashboard/Obsidian crash and target whitespace failure should be fixed before main receives it.

## Fix-First Branch

Recommended Claude fix branch:

```text
feat/ghoti-agent-claude-n3-58-fix-obsidian-dashboard-whitespace
```

Fix list:

1. `obsidian_probe.py`: catch `PermissionError` and `OSError` when probing executable candidates.
2. `ghoti_dashboard.py`: avoid direct unsafe `.exists()` on inaccessible executable candidates; use the unified safe probe.
3. `14_context/ghoti_dashboard_card.md`: remove trailing whitespace and regenerate truthful current values.
4. Optional: ensure `open_obsidian_vault.ps1 -Check` surfaces probe permission-denied status without a Python traceback.

## Merge Commands After Fix Or If Operator Accepts Conditional

```powershell
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git fetch origin
git merge --no-ff origin/feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass -m "merge(ghoti): land N+3.56 clean-pass bridge hardening"
```

## Post-Merge Validation Commands

```powershell
python -c "import ast, pathlib; files=['03_scripts/cc_codex_bridge.py','03_scripts/course_certificate_assistant.py','03_scripts/ruflo_install_gate.py','03_scripts/gemma_compact_memory_worker.py','03_scripts/obsidian_probe.py','03_scripts/ghoti_dashboard.py','03_scripts/prompt_bus.py','03_scripts/local_worker_router.py','03_scripts/agent_lane_status.py']; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8')) for f in files]; print('AST OK')"
python 03_scripts/cc_codex_bridge.py --status
python 03_scripts/cc_codex_bridge.py --init --dry-run
python 03_scripts/course_certificate_assistant.py --plan --course-name "Audit Smoke Course" --provider "Local Test" --goal "Create legitimate study plan only" --dry-run
python 03_scripts/ruflo_install_gate.py --source-status
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/obsidian_probe.py --status
python 03_scripts/ghoti_dashboard.py --json
python 03_scripts/prompt_bus.py --status-json
python 03_scripts/agent_lane_status.py --check
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
git diff --check
git diff --cached --check
```

If validation passes:

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## Stop Conditions

Stop and do not push main if:

- Obsidian probe/dashboard still crash.
- `git diff --cached --check` still reports target-introduced whitespace.
- Any live action, secret read, Ruflo runtime, MCP/swarm launch, `npx`, global install, account action, email, posting, payment, scraping, job application, fake certificate, cheating, or assessment submission path appears.
