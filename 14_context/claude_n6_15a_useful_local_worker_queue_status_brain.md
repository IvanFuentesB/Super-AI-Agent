# Ghoti N+6.15A — Useful Local Worker Queue + Ghoti Status Brain (Report)

## Summary

N+6.15A delivers the first genuinely useful day-to-day local Ghoti workflow. One
local command turns the repo into a concise status packet (and an optional Obsidian
handoff note), built entirely from local, offline, read-only data:

```bash
python 03_scripts/local_worker_queue/ghoti_status_brain.py --json
```

That single command reports the `origin/main` head and recent commits, the latest
Claude and Codex milestone reports, the `n6` test count, confined computer-use
sandbox readiness (dry-run only), repo-intake progress, the Hermes and Telegram
posture, and a concrete next recommended action. With `--write-handoff` the same run
writes a handoff note that a later Hermes step can read instead of re-deriving a
weaker summary.

This is not live autonomy, not a swarm launcher, not live browser/web automation,
not Telegram control, not MCP, and not email/WhatsApp. Everything is local and
read-only, and every risky feature flag defaults to `false`.

## Branch / worktree / base

- Branch: `feat/ghoti-agent-claude-n6-15a-useful-local-worker-queue-status-brain`
- Worktree: `C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n6_15a_useful_local_worker_queue_status_brain`
- Base `origin/main`: `67b5bc6` (already contains N+6.14A via its merge commit)

## Dependency on N+6.14A

This milestone builds directly on the N+6.14A confined local browser sandbox
runner: the status brain reports computer-use readiness by invoking that runner's
**dry-run only**. During this session `origin/main` advanced to `67b5bc6`, which
already merged N+6.14A (implementation commit `385e2c5`). This branch is based on
`385e2c5`; because `385e2c5` is an ancestor of `67b5bc6`, the merge-base of this
branch and `origin/main` is `385e2c5`, all N+6.15A changes are net-new files (plus
one append-only flag edit), and the future merge to main is clean. No rebase was
performed.

## Files changed

New files (12):

- `docs/GHOTI_N6_15A_USEFUL_LOCAL_WORKER_QUEUE_STATUS_BRAIN.md`
- `14_context/local_worker_queue/README.md`
- `14_context/local_worker_queue/status_schema_n6_15a.json`
- `14_context/local_worker_queue/queue_examples/status_summary_task.json`
- `14_context/local_worker_queue/queue_examples/computer_use_sandbox_status_task.json`
- `14_context/local_worker_queue/queue_examples/repo_intake_summary_task.json`
- `03_scripts/local_worker_queue/ghoti_status_brain.py`
- `03_scripts/local_worker_queue/ghoti_local_worker_queue.py`
- `03_scripts/local_worker_queue/check_local_worker_queue.ps1`
- `03_scripts/local_worker_queue/README.md`
- `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_LOCAL_WORKER_QUEUE_TASK.md`
- `01_projects/runtime_mvp/tests/test_n6_15a_useful_local_worker_queue_status_brain.py`

Modified files (1):

- `23_configs/ghoti_feature_flags.example.json` — appended six N+6.15A flags, all
  `false` (`local_worker_queue_enabled`, `local_status_brain_enabled`,
  `local_gemma_summary_enabled`, `auto_schedule_worker_enabled`,
  `telegram_status_bridge_enabled`, `hermes_memory_writer_enabled`). The single
  enabled flag (`telegram_status_commands_enabled`) is preserved.

This report file (`14_context/claude_n6_15a_useful_local_worker_queue_status_brain.md`)
is the 13th committed file.

## Status packet field verification

The `--json` packet emits every required field. Verified values from this worktree:

| Field | Value / state |
|-------|---------------|
| `ok` | `true` |
| `repo_root` | this worktree |
| `origin_main_short` | `67b5bc6` |
| `current_branch` | `feat/ghoti-agent-claude-n6-15a-useful-local-worker-queue-status-brain` |
| `latest_main_commits` | recent `origin/main` commits |
| `n6_test_count_known_or_null` | `228` |
| `latest_codex_report` | `codex_n6_13b_sandbox_computer_use_audit_merge_gate.md` (N+6.13B) |
| `latest_claude_report` | `claude_n6_14a_confined_browser_sandbox_runner.md` (N+6.14A) |
| `latest_tool_intake_summary` | static repo-intake summary present |
| `computer_use_sandbox_status` | `mode: dry_run_only`, `browser_launched: false`, `dom_action_performed: false`, `os_input_used: false`, `live_website: false` |
| `telegram_runtime_status` | `inventory_only_not_running` |
| `hermes_integration_status` | `manual_bridge_only_readiness_64pct` |
| `repo_visibility_unknown_or_public_private` | `unknown` |
| `next_recommended_action` | concrete next step string |
| `handoff_written` | `false` by default, `true` with `--write-handoff` |
| `handoff_path` | `14_context/agent_handoff_vault/04_Logs/GHOTI_STATUS_BRAIN_LAST_RUN.md` |
| `gemma_used` | `false` by default; `true` with `--use-gemma-if-available` on this host |
| `fallback_summary_used` | `true` by default; `false` when Gemma is used |
| `safety` | `live_browser_used`, `os_input_used`, `external_api_used`, `telegram_control_used`, `mcp_used`, `auto_send_used` all `false`; `local_only: true` |

## Gemma vs. fallback

The optional `--use-gemma-if-available` path is exercised and never fails. On this
host a local Ollama install with `gemma3:4b` is present, so the run reported
`gemma_used: true` / `fallback_summary_used: false`, calling the **local** model
only (argument-list `subprocess`, ≤60s timeout, ANSI output sanitized). Without the
flag — or on a host without Ollama/Gemma, or on any failure/timeout — the brain uses
the deterministic local fallback (`gemma_used: false` / `fallback_summary_used:
true`). No model is downloaded or installed, and no repo contents are sent to any
external API. Exactly one of the two flags is true on every run.

## Handoff note

`--write-handoff` writes `14_context/agent_handoff_vault/04_Logs/GHOTI_STATUS_BRAIN_LAST_RUN.md`
(`handoff_written: true`) with sections for current status, useful capabilities,
pending branches, disabled safety surface, and the next action. The validation run
that produced this note was treated as residue and removed before commit; the note
is regenerated on demand and is not committed.

## Test totals

- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py"`
  → **Ran 228 tests, OK** (0 failures, 0 errors).
- The N+6.15A module `test_n6_15a_useful_local_worker_queue_status_brain.py`
  contributes **27 tests** across 8 classes (files exist; schema/examples valid;
  status-packet contract + safety; `--write-handoff`; optional-Gemma exclusivity;
  sandbox dry-run only; queue supported/blocked/default-deny; source-safety token
  scan; flags default-false + single-true invariant; docs no-overclaim; PowerShell
  check posture).

## Runtime / dashboard / PowerShell check result

- `git diff --check` → clean.
- `python 03_scripts/local_worker_queue/ghoti_status_brain.py --json` → `ok: true`.
- `python 03_scripts/local_worker_queue/ghoti_status_brain.py --write-handoff --json`
  → `handoff_written: true`.
- All three queue examples (`status_summary`, `computer_use_sandbox_status`,
  `repo_intake_summary`) → `ok: true`, `supported: true`, `blocked: false`.
- `pwsh -File 03_scripts/local_worker_queue/check_local_worker_queue.ps1`
  → `ok: true`, `risky_flags_default_false: true`, `local_only: true`.
- `python 03_scripts/ghoti_product_launcher.py --status --json` → `ok: true`;
  `--context-pack --json` and `--repo-map --json` → `ok: true` (their regenerated
  artifacts were restored after validation).
- `python 03_scripts/public_repo_security_audit.py --run --json` →
  `safe_to_make_public: true`, `failed_checks: 0`, `blocking_findings: []`.

## Safety summary

- **Not live autonomy.** Starts no agents; the queue blocks `launch_claude`,
  `launch_codex`, and any unrecognized task type by default-deny.
- **Local and offline.** No internet, no GitHub CLI, no external API, no account
  login, no secrets read. Git is read-only (`rev-parse`, `log`, `status`, `branch
  --show-current`).
- **No live browser / no OS input.** The computer-use task only runs the N+6.14A
  confined sandbox **dry-run**; no browser launch, no DOM action, no mouse/keyboard,
  no desktop control, no live website.
- **No Telegram control, no MCP, no email/WhatsApp, no auto-send.** Those task types
  are blocked.
- **No shell execution.** `subprocess` is always invoked with an argument list; no
  shell string is ever used and there is no `Invoke-Expression`.
- **No installs, no Docker.** `install_repo` and `docker_run` are blocked.
- **Disabled by default.** All six N+6.15A flags default `false`; the global kill
  switch still overrides everything.

## What remains disabled

Live autonomy and agent launching; live website navigation and live browser
automation; OS-level mouse/keyboard input and desktop control; Telegram control and
message sending; MCP writes; email and WhatsApp; auto-send; arbitrary shell
execution; running third-party repository code; dependency installation; Docker
runtime; and any outbound API or account action. Every risky feature flag defaults
to `false`.

## Direct answers

- Useful one command now: `python 03_scripts/local_worker_queue/ghoti_status_brain.py --json`.
- Was Gemma used or fallback only? Both paths verified: fallback by default; the
  local Gemma model genuinely ran under `--use-gemma-if-available` on this host. No
  install or download was performed.
- Was the handoff written? Yes, on demand via `--write-handoff`; the validation
  artifact was removed before commit.
- Did Ghoti run any agent, browser, OS input, Telegram, MCP, email, install, or
  Docker? No. All blocked by default-deny; the only computer-use path is the
  confined sandbox dry-run.
- Are approval/safety gates intact? Yes — unchanged and not weakened.

## Next step

`N+6.15B` (merge gate) or a later milestone can wire the read-only Hermes step to
load `04_Logs/GHOTI_STATUS_BRAIN_LAST_RUN.md` as coordinator status, and teach the
status-only Telegram bot to surface this packet on a read-only command — each under
separate review, with `hermes_memory_writer_enabled` and
`telegram_status_bridge_enabled` staying `false` until a human approves them.

## Codex audit target branch

`audit/ghoti-agent-codex-n6-15a-useful-local-worker-queue-status-brain`

## Final verdict

IMPLEMENTED_AND_PUSHED — local, offline, read-only; full `n6` suite green (228);
security audit clean; all six risky flags default `false`.
