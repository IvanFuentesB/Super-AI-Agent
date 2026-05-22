# Daily Operator Guide

## What Ghoti is

Ghoti / Super-AI-Agent is a local-first supervised operator control center. It
helps Ivan coordinate local status checks, compact memory, coding workflows,
safe content demos, research plans, and future computer-use tooling from one
truthful dashboard. It is not autonomous, it does not post, and it does not run
live providers or account actions without explicit human approval.

Current baseline: N+5.3B clean/product-ready at
`6628e6f6fc91921225182a66ebf927982bd5464d`.

## Launch

```powershell
python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
```

Dashboard URL:

```text
http://127.0.0.1:3210
```

## What to check first

1. Open the dashboard and read Start Here / Daily Operator.
2. Confirm Status Truth still says N+5.3B clean/product-ready.
3. Confirm Hermes, Ollama/Gemma, Obsidian memory, UI-TARS, adapters, external
   sandbox, public audit, and readiness status are truthful.
4. Run a smoke check before relying on the dashboard.
5. Review the latest relevant report under `14_context/`.

## Daily commands

```powershell
python 03_scripts/ghoti_product_launcher.py --status --json
python 03_scripts/ghoti_product_launcher.py --smoke --json
python 03_scripts/supervised_content_mvp_runner.py --validate-latest
python 03_scripts/public_repo_security_audit.py --run --json
python 03_scripts/model_council_tool_intake.py --scan --json
python 03_scripts/ghoti_product_launcher.py --stop-dashboard
```

The stop command targets only the launcher-recorded PID. Do not use broad
process kills.

## Latest reports

Most milestone reports live under `14_context/`. Useful starting points:

- `14_context/codex_n5_3a_main_merge_product_finish_local_mvp.md`
- `14_context/codex_n5_3a_product_finish_remote_clean_audit.md`
- audit branch report: `14_context/codex_n5_3b_final_main_full_product_finish.md`

If the N+5.3B final report is not present on `origin/main`, inspect the pushed
audit branch `audit/ghoti-agent-codex-n5-3b-final-main-full-product-finish`.

## local_demo fallback

`local_demo fallback` means Ghoti keeps the workflow local and truthful when a
real local model is unavailable. In the current baseline, Ollama is available
but a Gemma model is missing, so memory compression/status tools report
`fallback_mode=local_demo` instead of pretending Gemma is active.

## Hermes is currently allowed

Hermes is currently allowed to be checked with safe local status probes only.
Known truth:

- WSL Ubuntu is present.
- Hermes path: `/home/ai_sandbox/.local/bin/hermes`
- Hermes version: `Hermes Agent v0.14.0`
- Browser/Playwright is degraded/not claimed unless separately verified.
- Codex provider support inside Hermes is pending/not proven.

Do not run Hermes setup, provider config, Telegram setup, token flows, or live
APIs from this daily workflow.

## UI-TARS is currently allowed

UI-TARS is currently observation-only. Allowed:

- dry-run observation status
- local observation packets
- approval-gated read-only capture in a later audited flow

Not allowed:

- click
- type
- hotkeys
- desktop control
- UI-TARS runtime launch
- external repo code execution

## What must remain manual

- Hermes provider setup
- Telegram connection and tokens
- real Gemma model pull/install
- Ruflo source/runtime enablement
- Graphify runtime integration
- browser/Playwright repair and verification
- public release human review
- any live provider, account, posting, money, trading, or legal action

## What not to do

- Do not commit `.env`, API keys, tokens, cookies, browser sessions, local
  credentials, or human private files.
- Do not run bot/captcha/cloak bypass workflows.
- Do not create fake engagement or spam workflows.
- Do not scrape credentials or browser sessions.
- Do not enable autonomous posting.
- Do not enable autonomous money/trading/legal actions.
- Do not wire external repos into runtime without a new audited milestone.
- Do not mutate the primary worktree; no primary worktree mutation except
  read-only inspection.
- Do not run live providers/tokens setup flows.

## Troubleshooting

### dashboard won't start

Run:

```powershell
python 03_scripts/ghoti_product_launcher.py --status --json
```

Check whether the state file records a PID and whether the dashboard reports
`dashboard_running=true`.

### port busy

The launcher defaults to port 3210. Run smoke/status first. If the port is used
by something not recorded by the launcher, stop that process manually only after
you identify that it belongs to this workspace.

### WSL/Hermes not found

Use only safe probes:

```powershell
wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; command -v hermes || true"
wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --version || true"
```

Do not run setup or provider config during daily checks.

### Ollama/Gemma missing

Run:

```powershell
python 03_scripts/local_memory_compression_bridge.py --status --json
```

If Gemma is missing, expect `local_demo fallback`. That is a safe degraded mode,
not a failure.

### public audit warnings

Run:

```powershell
python 03_scripts/public_repo_security_audit.py --run --json
```

The N+5.3B baseline has 0 blockers and 7 warnings. Warnings still require human
review before any public release claim.

### generated residue

Some status probes may update generated JSON timestamps. Inspect diffs before
committing. Restore generated probe residue when it is not an intended source
change.

### launcher PID stale

Run:

```powershell
python 03_scripts/ghoti_product_launcher.py --stop-dashboard
python 03_scripts/ghoti_product_launcher.py --status --json
```

The launcher stops only the recorded PID. If status still looks stale, inspect
the state file and process manually; do not kill broad node/python/pwsh process
sets.

## Stop and cleanup

```powershell
python 03_scripts/ghoti_product_launcher.py --stop-dashboard
python 03_scripts/ghoti_product_launcher.py --status --json
git status --short
```

End a daily session with no recorded launcher PID, no unexpected generated
residue, and no primary worktree mutation.
