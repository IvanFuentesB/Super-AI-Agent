# Codex N+3.50 - Post N+3.49A Audit

Milestone: N+3.50B - Audit Claude N+3.49A and prepare merge safety verdict

Date: 2026-05-06

## Branch Audited

- Base branch: `origin/feat/ghoti-visible-operator-stack`
- Base HEAD: `75856727c36ba7be00b3931ee094a1ec25fe660b`
- Claude branch: `origin/feat/ghoti-agent-claude-n3-49-local-orchestrator-ruflo-smoke`
- Claude commit audited: `c053fc6b3e1fca9ad90d39569f797a43272b2df7`
- Audit branch: `audit/ghoti-agent-codex-n3-50-n3-49a-audit`

The Claude branch resolves to the expected `c053fc6b3e1fca9ad90d39569f797a43272b2df7`.

## Files Changed By Claude Branch

Diff against `origin/feat/ghoti-visible-operator-stack`:

- Added `03_scripts/ghoti_local_orchestrator.py`
- Modified `03_scripts/prompt_bus.py`
- Modified `03_scripts/local_worker_router.py`
- Added `03_scripts/open_obsidian_vault.ps1`
- Added `14_context/tooling/obsidian_open_helper_n3_49a.md`
- Added `14_context/tooling/ruflo_isolated_smoke_n3_49a.md`
- Added `14_context/claude_n3_49a_local_orchestrator_prompt_bus_ruflo.md`
- Modified `14_context/agent_lanes/active_locks.jsonl`
- Modified `14_context/agent_lanes/lane_status.jsonl`
- Modified `23_configs/local_worker_routing.example.json`

Raw `git diff base..claude` also showed N+3.48 docs as deleted. A no-commit merge test from current base showed normal Git merge preserves those files. This is because the Claude branch forked before N+3.48 existed; it is not a merge blocker as long as a normal merge is used.

## Validation Commands And Results

Validation was run in a detached temporary worktree at `C:\Users\ai_sandbox\Documents\AI_Managed_Only_n3_49a_validate`, checked out at `c053fc6`.

### Python AST

```powershell
python -c "import ast, pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['03_scripts/ghoti_local_orchestrator.py','03_scripts/prompt_bus.py','03_scripts/local_worker_router.py']]; print('AST OK ghoti_local_orchestrator.py prompt_bus.py local_worker_router.py')"
```

Result: PASS.

### CLI Smoke

```powershell
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
```

Results:

- `ghoti_local_orchestrator.py --help`: PASS.
- `--status`: PASS, stdout only.
- `--plan-next`: PASS, stdout only.
- `--write-next-prompts --dry-run`: PASS, preview only. No files written in temp worktree.
- `--obsidian-check`: PASS; required Obsidian and compact memory files exist in temp worktree.
- `--ruflo-check`: PASS as a safe missing-state check in temp worktree. It reports Ruflo missing there because the Ruflo eval clone is local/untracked in the main workspace.
- `--gemma-check`: PARTIAL. Ollama is found, but `ollama list` did not show a Gemma model in this Codex validation run.
- `prompt_bus.py --status-json`: PASS, valid JSON output.
- `prompt_bus.py --write-chatgpt --dry-run`: PASS, preview only.
- `local_worker_router.py` Python automation route: PASS, routes to `python_automation_worker`.
- `local_worker_router.py` Ruflo route: PASS, routes to `ruflo_orchestrator_candidate`.
- `local_worker_router.py` course/certificate ethical route: NEEDS FOLLOW-UP, routed to `claude_code_impl` instead of `course_certificate_assistant`.

### JSON And JSONL

```powershell
python - <<'PY'
import json, pathlib
for p in [pathlib.Path("23_configs/local_worker_routing.example.json")]:
    json.loads(p.read_text(encoding="utf-8"))
    print("JSON OK", p)
for p in [pathlib.Path("14_context/agent_lanes/active_locks.jsonl"), pathlib.Path("14_context/agent_lanes/lane_status.jsonl")]:
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            json.loads(line)
    print("JSONL OK", p)
PY
```

Results:

- `23_configs/local_worker_routing.example.json`: PASS.
- `14_context/agent_lanes/active_locks.jsonl`: PASS, 2 records.
- `14_context/agent_lanes/lane_status.jsonl`: PASS, 4 records.

### Diff Check

`git diff --check` in the validation worktree: PASS.

### Merge Test

A temporary no-commit merge from current base succeeded:

```powershell
git merge --no-commit --no-ff origin/feat/ghoti-agent-claude-n3-49-local-orchestrator-ruflo-smoke
```

Result: PASS. Automatic merge went well. N+3.48 docs remained tracked after merge.

## Safety Verdict

Safety verdict: CONDITIONAL PASS.

No evidence found of:

- email sending
- posting
- payment actions
- account login automation
- scraping
- secrets or `.env` reads
- npm install by Codex
- actual Ruflo runtime wiring
- global installs
- background agent swarm start
- browser/desktop automation

Ruflo remains isolated and only read-checked. The branch recommends a safe install command, but does not run it.

## Issues Found

1. Course/certificate route miss:
   - Test phrase: `help me complete a course and get a certificate ethically`
   - Actual route: `claude_code_impl`
   - Expected safer route: `course_certificate_assistant`
   - Severity: low/medium. Not a live-action risk, but the next Claude fix should improve keyword coverage for ethical course/certificate language.

2. Gemma availability mismatch:
   - User Phase 1 notes said Gemma exists.
   - Codex validation saw Ollama installed but no Gemma model listed by `ollama list`.
   - Severity: medium for token-saving roadmap, not merge-blocking.
   - Recommendation: next Claude should re-check model names and avoid pulling models without explicit user approval.

3. Ruflo git metadata ownership:
   - Main workspace contains `21_repos/third_party/evals/ruflo`, package `claude-flow` version `3.5.80`, no `node_modules`.
   - `git -C ... rev-parse HEAD` reports dubious ownership for the local eval repo under current user.
   - Package metadata can still be read.
   - Recommendation: do not change global Git config automatically. If deep Git inspection is required, ask for explicit approval before adding `safe.directory`.

4. Clean worktree path differences:
   - In the detached validation worktree, `14_context/ghoti_current_prompt.md` is missing and Ruflo dir is missing because those are local/untracked workspace artifacts.
   - The code handles these missing states safely.

## Merge Recommendation

Merge recommendation: CONDITIONAL PASS - safe to merge if the operator accepts the listed follow-up issues.

Recommended merge approach:

1. Merge `origin/feat/ghoti-agent-claude-n3-49-local-orchestrator-ruflo-smoke` into `feat/ghoti-visible-operator-stack` using a normal merge.
2. Validate with AST, orchestrator smoke, JSON/JSONL, and `git diff --check`.
3. Push base branch.
4. Do not run npm install, Ruflo runtime, browser tools, live accounts, or Gemma model pulls during merge.

Follow-up should be handled immediately in the next Claude milestone:

- tighten course/certificate routing keywords
- add dashboard/local orchestrator read card
- add a Ruflo install gate runner that only performs `npm ci --ignore-scripts` after explicit approval
- re-check Ollama/Gemma model truth
