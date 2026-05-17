# Codex N+4.8A Real Audit - External Tool Sandbox + Adapter Discovery

## Audit Metadata

| Field | Result |
| --- | --- |
| Audit branch | `audit/ghoti-agent-codex-n4-8a-external-tool-sandbox-adapter-discovery-real-audit-2` |
| Audit worktree | `C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n4_8a_external_tool_sandbox_real_audit-2` |
| Target branch | `origin/feat/ghoti-agent-claude-n4-8a-external-tool-sandbox-adapter-discovery` |
| Target commit | `79c4bad18e42ec74946c8c63c6228fbf6018e36b` |
| Target commit verified | yes - `ls-remote` and fetched local ref matched |
| Main commit audited as merge base | `238c80cbd8056a1171b8ae57a94c93de0860abbe` |
| No-commit merge | pass - target branch merged into fresh `origin/main` audit worktree with no conflicts |
| Stale-base note | An earlier unsent audit worktree was discarded after `origin/main` advanced to N+4.7A main; final evidence is from this fresh `-2` worktree |
| Claude report | present: `14_context/claude_n4_8a_external_tool_sandbox_adapter_discovery.md` |

## Deliverables

| Deliverable | Result |
| --- | --- |
| `03_scripts/external_tool_sandbox_manager.py` | present |
| `01_projects/runtime_mvp/tests/test_n4_8a_external_tool_sandbox_adapter_discovery.py` | present |
| Adapter: UI-TARS Desktop | present: `02_automation/external_tool_adapters/ui_tars_desktop_adapter.py` |
| Adapter: UI-TARS Model | present: `02_automation/external_tool_adapters/ui_tars_model_adapter.py` |
| Adapter: TheAgency | present: `02_automation/external_tool_adapters/the_agency_adapter.py` |
| Adapter: agent-skills-eval | present: `02_automation/external_tool_adapters/agent_skills_eval_adapter.py` |
| Adapter: Vouch | present: `02_automation/external_tool_adapters/vouch_adapter.py` |
| Approval packet | present: `14_context/external_tools/approval_packets/external_tool_approval_packet_20260517T192949Z.md` |
| Sandbox status file | present: `14_context/external_tools/external_tool_sandbox_status.json` |
| Dashboard card | present: `External Tool Sandbox Truth` |
| Server endpoints | present: status, sync-approved, scan, latest |

## Sandbox / Adapter Validation

| Check | Result |
| --- | --- |
| `python 03_scripts/external_tool_sandbox_manager.py --status --json` | pass, exit 0, valid JSON |
| `python 03_scripts/external_tool_sandbox_manager.py --json` | pass, exit 0, valid JSON |
| Unknown repo slug rejection | pass, `evil/not-approved` rejected as not in approved catalog |
| `--sync-approved --json` | pass, 5 cloned, 0 failed, degraded false |
| `--scan --json` | pass, 5 scanned |
| `--generate-adapters --json` | pass, 5 adapter stubs |
| `--write-approval-packet --json` | pass, approval packet written |
| Installs performed | false |
| External repo code executed | false |
| Runtime wiring | none |
| Desktop control enabled | false |
| Live API enabled | false |
| Human approval required | true |

## Cloned Repo Result

| Approved Repo | Clone Result |
| --- | --- |
| `bytedance/UI-TARS-desktop` | cloned shallow under ignored sandbox; commit `7986f5aea500c4535c0e55dc5c5d0cda73767c45`; completion marker present |
| `bytedance/UI-TARS` | cloned shallow under ignored sandbox; commit `582f3a7ea5d285ee8ed9e2e84048d1ab01453c49`; completion marker present |
| `the-agency-ai/the-agency` | cloned shallow under ignored sandbox; commit `dd2430bfe62c2e27c4e678b6879faffd1c2b372a`; completion marker present |
| `darkrishabh/agent-skills-eval` | cloned shallow under ignored sandbox; commit `b60eebe3c6edaa917a284e13b9b0e9fa00f1c957`; completion marker present |
| `vouch-protocol/vouch` | cloned shallow under ignored sandbox; commit `1b37c3ef661bd1c4ed87c5349e51be7ce5038bcc`; completion marker present |
| Git ignore containment | pass - `21_repos/third_party/sandboxed/` is ignored and not staged |

## Static Validation

| Command | Result |
| --- | --- |
| `git diff --check` | pass |
| `git diff --cached --check` | pass |
| `git diff --check HEAD` | pass |
| `git show --check --stat HEAD` | pass |
| `git show --check --stat origin/feat/ghoti-agent-claude-n4-8a-external-tool-sandbox-adapter-discovery` | pass |
| `node --check 01_projects/dashboard_mvp/server.js` | pass |
| `node --check 01_projects/dashboard_mvp/public/app.js` | pass |
| Python AST for manager, adapters, and N+4.8A tests | pass |
| Status JSON parse | pass |

## Dashboard / Endpoint Validation

| Check | Result |
| --- | --- |
| `GET /api/external-tool-sandbox/status` | pass, HTTP 200, `ok: true` |
| `POST /api/external-tool-sandbox/scan` | pass, HTTP 200, `ok: true`, scanned 5 |
| `GET /api/external-tool-sandbox/latest` | pass, HTTP 200, `ok: true` |
| 500s | none observed |
| Method/pathname ReferenceError | none observed |
| Installs via endpoint smoke | false |
| External repo execution via endpoint smoke | false |

## Regression Validation

| Suite | Result |
| --- | --- |
| N+4.8A external tool sandbox tests | pass, 35/35 |
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
| Total unit/regression tests | pass, 292/292 |

## Downstream Checks

| Command | Result |
| --- | --- |
| `python 03_scripts/ghoti_product_launcher.py --status --json` | pass, exit 0 |
| `python 03_scripts/parallel_agent_relay.py --status --json` | pass, exit 0 |
| `python 03_scripts/local_memory_compression_bridge.py --json` | pass, exit 0, `external_api_used: false` |
| `python 03_scripts/repo_skill_plugin_intake.py --validate-config` | pass, 22 entries validated with runtime/live flags false |
| `python 03_scripts/ghoti_readiness_check.py --status` | pass, supervised MVP score 100, categories 9/9 |
| `python 03_scripts/supervised_content_mvp_runner.py --validate-latest` | pass, supervised MVP score 100, production public release ready false |
| `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1` | pass, exit 0, runtime MVP checks passed |
| `pwsh -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1` | pass, exit 0, dashboard MVP checks passed |

## Safety Summary

| Check | Result |
| --- | --- |
| No `npm install` / `pnpm install` / `pip install` performed | pass |
| No external repo code executed | pass |
| No UI-TARS started | pass |
| No desktop control enabled | pass |
| No live APIs/accounts | pass |
| No runtime wiring from adapters into operator | pass |
| Adapter stubs import external repo packages | no |
| Adapters require human approval | yes |
| Cloned repos committed | no - ignored sandbox only |
| Secrets/API keys in changed N+4.8A files | none found |
| `shell:true` | none found |
| Unknown repo slugs rejected | yes |
| Approval gates intact | yes |

## Screenshot / Terminal Behavior

| Check | Result |
| --- | --- |
| Blocking `.NET` popup | not observed |
| Weird clipboard command | not observed |
| Blocking `node.exe` window | not observed |
| Lingering validation process tied to audit worktree | none found |

## Final Verdict

CLEAN PASS

## Exact Next Recommended Action

Claude can merge N+4.8A to `main`, then run the final main audit for the external tool sandbox and adapter discovery milestone.
