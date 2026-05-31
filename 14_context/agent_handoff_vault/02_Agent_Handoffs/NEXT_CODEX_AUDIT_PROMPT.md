# Next Codex Audit Prompt — N+6.6A Hermes Router Wrapper System

Status: ready-for-codex (after Claude pushes the N+6.6A branch)
Source spec: `docs/GHOTI_N6_6_HERMES_ROUTER_WRAPPERS_SPEC.md`

## Role
You are the auditor. Codex **does not implement** and **does not merge**. Verify
the implementation branch against main and return a verdict. A human merges.

## Under audit (proposed)
- Implementation branch: `feat/ghoti-agent-claude-n6-6a-hermes-router-wrappers`
- Base main: current `origin/main` (must contain N+6.4A + N+6.4B).
- Write your audit to branch:
  `audit/ghoti-agent-codex-n6-6a-hermes-router-wrappers-real-audit`.

## Scope check
1. Only the allowed files changed: `03_scripts/hermes_wrappers/*.ps1`, the
   N+6.6A test, the wrapper-run log folder, and the run report. No unrelated edits.
2. No generated artifact or secret slipped into the commit.
3. Commit message contains no AI/Claude/Anthropic attribution trailer.

## Safety / contract check
1. Each of the six Phase-1 wrappers matches its contract in the spec.
2. Wrappers enforce repo-root + vault allow-list and reject `..` traversal and
   paths outside the root.
3. **never run arbitrary commands** — no `Invoke-Expression` of caller-supplied
   strings; no pass-through shell.
4. **no secrets** read/written; no `.env`/token/cookie/auth handling.
5. `run_gemma_summary` calls **loopback only** (`127.0.0.1:11434`) and refuses any
   non-local host.
6. Any `launch_*` wrapper present is **dry-run only** and cannot execute.
7. **no Telegram**, **no browser/computer-use**, **no MCP installed**, no live API,
   no autonomous launch.
8. Every run-log record carries `local_only:true` and `live_action:false`.

## Tests / validation check
1. Re-run `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py" -v`;
   confirm the new N+6.6A tests pass and the pre-existing n6 tests still pass.
2. `python 03_scripts/public_repo_security_audit.py --run --json` → 0 failed checks.
3. Confirm tests actually cover traversal rejection, secret rejection, dry-run
   writes-nothing, and the run-log fields (not just file existence).

## Overclaim check
- Confirm no doc/report claims a wrapper launches an agent, that Telegram/browser/
  computer-use/MCP is enabled, or that Ghoti is autonomous. Flag any **overclaim**.

## Reversibility
- Confirm the change is scripts + tests + report only and is trivially revertable.

## Verdict (choose one)
- `CLEAN PASS` — scope, safety, tests, and truthfulness all hold.
- `CONDITIONAL PASS` — passes with minor, named, non-blocking notes.
- `BLOCKED_VALIDATION` — a required check fails; state the exact blocker so the
  next Claude milestone can fix only that.

Write the verdict and the exact blocker (if any) to
`14_context/agent_handoff_vault/04_Logs/CODEX_LAST_AUDIT.md`.
