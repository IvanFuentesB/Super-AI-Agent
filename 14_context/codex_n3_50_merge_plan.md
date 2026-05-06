# Codex N+3.50 - Merge Plan For Claude N+3.49A

Milestone: N+3.50B - Audit Claude N+3.49A and prepare merge safety verdict

Date: 2026-05-06

## Merge Verdict

Verdict: CONDITIONAL PASS.

The branch is safe to merge if the operator accepts these follow-up issues:

- course/certificate route keyword miss should be fixed in the next Claude milestone
- Gemma model truth should be rechecked before claiming automatic local compression
- Ruflo install must remain isolated and approval-gated
- no runtime Ruflo wiring yet

## Exact Merge Commands

Run from the main repo:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git fetch origin
git rev-parse origin/feat/ghoti-visible-operator-stack
git rev-parse origin/feat/ghoti-agent-claude-n3-49-local-orchestrator-ruflo-smoke
git merge --no-ff origin/feat/ghoti-agent-claude-n3-49-local-orchestrator-ruflo-smoke -m "merge(ghoti): land N+3.49A local orchestrator and Ruflo smoke"
```

## Post-Merge Validation

After merge and before push:

```powershell
python -c "import ast, pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['03_scripts/ghoti_local_orchestrator.py','03_scripts/prompt_bus.py','03_scripts/local_worker_router.py']]; print('AST OK')"
python 03_scripts/ghoti_local_orchestrator.py --help
python 03_scripts/ghoti_local_orchestrator.py --status
python 03_scripts/ghoti_local_orchestrator.py --plan-next
python 03_scripts/ghoti_local_orchestrator.py --write-next-prompts --dry-run
python 03_scripts/ghoti_local_orchestrator.py --obsidian-check
python 03_scripts/ghoti_local_orchestrator.py --ruflo-check
python 03_scripts/ghoti_local_orchestrator.py --gemma-check
python 03_scripts/prompt_bus.py --status-json
python 03_scripts/prompt_bus.py --write-chatgpt --title smoke --body smoke --dry-run
python 03_scripts/local_worker_router.py --recommend --task "write a small Python automation to organize local prompt files"
python 03_scripts/local_worker_router.py --recommend --task "use Ruflo to coordinate local agents"
python 03_scripts/local_worker_router.py --recommend --task "help me complete a course and get a certificate ethically"
python 03_scripts/agent_lane_status.py --check
python -m json.tool 23_configs/local_worker_routing.example.json
git diff --check
```

Then push:

```powershell
git push origin feat/ghoti-visible-operator-stack
```

## Expected Merge Result

A no-commit merge test from current base succeeded and preserved the N+3.48 docs.

Expected changed files after merge:

- `03_scripts/ghoti_local_orchestrator.py`
- `03_scripts/prompt_bus.py`
- `03_scripts/local_worker_router.py`
- `03_scripts/open_obsidian_vault.ps1`
- `14_context/agent_lanes/active_locks.jsonl`
- `14_context/agent_lanes/lane_status.jsonl`
- `14_context/claude_n3_49a_local_orchestrator_prompt_bus_ruflo.md`
- `14_context/tooling/obsidian_open_helper_n3_49a.md`
- `14_context/tooling/ruflo_isolated_smoke_n3_49a.md`
- `23_configs/local_worker_routing.example.json`

N+3.48 docs should remain present.

## Rollback Notes If Merge Fails

If merge has conflicts:

```powershell
git status --short
git merge --abort
```

Then stop and ask the user. Do not run `git reset --hard`.

If validation fails:

```powershell
git status --short
```

Document the failure and either:

- fix only the specific issue on a Claude recovery branch, or
- abort the merge before committing if still in merge state.

Do not stage unrelated local dirt.

## Hard No During Merge

Do not:

- npm install Ruflo
- run Ruflo
- run OpenClaw/Paperclip/n8n/CUA/browser tools
- read `.env`
- connect accounts
- send email
- post
- pay
- scrape
- apply to jobs
- enter giveaways
- pull Gemma models
