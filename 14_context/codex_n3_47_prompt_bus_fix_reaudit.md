# Codex N+3.47 - Prompt Bus Fix Re-Audit

Milestone: N+3.47 - Re-Audit Claude N+3.45A-FIX And Prepare Final Merge Commands

Date: 2026-05-05

## Branches Inspected

- Base remote branch: `origin/feat/ghoti-visible-operator-stack`
- Base remote HEAD: `46941c8a0e68a8f67fe6ceb00e1be40032c8629b`
- Claude remote branch: `origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus`
- Claude remote HEAD: `13266eaf663bc0a6b7d205d57d869263b1af6e38`
- Previous Codex audit remote branch: `origin/audit/ghoti-agent-codex-n3-46-n3-45a-merge-audit`
- Previous Codex audit remote HEAD: `685fed9021e7528733a70d3f90e038c0c7dfd7ad`
- N+3.47 audit branch: `audit/ghoti-agent-codex-n3-47-prompt-bus-fix-reaudit`

## Important Repo Truth

The expected new Claude fix commit was not found on the remote Claude branch.

`origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus` still points to:

```text
13266ea feat(ghoti): add N+3.45A tooling and prompt bus
```

The local Claude branch now contains a new local fix commit:

```text
110a84a fix(ghoti): preserve prompt bus dry-run purity
```

However, the fix commit has not been pushed to `origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus` as of this audit. The local and remote branch are therefore out of sync:

- local `feat/ghoti-agent-claude-n3-45-tooling-prompt-bus`: `110a84a`
- remote `origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus`: `13266ea`

The local fix commit changes:

- `.claude/settings.json`
- `03_scripts/prompt_bus.py`

Those changes are the intended dry-run fix and the allowed removal of the exact Claude Code deny rule `Bash(git push*)`, but they are not pushed.

## Dry-Run Purity Verdict

Remote mergeable Claude branch: FAIL / NOT READY.

Reason: the remote Claude branch is still at `13266ea`, the same commit that Codex N+3.46 flagged as conditional because `cmd_init()` called `_ensure_dirs()` before checking dry-run.

Local Claude fix commit `110a84a`: PASS.

Evidence from local diff:

```diff
 def cmd_init(args):
-    _ensure_dirs()
     if args.dry_run and not args.apply:
         print("[DRY RUN] Would create directories:")
         ...
         return
+    _ensure_dirs()
     print("Directories verified/created:")
```

Code inspection verdict for local patch:

- `--init --dry-run` returns before `_ensure_dirs()` is called.
- Directory creation happens only after the dry-run return path.
- `--write-claude` writes only under `if args.apply:`.
- `--write-codex` creates the outbox directory and writes only under `if args.apply:`.
- `--status` and `--list-outbox` are read-only.
- No clipboard use was found.
- No external APIs, email, posting, payment, scraping, browser automation, or account actions were found.

## Settings Rule Verdict

Local `.claude/settings.json` change in `110a84a`: PASS, scoped exactly.

Evidence:

```diff
     "deny": [
       "Bash(rm -rf *)",
-      "Bash(git push*)",
       "Bash(git reset --hard*)",
```

JSON validation confirmed `.claude/settings.json` parses and no longer contains `Bash(git push*)` in the local working tree.

Remote branch verdict:

- `.claude/settings.json` is not changed on the remote Claude branch.
- Therefore the allowed push-deny removal is not yet committed/pushed.

## Validation Results

Validation was run against local Claude commit `110a84a`.

Commands run:

```powershell
python 03_scripts/prompt_bus.py --init --dry-run
python -c "import ast, pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['03_scripts/prompt_bus.py','03_scripts/local_worker_router.py']]; print('AST OK prompt_bus.py local_worker_router.py')"
python 03_scripts/prompt_bus.py --help
python 03_scripts/prompt_bus.py --init --dry-run
python 03_scripts/prompt_bus.py --status
python 03_scripts/prompt_bus.py --write-claude --title "smoke" --body "smoke body" --dry-run
python 03_scripts/prompt_bus.py --write-codex --title "smoke" --body "smoke body" --dry-run
python 03_scripts/prompt_bus.py --list-outbox
python 03_scripts/local_worker_router.py --help
python 03_scripts/local_worker_router.py --recommend --task "compress a long markdown handoff"
python 03_scripts/local_worker_router.py --recommend --task "edit dashboard JavaScript"
python 03_scripts/local_worker_router.py --recommend --task "validate JSONL"
python 03_scripts/local_worker_router.py --study-template --dry-run
python 03_scripts/local_worker_router.py --course-cert-template --dry-run
python 03_scripts/agent_lane_status.py --check
python 03_scripts/agent_lane_status.py --list
```

Results:

- AST validation: PASS.
- Prompt bus dry-run smoke: PASS.
- Prompt bus status/write/list dry-runs: PASS.
- Local worker router help/recommend/template dry-runs: PASS.
- Agent lane status check/list: PASS.
- `23_configs/local_worker_routing.example.json`: JSON PASS.
- `14_context/agent_lanes/active_locks.jsonl`: JSONL PASS.
- `14_context/agent_lanes/lane_status.jsonl`: JSONL PASS.
- `.claude/settings.json`: JSON PASS.
- `.claude/settings.json` contains `Bash(git push*)`: False.
- `git diff --check`: PASS, with LF-to-CRLF warnings only.

## File Scope Verdict

Remote Claude branch file scope remains the expected N+3.45A scope:

- `.claude/commands/`
- `03_scripts/prompt_bus.py`
- `03_scripts/local_worker_router.py`
- `14_context/prompt_bus/`
- `14_context/tooling/`
- `14_context/local_workers/`
- `14_context/prompt_bus_n3_45a.md`
- `14_context/local_worker_routing_n3_45a.md`
- `14_context/claude_commands_n3_45a.md`
- `23_configs/local_worker_routing.example.json`
- `14_context/agent_lanes/active_locks.jsonl`
- `14_context/agent_lanes/lane_status.jsonl`

Local fix commit adds only:

- `.claude/settings.json`
- `03_scripts/prompt_bus.py`

No Codex `codex_n3_45b_*.md` files appear in the Claude branch diff.

## Codex Branch Separation

`origin/audit/ghoti-agent-codex-n3-45-tool-routing` remains separate and contains only the seven expected N+3.45B docs.

Accidental `370e19b` remains local-only:

- `git branch -r --contains 370e19b`: no remote branch output.
- `git branch --contains 370e19b`: local `audit/ghoti-agent-codex-n3-45-tool-routing` only.

## Safe/Unsafe Verdict

Final verdict: NOT READY TO MERGE FROM REMOTE YET.

Why:

- The fix is present in local commit `110a84a` and passes locally.
- The fix is not pushed to `origin/feat/ghoti-agent-claude-n3-45-tooling-prompt-bus`.
- The remote Claude branch remains the old conditional-pass commit `13266ea`.

Required next action:

Push the local Claude fix commit, or recommit the exact two-file fix on the Claude branch and push:

- `.claude/settings.json`
- `03_scripts/prompt_bus.py`

After that, re-run the merge commands in `14_context/codex_n3_47_final_merge_plan.md`.
