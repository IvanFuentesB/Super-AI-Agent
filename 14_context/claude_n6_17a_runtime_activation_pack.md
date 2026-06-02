# Ghoti N+6.17A — Runtime Activation Pack (Report)

## Summary

N+6.17A makes Ghoti easier to actually *use* from PowerShell, Telegram, and WSL
Hermes by adding a small set of local PowerShell wrappers in
`03_scripts/runtime_activation/`. Each wrapper is local and read-only by default,
emits a single JSON object, and makes any external call with an argument array (no
`Invoke-Expression`, no `shell=True`). One safe command per everyday action:

```powershell
pwsh -File 03_scripts/runtime_activation/check_ghoti_runtime.ps1
```

The pack's headline fix: bare `python` is broken on this host (a uv trampoline that
fails to spawn its Python child), so every wrapper that needs Python resolves a
*working* interpreter first via `ghoti_python_resolver.ps1`, then drives the existing
N+6.16A status bridge / status-only Telegram bot with it.

This is status-only. There is no remote control, no `/run`, no live agent launch, no
MCP, no live browser/computer-use, no OS click/type, no account login, no
email/WhatsApp, no auto-send, no external API, and no installs. No real Telegram
token or chat id lives in the repo, and the local runtime config the enable script
writes lives outside the repo and is never committed.

## Verdict

IMPLEMENTED_AND_PUSHED.

## Branch / worktree / base

- Branch: `feat/ghoti-agent-claude-n6-17a-runtime-activation-pack`
- Worktree: `C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n6_17a_runtime_activation_pack`
- Base commit: `023a5bf` (N+6.16A, "feat(ghoti): add status bridge for Telegram and Hermes")
- Current `origin/main`: `a20a14c` ("docs(ghoti): record n6.16b status bridge merge gate")

## Dependency on N+6.16A

This milestone builds directly on the N+6.16A status bridge
(`03_scripts/status_bridge/ghoti_status_bridge.py`): `write_hermes_status_handoff.ps1`
calls it with `--write-hermes-handoff`, and `enable_status_bridge_runtime_config.ps1`
turns on the bot's two bridge flags. During this session `origin/main` advanced to
`a20a14c`, which already merged N+6.16A (implementation commit `023a5bf` via merge
`20aa44e`). This branch is based on `023a5bf`; because `023a5bf` is an ancestor of
`a20a14c`, the merge-base of this branch and `origin/main` is `023a5bf`, every
N+6.17A change is a net-new file (no existing file is edited), and the future merge
to main is clean. No rebase was performed.

## Files changed

New files (14), zero modified:

- `03_scripts/runtime_activation/ghoti_python_resolver.ps1` — resolve a working
  Python interpreter, skipping the broken PATH `python`/`python3`/`py -3` shim.
- `03_scripts/runtime_activation/check_ghoti_runtime.ps1` — one-command runtime
  health check (Python, origin/main, status brain + bridge + bot presence, secret
  files existence only, WSL/ollama/gemma probe).
- `03_scripts/runtime_activation/write_hermes_status_handoff.ps1` — resolve Python
  and call the status bridge with `--write-hermes-handoff`; `-DryRun` previews.
- `03_scripts/runtime_activation/enable_status_bridge_runtime_config.ps1` — turn on
  the two Telegram status-bridge flags in the LOCAL outside-repo runtime config;
  `-DryRun` previews and writes nothing.
- `03_scripts/runtime_activation/start_ghotideepbot_status_only.ps1` — start the
  status-only bot with the resolved Python; `-DryRun` previews the would-run command.
- `03_scripts/runtime_activation/resume_wsl_hermes_session.ps1` — preview (default)
  or `-Run` the exact command that resumes WSL Hermes session
  `20260601_081506_d35c70`.
- `03_scripts/runtime_activation/README.md` — how to run each wrapper, safely.
- `14_context/runtime_activation/README.md` — the configuration contract overview.
- `14_context/runtime_activation/runtime_activation_status_schema.json` — the shape
  and safe-posture of the health-check JSON.
- `23_configs/runtime_activation.example.json` — example activation config; only
  PATHS to outside-repo secrets, never a token or chat id.
- `docs/GHOTI_N6_17A_RUNTIME_ACTIVATION_PACK.md` — the milestone doc.
- `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_RUNTIME_ACTIVATION_TASK.md`
  — status-only seed handoff describing the next safe local step.
- `01_projects/runtime_mvp/tests/test_n6_17a_runtime_activation_pack.py` — the
  N+6.17A test module (19 tests).
- `14_context/claude_n6_17a_runtime_activation_pack.md` — this report.

## Useful commands

```powershell
pwsh -File 03_scripts/runtime_activation/ghoti_python_resolver.ps1
pwsh -File 03_scripts/runtime_activation/check_ghoti_runtime.ps1
pwsh -File 03_scripts/runtime_activation/write_hermes_status_handoff.ps1
pwsh -File 03_scripts/runtime_activation/enable_status_bridge_runtime_config.ps1 -DryRun
pwsh -File 03_scripts/runtime_activation/start_ghotideepbot_status_only.ps1 -DryRun
pwsh -File 03_scripts/runtime_activation/resume_wsl_hermes_session.ps1
```

## Python resolver result

`ghoti_python_resolver.ps1` returns `ok: true`. It skips the broken PATH shim and
resolves the uv-managed CPython:

- `executable`: `C:\Users\ai_sandbox\AppData\Roaming\uv\python\cpython-3.13.12-windows-x86_64-none\python.exe`
- `source`: `uv:<that path>`
- `tried`: `["python", "python3", "py -3", "<uv python.exe>"]`
- `error`: `null`

## Runtime check result

`check_ghoti_runtime.ps1` returns `ok: true` with `python_ok: true`,
`status_brain_ok: true`, `status_bridge_ok: true`,
`telegram_bot_scripts_present: true`, `hermes_wsl_available: true`,
`ollama_available: true`, `gemma_available: true`,
`same_session_id: 20260601_081506_d35c70`,
`runtime_config_path: C:/Users/ai_sandbox/.ghoti_runtime/telegram_status_config.json`,
`local_only: true`, and `live_browser_enabled` / `telegram_control_enabled` /
`mcp_enabled` / `auto_send_enabled` all `false`. `telegram_secret_files_present` is
`false` on this host because the allowed-chat-id file is not present yet (the check
reads only whether the secret files exist, never their values).

## Telegram status-bridge activation result

`enable_status_bridge_runtime_config.ps1 -DryRun` returns `ok: true`,
`dry_run: true`, `status_bridge_enabled: true`,
`use_status_bridge_for_telegram_status: true`, `config_outside_repo: true`,
`secrets_written: false`, and `config_written: false`. The real (non-dry-run) write
targets `C:/Users/ai_sandbox/.ghoti_runtime/telegram_status_config.json` outside the
repo and stores only file PATHS to the token and chat-id files — never a token or a
chat id. The real write was NOT performed in this lane; only the preview was
exercised. Telegram stays status-only: there is no `/run` and no live control.

## Hermes resume command

`resume_wsl_hermes_session.ps1` previews (and, with `-Run`, executes) exactly:

```bash
wsl -d Ubuntu --cd /mnt/c/Users/ai_sandbox/Documents/AI_Managed_Only -- bash -lc 'export PATH=/home/ai_sandbox/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin; hermes --resume 20260601_081506_d35c70'
```

The Windows Hermes Desktop app was deleted; WSL Hermes is the only Hermes
installation now, and this resumes the same session. The default is preview-only
(`run: false`); `-Run` was NOT used in this lane.

## Validation

- `python ... test_n6_17a_runtime_activation_pack.py` → **19 tests, 19 pass**.
- Full n6 suite (`unittest discover -p "test_n6_*.py"`) → **272 tests, 1 failure**.
  The single failure is `test_n6_14a_confined_browser_sandbox_runner.PowerShellCheckTests.test_check_emits_json_disabled_posture`,
  a pre-existing environmental failure caused by the broken PATH `python` shim in
  N+6.14A's naive `Get-Command python` check — the exact problem this pack's resolver
  is designed to route around. This lane touches zero N+6.14A files, so it is not an
  N+6.17A regression. (Fixing that older check is out of scope for this additive lane.)
- Each of the six wrappers was run and emits a single valid JSON object in its
  preview/dry-run mode; nothing live was started.
- `git diff --check` (staged) and `git show --check` (HEAD) report no whitespace or
  conflict-marker errors.
- Validation residue (the bridge's `HERMES_STATUS_BRIDGE_LAST_RUN.md`, regenerated by
  the N+6.16A test during the full-suite run) was removed; only the 14 intended files
  are committed.

## Skills

- **Skills detected this session:** `ghoti-status` (project), `ultraplan` (project),
  `goal` (project), and `anthropic-skills:karpathy-guidelines` (plugin). Many
  live-action MCP connectors were also available (Figma, Gmail, Google Calendar,
  computer-use, Claude-in-Chrome, browser preview) as deferred tools.
- **Skills used, and why relevant:** `ghoti-status` to orient on branch, HEAD,
  active lane locks, and prompt-bus state before editing; `ultraplan` + `goal` to
  plan the milestone and execute the current prompt; `karpathy-guidelines` as ongoing
  behavioral guardrails. These match the task: repo inspection, local automation,
  PowerShell/Python scripting, agent handoff, and documentation.
- **Skills ignored, and why:** every UI/UX/design and live-action connector
  (Figma, Gmail, Calendar, computer-use, Claude-in-Chrome, browser preview). They are
  irrelevant to a local, read-only PowerShell/Python pack and using them would
  violate the no-live-action rules of this lane.
- **Did skill instructions change the implementation?** Yes. `karpathy-guidelines`
  reinforced surgical, additive-only changes (no existing file is edited), simplicity
  (small single-purpose wrappers), and goal-driven verification (each wrapper proven
  by asserting its JSON contract); it also nudged the enable script to be idempotent
  and non-destructive (preserve an existing config, flip only the two bridge flags)
  and to default the outside-repo write / bot start / Hermes resume to preview.

## Safety — what remains disabled

Remote control, `/run`, live agent launch, MCP, live browser/computer-use, OS-level
click/type, account login automation, email/WhatsApp drafting, auto-send, external
API calls, installs, Docker/VPS runtime, and third-party code execution are all still
disabled and out of scope. No secret value is ever read or written; only file PATHS
to outside-repo secrets appear anywhere in the repo. Approval gates are unchanged.

## Codex audit target branch

`audit/ghoti-agent-codex-n6-17a-runtime-activation-pack`
