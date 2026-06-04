# Ghoti N+6.18A — Operator Dashboard, status-only MVP (Report)

## Summary

N+6.18A ships the first local **operator view** for Ghoti: a small, local-only web
page that shows runtime status at a glance, so the user no longer has to read raw
terminal JSON. It is built with the Python standard library only and is
**status-only** and read-only.

```powershell
pwsh -File 03_scripts/operator_dashboard/start_operator_dashboard.ps1
# then open http://127.0.0.1:8765/
```

The server binds the loopback interface (`127.0.0.1`) only, exposes only GET routes,
runs no commands, starts or stops no processes, mutates no runtime config, reads no
secrets, and loads no external page assets. It aggregates the existing local status
tools (the N+6.16A status bridge, the N+6.17A runtime activation config, the feature
flags, and bounded `wsl`/`ollama` probes) and degrades gracefully if any one is
missing.

## Verdict

IMPLEMENTED_AND_PUSHED.

## Branch / worktree / base / dependency

- Branch: `feat/ghoti-agent-claude-n6-18a-operator-dashboard-status-only`
- Commit message: `feat(ghoti): add status-only operator dashboard`
- Worktree: `C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n6_18a_operator_dashboard_status_only`
- Base commit: `186d472` (N+6.17A, "feat(ghoti): add runtime activation pack")
- `origin/main` at finish: `1660fe2` ("docs(ghoti): record n6.17b runtime activation merge gate")

### Dependency on N+6.17A

This milestone builds on the N+6.17A runtime activation pack (the Python resolver, the
runtime health check, and the WSL Hermes resume preview) and on the N+6.16A status
bridge. At the **start condition** `origin/main` was `a20a14c` and N+6.17A
(`186d472`) was **not** yet on main, so per the start condition this branch was
created from `origin/feat/ghoti-agent-claude-n6-17a-runtime-activation-pack`
(`186d472`). During implementation Codex merged N+6.17A to main, so `origin/main`
advanced to `1660fe2`. Because `186d472` is now an **ancestor of `origin/main`**
(verified: the merge-base of this branch and `origin/main` is exactly `186d472`),
every N+6.18A change is a net-new file on a base that is already in main, and the
future merge to main is clean. No rebase was performed and no existing file was
edited except the one example config the prompt explicitly authorized.

## Files changed

New files (13), plus one authorized config edit:

- `03_scripts/operator_dashboard/ghoti_operator_dashboard.py` — the stdlib-only
  local HTTP server + CLI (`--status-json`, `--check`, `--serve`).
- `03_scripts/operator_dashboard/static/index.html` — the dashboard page (9 cards,
  refresh button, no external assets, no forms that submit actions).
- `03_scripts/operator_dashboard/static/app.js` — fetches `GET /api/status` and
  renders cards with DOM APIs only (no dynamic code execution, no external request,
  no websocket).
- `03_scripts/operator_dashboard/static/styles.css` — local styling, system fonts,
  no CDN, no external font import.
- `03_scripts/operator_dashboard/check_operator_dashboard.ps1` — one-command safety
  check; emits JSON.
- `03_scripts/operator_dashboard/start_operator_dashboard.ps1` — start wrapper;
  `-DryRun` preview, resolves a working Python, binds `127.0.0.1` only, opens the
  browser only with `-OpenBrowser`.
- `03_scripts/operator_dashboard/README.md` — how to run.
- `14_context/operator_dashboard/README.md` — the configuration contract overview.
- `14_context/operator_dashboard/operator_dashboard_status_schema.json` — the
  `/api/status` shape and safe posture.
- `docs/GHOTI_N6_18A_OPERATOR_DASHBOARD_STATUS_ONLY.md` — the milestone doc.
- `14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_OPERATOR_DASHBOARD_TASK.md`
  — status-only seed handoff.
- `01_projects/runtime_mvp/tests/test_n6_18a_operator_dashboard_status_only.py` — the
  N+6.18A test module.
- `14_context/claude_n6_18a_operator_dashboard_status_only.md` — this report.
- `23_configs/ghoti_feature_flags.example.json` — **edited** to add the five
  `operator_dashboard_*` flags, all `false` (the only authorized edit; invariant
  preserved).

## Skills

I can see the installed skills for this repo/session.

- **Skills detected:** project skills `ghoti-status`, `goal`, `prompt-bus`,
  `ultraplan`; plugin skill `anthropic-skills:karpathy-guidelines`; plus a broad
  plugin catalog (`doc-coauthoring`, `docx`, `pptx`, `pdf`, `xlsx`, `mcp-builder`,
  `skill-creator`, `theme-factory`, `web-artifacts-builder`, `consolidate-memory`,
  `code-review`, `security-review`, `verify`, `run`, `simplify`, and others) and many
  deferred live-action MCP connectors (Figma, Gmail, Google Calendar, computer-use,
  Claude-in-Chrome, browser preview).
- **Skills used, and why relevant:** `ghoti-status` to inspect git state, lane locks,
  and the prompt bus before implementing (it confirmed no N+6.x lane-lock conflict);
  `anthropic-skills:karpathy-guidelines` as ongoing coding guardrails. These match the
  task: repo inspection, local automation, and Python/PowerShell/HTML/CSS/JS
  scripting for a small local dashboard.
- **Skills ignored, and why:** every UI/UX-framework and document-format skill
  (`web-artifacts-builder`, `theme-factory`, `docx`, `pptx`, `pdf`, `xlsx`,
  `doc-coauthoring`), `mcp-builder`, and every live-action connector (Figma, Gmail,
  Calendar, computer-use, Claude-in-Chrome, browser preview). The dashboard UI is a
  deliberately minimal, dependency-free local static page; `web-artifacts-builder`
  (React/Tailwind/shadcn via CDN) would have violated the no-external-CDN /
  no-external-JS-CSS rule, and the live-action connectors are irrelevant to a local,
  read-only view and would breach the no-live-action rules of this lane.
- **Did skill instructions affect implementation?** Yes. `karpathy-guidelines` drove
  surgical, additive-only changes (only the one authorized config was edited),
  simplicity (Python standard library only; a small single-purpose server instead of
  a framework), and goal-driven verification (each route and CLI proven by asserting
  its JSON contract, plus an in-process loopback server smoke that confirms GET works
  and POST is rejected). `ghoti-status` confirmed it was safe to proceed (no lane-lock
  conflict). The task's own guidance — do not use UI/UX skills unless actually editing
  the dashboard UI/CSS, and no external CDN — kept the static page hand-written and
  dependency-free.

## Useful commands

```powershell
pwsh -File 03_scripts/operator_dashboard/start_operator_dashboard.ps1 -DryRun
pwsh -File 03_scripts/operator_dashboard/start_operator_dashboard.ps1
pwsh -File 03_scripts/operator_dashboard/check_operator_dashboard.ps1
python 03_scripts/operator_dashboard/ghoti_operator_dashboard.py --status-json
python 03_scripts/operator_dashboard/ghoti_operator_dashboard.py --check --json
```

## Dashboard URL

<http://127.0.0.1:8765/> (loopback only).

## status-json result

`--status-json` returns `ok: true` with `source: status_brain` and every required
section present: `runtime_health`, `python_resolver`, `status_brain`, `status_bridge`,
`telegram_status_readiness`, `hermes_session`, `ollama_gemma`, `computer_use_sandbox`,
`disabled_capabilities`, `next_recommended_action`, and `safety`. The `safety` block
reports `local_only`, `read_only`, and `binds_loopback_only` true and every
live-capability flag false. `origin_main_short` is `1660fe2`. The Hermes card carries
the WSL resume command **preview** only (`run_from_dashboard: false`).

## check result

`--check --json` returns `ok: true` with `no_post_routes`, `no_command_execution`,
`no_shell_true`, `localhost_default`, `binds_loopback_only`, `no_external_assets`,
`no_eval_js`, `static_files_exist`, `dashboard_script_exists`, `feature_flags_present`,
`risky_flags_default_false`, and `only_status_commands_flag_enabled` all true.

## Validation

- `python ... test_n6_18a_operator_dashboard_status_only.py` → **35 tests, 35 pass**.
- Full n6 suite (`unittest discover -p "test_n6_*.py"`) → **307 tests, 1 failure**. The
  single failure is the pre-existing environmental
  `test_n6_14a_confined_browser_sandbox_runner.PowerShellCheckTests.test_check_emits_json_disabled_posture`,
  caused by the broken PATH `python` shim hitting N+6.14A's naive `Get-Command python`
  check (the exact problem the N+6.17A resolver routes around). This lane touches zero
  N+6.14A files, so it is not an N+6.18A regression.
- `--status-json` and `--check --json` → both `ok: true` (see above).
- PowerShell `check_operator_dashboard.ps1` → `ok: true` (`status_json_works` and
  `check_json_works` true); `start_operator_dashboard.ps1 -DryRun` → `dry_run: true`,
  `status_only: true`, opens nothing, starts nothing.
- `public_repo_security_audit.py --run --json` → `failed_checks: 0`,
  `safe_to_make_public: true`, no blocking findings (8 pre-existing warnings only).
- `ghoti_product_launcher.py --status --json`, `--context-pack --json`, and
  `--repo-map --json` → all `ok: true`.
- Live dashboard smoke (real `--serve` on `127.0.0.1:8765`) → all GET endpoints
  `200 ok`, unknown path `404`, `POST /api/status` rejected (`501`), no token leak,
  server stopped cleanly.
- `git diff --check` (working tree) → clean.
- Generated validation residue restored (the launcher context-pack / repo-map
  outputs and the N+6.16A status-bridge log regenerated during the suite); only the
  14 intended paths remain.

## Live endpoint result

A real `--serve` instance was started on `127.0.0.1:8765`, exercised, and then
terminated cleanly (no orphan process):

| Request | Result |
|---------|--------|
| `GET /api/health` | `200`, `ok: true` |
| `GET /api/status` | `200`, `ok: true` |
| `GET /api/disabled-capabilities` | `200`, `ok: true` |
| `GET /api/does-not-exist` | `404` |
| `POST /api/status` | `501` (rejected — no POST handler) |
| token leak in `GET /api/status` body | none |

No installs, no external-repo code execution, no agent launch, no desktop control, no
click/type/hotkey, no live API, and no secret leak.

## Safety — direct answers

- Does the dashboard run commands? **No.** Only GET routes; no command-execution
  endpoint; no `do_POST`; every subprocess is an argument list with a timeout, never a
  shell string, and never `Invoke-Expression`.
- Does it bind externally? **No.** It binds `127.0.0.1` only; a non-loopback host is
  refused unless an explicit opt-in flag is passed, and that flag is left disabled.
- Does it start or stop processes, or mutate runtime config? **No.**
- Does it read secrets? **No.** It reports only whether helper scripts exist and the
  already-sanitized status packet; no token or chat-id value is read.
- Does the page load external assets or call an external API? **No.** No CDN, no
  external CSS/JS/fonts, no external network connection, no websocket, no dynamic code
  execution.
- Are approval gates intact? **Yes.** Nothing here weakens an approval gate.

## What remains disabled

Remote/external access, command execution, process start/stop, runtime-config
mutation, Telegram `/run` and `/send`, live agent launch, Claude/Codex launch, MCP,
live browser/computer-use, OS-level input, account login, email/WhatsApp drafting,
auto-send, external API calls, installs, Docker/VPS runtime, and external-repo code
execution are all still disabled and out of scope. A future public or remote dashboard
is a separate milestone and would require authentication and HTTPS first.

## Codex audit target branch

`audit/ghoti-agent-codex-n6-18a-operator-dashboard-status-only`
