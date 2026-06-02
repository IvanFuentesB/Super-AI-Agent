# Ghoti N+6.16A — Status Bridge for Telegram + Hermes (Report)

## Summary

N+6.16A connects the N+6.15A local status brain to the surfaces where Ghoti is
actually opened — the status-only Telegram bot, Hermes (the local desktop/CLI
assistant), an Obsidian handoff vault, and local PowerShell — through one small,
local, read-only **status bridge**:

```bash
python 03_scripts/status_bridge/ghoti_status_bridge.py --json
```

The bridge reads the status brain once and renders it four ways: `--json` (full
packet for tools), `--markdown` (an Obsidian / Hermes note), `--telegram-safe-json`
(short, sanitized, length-bounded text for a Telegram reply), and
`--write-hermes-handoff` (also write a Hermes-readable handoff note). So Hermes,
Desktop, Telegram, and PowerShell all read **one** status source instead of each
repeating its own weak guess.

This is status-only. There is no remote control, no `/run`, no live agent launch,
no MCP, no live browser/computer-use, no OS click/type, no account login, no
email/WhatsApp, no auto-send, and no external API. Every new feature flag defaults
to `false`, and no Telegram token or chat id lives in the repo.

## Branch / worktree / base

- Branch: `feat/ghoti-agent-claude-n6-16a-status-bridge-telegram-hermes`
- Worktree: `C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n6_16a_status_bridge_telegram_hermes`
- Base commit: `08d7cb2` (N+6.15A, "feat(ghoti): add useful local worker queue status brain")
- Current `origin/main`: `de1cf84` (already merged N+6.15A)

## Dependency on N+6.15A

This milestone builds directly on the N+6.15A status brain
(`03_scripts/local_worker_queue/ghoti_status_brain.py`): the bridge invokes that
brain as a local, read-only subprocess and re-renders its packet for each surface.
During this session `origin/main` advanced to `de1cf84`, which already merged
N+6.15A (implementation commit `08d7cb2` via merge `0484fa2`). This branch is based
on `08d7cb2`; because `08d7cb2` is an ancestor of `de1cf84`, the merge-base of this
branch and `origin/main` is `08d7cb2`, all N+6.16A changes are net-new files plus
three append-only edits, and the future merge to main is clean. No rebase was
performed.

## Files changed

New files (8):

- `03_scripts/status_bridge/ghoti_status_bridge.py` — the status bridge (renders the
  brain packet as JSON / Markdown / Telegram-safe text; optional Hermes handoff write).
- `03_scripts/status_bridge/check_status_bridge.ps1` — read-only PowerShell health
  check (file presence, three render modes, safety flags).
- `03_scripts/status_bridge/README.md` — bridge purpose, the four CLI modes, safety.
- `docs/GHOTI_N6_16A_STATUS_BRIDGE_TELEGRAM_HERMES.md` — the milestone doc.
- `14_context/hermes_integrations/STATUS_BRIDGE_TELEGRAM_HERMES.md` — Hermes-facing
  note: read one status source instead of repeating a generic summary.
- `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_STATUS_BRIDGE_TASK.md` —
  status-only seed handoff describing the next safe local step.
- `14_context/local_worker_queue/status_bridge_example_output.json` — a committed,
  sanitized `--json` snapshot for reference (all safety flags `false`, `local_only`
  `true`, no secrets).
- `01_projects/runtime_mvp/tests/test_n6_16a_status_bridge_telegram_hermes.py` — the
  N+6.16A test module.

Modified files (3):

- `03_scripts/telegram_status_bot/ghoti_telegram_status_bot.py` — `/status` can read
  the bridge **only** when the runtime config opts in; the bridge is imported as a
  **local Python module** (no new subprocess), and the bot falls back to its
  deterministic built-in status when the bridge is unavailable or not opted in.
- `23_configs/telegram_status_bot.example.json` — four new opt-in keys, all safe by
  default (`status_bridge_enabled: false`, `status_bridge_script_path`,
  `status_bridge_timeout_seconds: 20`, `use_status_bridge_for_telegram_status: false`).
- `23_configs/ghoti_feature_flags.example.json` — three new flags, all `false`
  (`status_bridge_enabled`, `hermes_status_bridge_enabled`,
  `status_bridge_auto_handoff_enabled`). The single enabled flag
  (`telegram_status_commands_enabled`) is preserved.

This report (`14_context/claude_n6_16a_status_bridge_telegram_hermes.md`) is the
12th committed file.

## Telegram bot integration: yes (opt-in, off by default)

The Telegram bot now answers `/status` from the bridge, but **only** when the
runtime config sets both `status_bridge_enabled` and
`use_status_bridge_for_telegram_status` to `true`. Both default `false`, so out of
the box `/status` keeps its deterministic built-in status. When enabled, the bot
imports the bridge as a local module — it adds **no new subprocess of its own**, so
the bot's only subprocess remains the read-only `git` lookup — and it falls back to
the built-in status if the bridge raises or returns nothing. The kill-switch check
still runs first, before any bridge logic. The command surface is unchanged and
remains status-only: `/status`, `/current_task`, `/latest_claude`, `/latest_codex`,
`/help`, and `/flags` are read-only, and the blocked commands (`/run`, `/send`,
`/login`, `/post`, `/buy`, `/trade`, `/delete`, `/mcp`, `/browser`, `/computer`,
`/email`, `/whatsapp`, `/install`, `/clone`, `/shell`, `/exec`, `/deploy`, `/agent`,
`/claude`, `/codex`) stay blocked with no handler.

## Hermes handoff: yes

`--write-hermes-handoff` writes
`14_context/agent_handoff_vault/04_Logs/HERMES_STATUS_BRIDGE_LAST_RUN.md`, a
Hermes-readable note carrying the real `origin/main`, current branch, `n6` test
count, the latest Claude report, the latest Codex audit, and the next recommended
action — the facts Hermes needs so it does not guess. Hermes should read the status
bridge and the handoff note instead of repeating a generic summary. The validation
run that produced this note was treated as residue and removed before commit; the
note is regenerated on demand and is not committed.

## Status packet field verification

Verified values from this worktree (`--json`):

| Field | Value / state |
|-------|---------------|
| `ok` | `true` |
| `milestone` | `N+6.16A` |
| `source` | `status_brain` |
| `hermes_handoff_written` | `false` by default; `true` with `--write-hermes-handoff` |
| `hermes_handoff_path` | `null` by default; the `04_Logs` note path when written |
| `packet.origin_main_short` | `de1cf84` |
| `packet.current_branch` | `feat/ghoti-agent-claude-n6-16a-status-bridge-telegram-hermes` |
| `packet.n6_test_count_known_or_null` | `228` (brain-reported) |
| `packet.computer_use_sandbox_status.mode` | `dry_run_only` |
| `safety.live_browser_used` | `false` |
| `safety.os_input_used` | `false` |
| `safety.external_api_used` | `false` |
| `safety.telegram_control_used` | `false` |
| `safety.mcp_used` | `false` |
| `safety.auto_send_used` | `false` |
| `safety.agent_launch_used` | `false` |
| `safety.network_used` | `false` |
| `safety.secrets_read` | `false` |
| `safety.local_only` | `true` |

`--telegram-safe-json` returns `ok: true`, a non-empty `telegram_safe_text`
(length-bounded ≤ 3500), and `secrets_present: false`. `--markdown` renders a
headed Markdown status. `--write-hermes-handoff` sets `hermes_handoff_written: true`.

## Test totals

- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py"`
  → **Ran 253 tests** — 252 pass, 1 failure (see below).
- The N+6.16A module `test_n6_16a_status_bridge_telegram_hermes.py` contributes
  **25 tests** across 7 classes: pack files exist; bridge CLI (`--json`,
  `--markdown`, `--telegram-safe-json`, safety flags, `--write-hermes-handoff`); bot
  integration (source markers, default-off, enabled-uses-bridge, blocked commands,
  kill-switch first, no new subprocess); config (single-true flag invariant + bot
  bridge keys); safety scan (bridge local/read-only, no `shell=True`, no
  `Invoke-Expression`, no token/chat-id, no secret blobs); docs content; PowerShell
  health-check posture. Run in isolation → **25 OK**.

### The single failure is pre-existing and environmental, not an N+6.16A regression

The one failure is
`test_n6_14a_confined_browser_sandbox_runner.PowerShellCheckTests.test_check_emits_json_disabled_posture`
(`assertIs(data["ok"], True)` → `False`). Root cause, proven:

- This host's PATH `python` shim is broken — invoking `python` returns
  `uv trampoline failed to spawn Python child process / entity not found (os error 2)`.
- N+6.14A's `check_confined_browser_sandbox.ps1` discovers the interpreter with a
  naive `Get-Command python`, finds that broken shim, so its `dry_run_works` field
  becomes `false`, which cascades to `ok: false`. All of that check's existence and
  safety fields remain correct (`runner_exists`, `target_exists`, `flags_exist`
  `true`; `local_browser_action_enabled`, `live_navigation_enabled`,
  `os_input_enabled`, `account_login_enabled`, `captcha_bypass_enabled` all `false`).
- This N+6.16A changeset touches **zero** N+6.14A / confined-browser files
  (verified by name across the diff and untracked set). The failing test file was
  last modified by `385e2c5` (N+6.14A), not by this branch. The same suite reported
  **228 OK** during N+6.15A when the shim still worked.

This is therefore an environmental failure in untracked-by-this-lane N+6.14A code,
not an N+6.16A regression, and per the minimal-change rule it was not "fixed" here.
This lane's own new PowerShell check (`check_status_bridge.ps1`) adds a uv-fallback
interpreter scan specifically so it stays functional under the broken shim, which is
why it returns `ok: true`.

## Runtime / dashboard / PowerShell check result

- `git diff --check` → clean (exit 0).
- `python 03_scripts/status_bridge/ghoti_status_bridge.py --json` → `ok: true`,
  `source: status_brain`, `safety.local_only: true`, `hermes_handoff_written: false`.
- `python 03_scripts/status_bridge/ghoti_status_bridge.py --markdown` → renders a
  headed Markdown status.
- `python 03_scripts/status_bridge/ghoti_status_bridge.py --telegram-safe-json` →
  `ok: true`, non-empty `telegram_safe_text`, `secrets_present: false`.
- `powershell -File 03_scripts/status_bridge/check_status_bridge.ps1` → `ok: true`,
  `bridge_json_works: true`, `local_only: true`, `risky_flags_default_false: true`.
- Telegram bot readiness check (`check_telegram_status_bot.ps1 -NoSecretsRequired`)
  and dry-run start (`start_telegram_status_bot.ps1 -DryRun`) → exercised green via
  the test module (no token required, nothing started).
- `python 03_scripts/ghoti_product_launcher.py --status --json` → `ok: true`.
- `python 03_scripts/public_repo_security_audit.py --run --json` →
  `safe_to_make_public: true`, no blocking findings (the committed example snapshot
  contains no secrets).

## Safety summary

- **Status-only.** The bridge renders status; it starts no agent, opens no network
  connection, calls no external API, controls no browser or desktop, sends nothing,
  installs nothing, and runs no third-party code.
- **One read-only subprocess.** The bridge's only subprocess is the local
  status-brain call, always invoked with an argument list — never a shell string,
  never `Invoke-Expression`. The Telegram bot adds **no** new subprocess: it imports
  the bridge as a local module, so its only subprocess stays the read-only `git`
  lookup.
- **No secrets in the repo.** The bridge needs no Telegram token and no chat id; the
  bot token and allowed chat id continue to live outside the repo and are never
  committed. Output is sanitized: secret-shaped substrings are scrubbed and
  non-printable characters stripped.
- **Off by default.** The three new feature flags and the four new bot config keys
  all default `false`; the single enabled flag stays
  `telegram_status_commands_enabled`. The global kill switch overrides everything and
  is checked first.
- **Approval gates intact.** Nothing here weakens an approval gate. Live control,
  remote command, and agent launch remain future, separately-approved milestones.

## What remains disabled

Remote control, `/run`, live agent launch, MCP, live browser/computer-use, OS-level
click/type, account login automation, email/WhatsApp drafting, auto-send, external
API calls, installs, Docker/VPS runtime, arbitrary shell execution, and third-party
code execution are all still disabled and out of scope. Every risky feature flag
defaults to `false`.

## Direct answers

- **Does the Telegram bot now have status-bridge integration?** Yes — `/status` can
  read the bridge, but only when the config opts in (`status_bridge_enabled` +
  `use_status_bridge_for_telegram_status`, both default `false`); otherwise it keeps
  its deterministic built-in status. It adds no new subprocess and falls back safely.
- **Can a Hermes handoff note be written?** Yes — `--write-hermes-handoff` writes
  `14_context/agent_handoff_vault/04_Logs/HERMES_STATUS_BRIDGE_LAST_RUN.md`
  on demand; it is regenerated, not committed.
- **Useful command now:** `python 03_scripts/status_bridge/ghoti_status_bridge.py --json`.
- **Did Ghoti run any agent, live browser, OS input, Telegram send, MCP, email,
  install, or external API?** No. All are blocked / out of scope; the only subprocess
  is the read-only status-brain (and, in the bot, read-only `git`).
- **Are approval / safety gates intact?** Yes — unchanged and not weakened.

## Codex audit target branch

`audit/ghoti-agent-codex-n6-16a-status-bridge-telegram-hermes`

## Final verdict

IMPLEMENTED_AND_PUSHED — local, offline, read-only status bridge wired to the
Telegram bot (opt-in, default-off) and a Hermes handoff note. The N+6.16A module is
green (25 tests); the full `n6` suite is 252/253, the lone failure being a
pre-existing, environmental broken-`python`-shim issue in untouched N+6.14A code, not
an N+6.16A regression. Security audit clean; all new flags default `false`; no
secrets in the repo.
