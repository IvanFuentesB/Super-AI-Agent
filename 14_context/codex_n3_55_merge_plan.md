# Codex N+3.55 - Merge Plan

## Merge Verdict

PENDING TARGET BRANCH. Do not merge N+3.51 yet.

## Exact Blocker

The real Claude implementation branch is missing from the remote. The local same-named branch points to main `e7e946a`, not N+3.51 implementation work.

## Required Push Command

Claude or the operator must push the actual implementation branch:

```powershell
git push origin feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening
```

If Claude used a fallback branch name, push the actual fallback branch instead.

## Merge Commands If Future Audit Passes

After the branch exists and Codex issues PASS or an acceptable CONDITIONAL PASS:

```powershell
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git fetch origin
git merge --no-ff origin/feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening -m "merge(ghoti): land N+3.51 bridge hardening"
```

Post-merge validation:

```powershell
python -c "import ast, pathlib; files=['03_scripts/ruflo_install_gate.py','03_scripts/gemma_compact_memory_worker.py','03_scripts/cc_codex_bridge.py','03_scripts/course_certificate_assistant.py','03_scripts/prompt_bus.py','03_scripts/ghoti_dashboard.py','03_scripts/local_worker_router.py','03_scripts/agent_lane_status.py']; existing=[f for f in files if pathlib.Path(f).exists()]; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8')) for f in existing]; print('AST OK:', existing)"
python 03_scripts/ruflo_install_gate.py --status
python 03_scripts/ruflo_install_gate.py --install --dry-run
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/gemma_compact_memory_worker.py --compress --input 14_context/compact_memory/project_state.md --dry-run
python 03_scripts/cc_codex_bridge.py --verify
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

## Do Not Merge If

- The branch is still missing.
- The branch is stale at `e7e946a`.
- Implementation files exist only as dirty local changes.
- Ruflo runtime/swarm/MCP was launched.
- Gemma writes canonical memory directly.
- The bridge uses clipboard, auto-send, browser automation, or external APIs by default.
- Course helper enables cheating or fake certificates.
- Dashboard API triggers installs, compression, writes, or live actions.
