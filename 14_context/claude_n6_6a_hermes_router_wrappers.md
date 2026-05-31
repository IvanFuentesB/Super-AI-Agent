# N+6.6A — Hermes Soul + Router Wrapper Foundation (run report)

Lane: implementation specialist (Claude Code). Codex audits next; a human merges.
Date: 2026-05-31

## Branch / base

- Branch: `feat/ghoti-agent-claude-n6-6a-hermes-router-wrappers`
- Worktree: `.claude/worktrees/n6_6a_hermes_router_wrappers` (repo-contained, isolated)
- Base `main`: `67eb4a5` — `docs(ghoti): record n6.4b main merge gate` (N+6.4B).
- Pushed: feature branch only (see final response / `git ls-remote`). `main` not touched.

## Start condition (verified)

- `origin/main` is at N+6.4B (`67eb4a5`); the N+6.4B vault + Hermes truth foundation
  is present (`14_context/agent_handoff_vault/`, `AGENT_RULES.md`, handoff + log notes).
- `origin/feat/ghoti-agent-codex-n6-5a-safe-computer-use-observation-harness` exists and
  was inspected read-only: it is an **observation-only** harness and does **not** overlap
  the N+6.6A file set. It is **not** claimed to be merged.
- `origin/plan/ghoti-n6-6-7-8-command-center-architecture` exists (the prior planning
  lane) and was inspected read-only. This milestone implements only the N+6.6A slice.

## What was built (15 files, all new)

Soul / memory (`14_context/agent_handoff_vault/`):
- `HERMES_SOUL.md` — Hermes is the local coordinator/memory writer, **not** the main
  brain (ChatGPT is); approved wrappers only; never run arbitrary commands; preserve
  safety gates; ask for human approval on risk; never store secrets; never claim an
  unverified live capability.
- `HERMES_CURRENT_STATUS.md` — N+6.4B on main; N+6.5A is observation-only and not
  claimed merged; N+6.6A implements the wrapper foundation; Telegram/browser-computer-use/
  MCP not enabled; external repos not mass-installed; `llama3.1:8b` coordinator brain,
  Gemma is the cheap summary/compression worker.
- `HERMES_ROUTER_POLICY.md` — routing table, risk levels (low/medium/high/blocked),
  status lifecycle ending in `human_decision`.
- `04_Logs/HERMES_COORDINATOR_SUMMARY.md` — coordinator snapshot (read by
  `collect_agent_outputs.ps1`).

Wrappers (`03_scripts/hermes_router/`, dry-run / read-only):
- `read_current_task.ps1` (read-only)
- `write_handoff_note.ps1` (dry-run; `-AllowWrite` to write under `04_Logs/` only)
- `prepare_claude_prompt.ps1` (dry-run; never launches Claude)
- `prepare_codex_audit.ps1` (dry-run; never launches Codex)
- `collect_agent_outputs.ps1` (read-only)
- `run_gemma_summary.ps1` (dry-run only; no model call, no network)
- `hermes_router_status.ps1` (read-only; reports standing safety flags)
- `README.md` (safety model + wrapper table)

Doc + test + report:
- `docs/GHOTI_N6_6A_HERMES_ROUTER_WRAPPERS.md`
- `01_projects/runtime_mvp/tests/test_n6_6a_hermes_router_wrappers.py`
- `14_context/claude_n6_6a_hermes_router_wrappers.md` (this report)

## Safety model enforced

- **Approved wrappers only**; Hermes **never runs arbitrary commands**. No
  `Invoke-Expression`, no `Start-Process`, no `Invoke-WebRequest`/`Invoke-RestMethod`,
  no installs — proven by a static scan test over every `.ps1`.
- **Dry-run / read-only by default.** Writers require an explicit `-AllowWrite`.
- **Path containment.** `write_handoff_note.ps1` sanitizes the title to `[a-z0-9_-]`
  and refuses any path outside `04_Logs/`. Probe `..\..\..\Windows\System32\evil:note`
  resolved to `windows_system32_evil_note.md`, `under_logs=true`, `wrote=false`.
- **No launches, no network, no secrets.** `prepare_*` report `launches_claude/codex=false`;
  `run_gemma_summary` reports `local_model_call_implemented=false`, `network_used=false`.

## Validation (real output)

| Check | Result |
|-------|--------|
| `test_n6_6a_hermes_router_wrappers` | 16 passed |
| `unittest discover -p "test_n6_*.py"` | **46 passed** (30 pre-existing + 16 new), 0 failures |
| `git diff --check` | clean |
| `ghoti_product_launcher.py --status --json` | `ok=True` |
| `ghoti_product_launcher.py --context-pack --json` | `ok=True` (residue reverted) |
| `ghoti_product_launcher.py --repo-map --json` | `ok=True` (residue reverted) |
| `public_repo_security_audit.py --run --json` | total 150, passed 143, **failed 0**, warnings 7, `safe_to_make_public=True` |
| Generated residue | 19 files under `compact_memory/generated` + `repo_knowledge/generated` reverted; only the 15 intended files committed |

## What is explicitly NOT enabled

- No Telegram. No browser/computer-use. No MCP installed.
- No autonomous agent launch (prompt prep never starts an agent; launch is a later,
  separately-approved, dry-run-first milestone).
- No external repo clone/install/run. No live account/API/posting/money action.
- No arbitrary command execution by Hermes. `main` is untouched.

## What Codex should audit next

1. Each wrapper matches its contract; no `Invoke-Expression`/`Start-Process`/web call.
2. `write_handoff_note.ps1` cannot escape `04_Logs/` (traversal + containment).
3. `prepare_*` never launch an agent; `run_gemma_summary` makes no network/model call.
4. No doc overclaims Telegram/browser-computer-use/MCP/autonomy.
5. The change is memory notes + scripts + doc + test only, and is trivially revertable.

## Verdict

IMPLEMENTED_AND_PUSHED (feature branch only). The safe Hermes coordinator foundation
exists with tests; no autonomy, network, or external capability was enabled.
