# Codex N+4.7A Real Audit - One-Command Product Launcher Demo Smoke

## Audit Metadata

| Field | Result |
| --- | --- |
| Audit branch | `audit/ghoti-agent-codex-n4-7a-one-command-product-launcher-demo-smoke-real-audit` |
| Audit worktree | `C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n4_7a_one_command_product_launcher_real_audit` |
| Target branch | `origin/feat/ghoti-agent-claude-n4-7a-one-command-product-launcher-demo-smoke` |
| Target commit | `d5a218f67c5f2ffca8109be8d1b2b49b27d40338` |
| Target commit verified | yes - `ls-remote` and local fetched ref matched |
| Base main audited | `64759086b0ca7e63d0616753b998e32f07ce2e68` |
| No-commit merge | pass - target branch merged into `origin/main` audit branch with no conflicts |
| Claude report | present: `14_context/claude_n4_7a_one_command_product_launcher_demo_smoke.md` |

## Changed Files

| Path | Audit Result |
| --- | --- |
| `03_scripts/ghoti_product_launcher.py` | new launcher present |
| `01_projects/runtime_mvp/tests/test_n4_7a_one_command_product_launcher_demo_smoke.py` | new 25-test suite present |
| `01_projects/dashboard_mvp/public/index.html` | Ghoti Local Launcher Truth card present |
| `14_context/claude_n4_7a_one_command_product_launcher_demo_smoke.md` | implementation report present |

## Launcher CLI Validation

| Check | Result |
| --- | --- |
| `--status` | supported |
| `--json` | supported |
| `--start-dashboard` | supported |
| `--stop-dashboard` | supported |
| `--smoke` | supported |
| `--open-dashboard` | supported and optional |
| `--run-demo-smoke` | supported |
| `--port` | supported |
| `--timeout-seconds` | supported |
| `python 03_scripts/ghoti_product_launcher.py --status --json` | pass, exit 0, valid JSON |
| `python 03_scripts/ghoti_product_launcher.py --json` | pass, exit 0, valid JSON |
| `python 03_scripts/ghoti_product_launcher.py --smoke --json` | pass, exit 0, valid JSON |
| Dashboard URL | `http://127.0.0.1:3210` |
| State file | `01_projects/dashboard_mvp/runtime_data/ghoti_product_launcher_state.json`, repo-local |
| Browser opening | off by default; only attempted when `--open-dashboard` is explicitly passed |
| Fixed argv / shell behavior | pass - launcher uses fixed argv with `shell=False` |
| Stop behavior | pass - stop targets recorded PID, not broad `node.exe` taskkill |

## Live Launcher Smoke

| Step | Result |
| --- | --- |
| `python 03_scripts/ghoti_product_launcher.py --start-dashboard --json` | pass, exit 0, `ok: true`, PID `19256`, URL `http://127.0.0.1:3210`, `opened_browser: false` |
| `python 03_scripts/ghoti_product_launcher.py --smoke --json` | pass, exit 0, `ok: true`, `all_passed: true`, `no_500: true`, `no_ref_error: true` |
| Product endpoint: `GET /api/product-control/status` | pass, HTTP 200, `ok: true` |
| Product endpoint: `POST /api/product-control/create-relay-pair` | pass, HTTP 200, `ok: true` |
| Product endpoint: `POST /api/product-control/run-content-studio-demo` | pass, HTTP 200, `ok: true` |
| Product endpoint: `GET /api/product-control/latest` | pass, HTTP 200, `ok: true` |
| `python 03_scripts/ghoti_product_launcher.py --stop-dashboard --json` | pass, exit 0, `ok: true`, stopped recorded PID only |
| Post-stop status | pass, `dashboard_running: false` |
| Method/pathname ReferenceError | not observed |
| Path escape | not observed |

## Static Validation

| Command | Result |
| --- | --- |
| `git diff --check` | pass |
| `git diff --cached --check` | pass |
| `git diff --check HEAD` | pass |
| `git show --check --stat HEAD` | pass |
| `git show --check --stat origin/feat/ghoti-agent-claude-n4-7a-one-command-product-launcher-demo-smoke` | pass |
| `node --check 01_projects/dashboard_mvp/server.js` | pass |
| `node --check 01_projects/dashboard_mvp/public/app.js` | pass |
| Python AST for launcher/test files | pass |

## Regression Validation

| Suite | Result |
| --- | --- |
| N+4.7A launcher tests | pass, 25/25 |
| N+4.6A product dashboard tests | pass, 33/33 |
| N+4.5A relay tests | pass, 68/68 |
| N+4.4D preview containment tests | pass, 18/18 |
| N+4.4C recipe runner tests | pass, 16/16 |
| N+4.4B action center tests | pass, 17/17 |
| N+4.4A desktop operator tests | pass, 20/20 |
| N+4.3A content studio tests | pass, 15/15 |
| N+4.2A memory/intake tests | pass, 26/26 |
| N+4.1 reliability tests | pass, 19/19 |
| Total unit/regression tests | pass, 257/257 |

## Downstream Checks

| Command | Result |
| --- | --- |
| `python 03_scripts/parallel_agent_relay.py --status --json` | pass, exit 0 |
| `python 03_scripts/local_memory_compression_bridge.py --json` | pass, exit 0, local-only/external API false |
| `python 03_scripts/repo_skill_plugin_intake.py --validate-config` | pass, 22 entries validated with blocked runtime/live flags false |
| `python 03_scripts/ghoti_readiness_check.py --status` | pass, supervised MVP score 100, categories 9/9 |
| `python 03_scripts/supervised_content_mvp_runner.py --validate-latest` | pass, supervised MVP score 100, production public release ready false |
| `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1` | pass, exit 0, runtime MVP checks passed |
| `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1` | pass, exit 0, dashboard MVP checks passed |

## Dashboard Validation

| Check | Result |
| --- | --- |
| Ghoti Local Launcher Truth card | present |
| One-command launcher label | present |
| Start Dashboard label | present |
| Stop Dashboard label | present |
| Product Smoke Test label | present |
| Open Dashboard Optional label | present |
| Run Demo Smoke label | present |
| No External API label | present |
| No Live Account Actions label | present |

## Safety Validation

| Check | Result |
| --- | --- |
| No `shell: true` in launcher path | pass |
| Launcher process creation | fixed argv, `shell=False` |
| Stop-dashboard behavior | recorded PID only; no broad `taskkill /IM node.exe` |
| Browser open | optional and localhost-only behind `--open-dashboard` |
| External API use | not enabled |
| Live account/posting/money/trading actions | not enabled |
| Autonomous Claude/Codex launch | not enabled |
| Secrets/API keys in changed N+4.7A files | none found |
| Approval gates | intact |
| Generated runtime/smoke artifacts | left untracked and not staged |

## Screenshot / Terminal Behavior

| Check | Result |
| --- | --- |
| Blocking `.NET` popup | not observed |
| Weird `runtime-desktop-clipboard-checkruntime-desktop-clipboard-check` command | not observed |
| Blocking `node.exe` window | not observed |
| Lingering validation process tied to audit worktree | none found after checks |

## Direct Answers

| Question | Answer |
| --- | --- |
| Is the one-command launcher implemented? | yes |
| Does it print a dashboard URL? | yes, `http://127.0.0.1:3210` |
| Is `--open-dashboard` optional/off by default? | yes |
| Does product smoke cover the four product-control endpoints? | yes |
| Does start/smoke/stop work live? | yes |
| Does stop-dashboard kill only the recorded PID? | yes |
| Does this use external APIs? | no |
| Does this enable live account/posting/money/trading actions? | no |
| Does this launch Claude/Codex autonomously? | no |
| Are approval gates intact? | yes |
| Is this full Ghoti production 100%? | no - this is still local-only, approval-gated product smoke/demo infrastructure |

## Final Verdict

CLEAN PASS

## Exact Next Recommended Action

Claude can merge N+4.7A to `main`, then run a final main audit for the one-command product launcher stack.
