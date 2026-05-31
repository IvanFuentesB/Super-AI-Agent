# Next Claude Task — N+6.6A Hermes Router Wrapper System (dry-run only)

Status: ready-for-claude (planned; not yet started)
Source spec: `docs/GHOTI_N6_6_HERMES_ROUTER_WRAPPERS_SPEC.md`

## Milestone
N+6.6A — Hermes Router Wrapper System (Phase-1 wrappers + tests, dry-run only).

## Goal
Implement the six Phase-1 Hermes wrappers as small, safe PowerShell scripts with
a fixed contract, plus tests that lock the safety behavior. Hermes must run
**approved wrappers only** and **never run arbitrary commands**. No agent is
launched. No live action is taken.

## Branch / worktree (proposed)
- Branch: `feat/ghoti-agent-claude-n6-6a-hermes-router-wrappers`
- Worktree: `.claude/worktrees/claude_n6_6a_hermes_router_wrappers` from origin/main.

## Build these wrappers (`03_scripts/hermes_wrappers/`)
1. `read_current_task.ps1`
2. `write_handoff_note.ps1`
3. `run_gemma_summary.ps1` (local loopback `http://127.0.0.1:11434/v1` only)
4. `prepare_claude_prompt.ps1`
5. `prepare_codex_audit.ps1`
6. `collect_agent_outputs.ps1`

Each must follow the per-wrapper contract in the spec (purpose, inputs, outputs,
allowed paths, forbidden actions, log, dry-run, failure, approval, tests,
security). Append one record per run to
`14_context/agent_handoff_vault/04_Logs/wrapper_runs/<date>.jsonl` with
`local_only:true` and `live_action:false`.

## Files allowed
- `03_scripts/hermes_wrappers/*.ps1` (new)
- `01_projects/runtime_mvp/tests/test_n6_6a_hermes_router_wrappers.py` (new)
- `14_context/agent_handoff_vault/04_Logs/wrapper_runs/` (log folder; first run)
- A short run report `14_context/claude_n6_6a_hermes_router_wrappers.md`

## Files forbidden
- Secrets, `.env`, auth files, cookies, tokens.
- Any `launch_*` wrapper that actually launches (Phase 2 is a later milestone;
  if stubbed, it must be **print-only dry-run**).
- Dashboard/app refactors unrelated to wrappers.
- Telegram, browser/computer-use, MCP, live account/API.

## Success criteria
- Six wrappers exist and honor the repo-root + vault allow-list; reject `..`
  traversal and any path outside the root.
- No wrapper reads/writes secrets; **never run arbitrary commands**
  (no `Invoke-Expression` of caller strings).
- Dry-run writes nothing; every run logs `local_only:true` / `live_action:false`.
- Tests cover happy path, traversal rejection, secret rejection, dry-run, and the
  log fields. Existing `test_n6_*.py` still pass.
- Report states what changed and what is still NOT enabled.

## Validation (run and capture real output)
- `git diff --check`; `git show --check --stat HEAD`
- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py" -v`
- `python 03_scripts/public_repo_security_audit.py --run --json` (0 failed)
- `python 03_scripts/ghoti_product_launcher.py --status --json` (ok=True)
- Restore any generated residue before committing.

## Safety rules
- No live actions; no agent launch; no broad process kills.
- No browser click/type; no Telegram; no MCP install.
- No external repo install or execution.
- One agent per task; never edit the same files as a parallel lane.
- Stage only intended files (no `git add -A`).
- Commit message must contain no AI/Claude/Anthropic attribution trailer.

## Final response format
branch · commit · pushed yes/no · files changed · wrapper list · test totals ·
security-audit result · safety summary · final verdict (IMPLEMENTED_AND_PUSHED or
BLOCKED).
