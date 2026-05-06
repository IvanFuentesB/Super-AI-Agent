# Codex N+3.56 - Merge Plan

## Merge Verdict

CONDITIONAL PASS.

The branch is safe to merge from a safety perspective if the operator accepts that Ruflo and Gemma are still capability-gated. If the goal is to claim full N+3.51 capability before merge, ask Claude for a small fix branch first.

## Recommended Path

Preferred: merge the branch, then immediately run a small N+3.57 hardening/fix milestone.

Reason: No unsafe live behavior was found, merge is conflict-free, and the current gaps are mostly environment/prerequisite/polish issues.

## Exact Merge Commands

```powershell
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git fetch origin
git merge --no-ff origin/feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening -m "merge(ghoti): land N+3.51 bridge Ruflo Gemma hardening"
```

## Post-Merge Validation Commands

```powershell
python -c "import ast, pathlib; files=['03_scripts/cc_codex_bridge.py','03_scripts/course_certificate_assistant.py','03_scripts/ruflo_install_gate.py','03_scripts/gemma_compact_memory_worker.py','03_scripts/ghoti_dashboard.py','03_scripts/prompt_bus.py','03_scripts/local_worker_router.py','03_scripts/agent_lane_status.py']; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8')) for f in files]; print('AST OK')"
python 03_scripts/cc_codex_bridge.py --status
python 03_scripts/cc_codex_bridge.py --write-pair --title post-merge-smoke --body "Post-merge local bridge smoke only." --dry-run
python 03_scripts/course_certificate_assistant.py --policy
python 03_scripts/course_certificate_assistant.py --plan --course-name "Audit Smoke Course" --provider "Local Test" --hours 10 --deadline "2026-06-01" --dry-run
python 03_scripts/ruflo_install_gate.py --status
python 03_scripts/ruflo_install_gate.py --install --dry-run
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/gemma_compact_memory_worker.py --compress --input 14_context/compact_memory/project_state.md --dry-run
python 03_scripts/prompt_bus.py --status-json
python 03_scripts/prompt_bus.py --write-context-pack --target all --title post-merge-smoke --include-status --include-memory --include-next-actions --dry-run
python 03_scripts/ghoti_dashboard.py --json
python 03_scripts/agent_lane_status.py --check
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
powershell -ExecutionPolicy Bypass -File 03_scripts/open_obsidian_vault.ps1 -Check
git diff --check
```

If acceptable:

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## If Operator Wants Fix Before Merge

Ask Claude for:

```text
N+3.56-FIX - Small bridge hardening fixes before merge
```

Fix list:

1. Add `--goal` to `course_certificate_assistant.py` or remove it from official validation docs.
2. Ensure bridge dirs can be initialized safely so `cc_codex_bridge.py --verify` is not PARTIAL after merge.
3. Align Obsidian executable detection between dashboard and PowerShell helper.
4. Make dashboard wording say Ruflo is "gate present, repo missing" rather than "deps installable" when the Ruflo repo is absent.
5. Add a router rule that routes "bridge handoff" tasks to `cc_codex_bridge` rather than `codex_audit`.

## Do Not Do

- Do not run Ruflo runtime, swarm, MCP, or `npx`.
- Do not run global installs.
- Do not run Gemma apply until a Gemma model is installed and output path is confirmed draft-only.
- Do not use browser automation, accounts, email, posting, scraping, payments, or job applications.
