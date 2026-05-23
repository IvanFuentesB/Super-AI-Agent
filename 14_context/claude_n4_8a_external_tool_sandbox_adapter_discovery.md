# N+4.8A — External Tool Sandbox + Adapter Discovery MVP

## Identifiers

| Field | Value |
|-------|-------|
| Milestone | N+4.8A — External Tool Sandbox + Adapter Discovery MVP |
| Branch | feat/ghoti-agent-claude-n4-8a-external-tool-sandbox-adapter-discovery |
| Worktree | C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\claude_n4_8a_external_tool_sandbox_adapter_discovery |
| Base main | 64759086b0ca7e63d0616753b998e32f07ce2e68 |
| Stacked on | N+4.7A one-command launcher (d5a218f), merged via b531ab3 |

## Files changed

| File | Change |
|------|--------|
| `03_scripts/external_tool_sandbox_manager.py` | NEW — safe clone + static-scan manager |
| `02_automation/external_tool_adapters/*.py` | NEW — 5 safe adapter stubs + `__init__.py` |
| `01_projects/dashboard_mvp/server.js` | +4 `/api/external-tool-sandbox/*` endpoints |
| `01_projects/dashboard_mvp/public/index.html` | +`external-tool-sandbox-truth` dashboard card |
| `01_projects/dashboard_mvp/public/app.js` | +`attachExternalToolSandbox` read-only handler |
| `01_projects/runtime_mvp/tests/test_n4_8a_*.py` | NEW — 35-test suite |
| `14_context/external_tools/external_tool_sandbox_status.json` | NEW — sandbox status snapshot |
| `14_context/external_tools/approval_packets/external_tool_approval_packet_*.md` | NEW — human approval packet |
| `14_context/claude_n4_8a_*.md` | NEW — this report |

The cloned external repos live under `21_repos/third_party/sandboxed/` and are
**not committed** — the repo `.gitignore` already ignores `21_repos/third_party/*`.

## Repos cloned

This is the first Ghoti milestone to actually clone external repos. All 5 approved
public repos were shallow-cloned (`git clone --depth 1`) for **static inspection
only**. No degradation — 5/5 cloned.

| Repo | Clone status | Commit | Clone path |
|------|--------------|--------|------------|
| bytedance/UI-TARS-desktop | cloned | 7986f5aea500 | 21_repos/third_party/sandboxed/ui_tars_desktop |
| bytedance/UI-TARS | cloned | 582f3a7ea5d2 | 21_repos/third_party/sandboxed/ui_tars_model |
| the-agency-ai/the-agency | cloned | dd2430bfe62c | 21_repos/third_party/sandboxed/the_agency |
| darkrishabh/agent-skills-eval | cloned | b60eebe3c6ed | 21_repos/third_party/sandboxed/agent_skills_eval |
| vouch-protocol/vouch | cloned | 1b37c3ef661b | 21_repos/third_party/sandboxed/vouch |

Note: an initial clone attempt hit the Windows `MAX_PATH` (filename-too-long) limit
on the 2 deepest-nested repos at checkout. This was resolved by cloning with
`git -c core.longpaths=true clone --depth 1` (a per-command Windows git option — no
global config change). Final result: 5/5 cloned. The manager degrades truthfully
(per-repo `clone_status`, `degraded` flag) if any clone ever fails.

## Static scan summary

`--scan` read each repo's README / package files / docs / LICENSE (files only —
nothing executed):

| Repo | Ecosystem | Install req (NOT installed) | API key req | Desktop-control risk | License |
|------|-----------|------------------------------|-------------|----------------------|---------|
| UI-TARS Desktop | node/js-ts | npm, pnpm | yes | YES | Apache License |
| UI-TARS Model | (assets) | none detected | yes | YES | Apache License |
| TheAgency | node/js-ts | npm | no | no | MIT License |
| agent-skills-eval | node/js-ts | npm | yes | no | MIT License |
| Vouch Protocol | python | pip | yes | no | Apache License 2.0 |

No install was performed. No external repo code was executed.

## Generated adapter stubs

5 safe Ghoti-local adapter stubs generated under `02_automation/external_tool_adapters/`:
`ui_tars_desktop_adapter.py`, `ui_tars_model_adapter.py`, `the_agency_adapter.py`,
`agent_skills_eval_adapter.py`, `vouch_adapter.py`.

Each stub: local-only; imports NO external repo package (stdlib `json` only);
exposes `status()`, `capabilities()`, `safety_gates()`; runs no external code,
no desktop actions, no API calls; reports `requires_human_approval = true` and
`wired = false`.

## Approval packet

`14_context/external_tools/approval_packets/external_tool_approval_packet_20260517T192949Z.md`
— a per-tool human review packet (clone status, scan findings, install/API/desktop
risk, and a per-tool approval checklist). No tool is wired until a human checks the boxes.

## Dashboard result

New **External Tool Sandbox Truth** card in the Product Control Center section. All
15 required labels present: External Tool Sandbox, UI-TARS Desktop, UI-TARS Model,
TheAgency, agent-skills-eval, Vouch Protocol, Clone Status, Static Scan Only, No
Install Yet, No Runtime Wiring, No Desktop Control Yet, No Live APIs, Human Approval
Required, Adapter Stubs Generated, Approval Packet Required.

4 server endpoints added: `GET /api/external-tool-sandbox/status`,
`POST /api/external-tool-sandbox/sync-approved`, `POST /api/external-tool-sandbox/scan`,
`GET /api/external-tool-sandbox/latest`. Fixed argv, `shell:false`, timeouts; the
sync/scan endpoints pass NO user-supplied repo slug — only the fixed approved catalog.

## Validation table (real output)

| Check | Result |
|-------|--------|
| `git diff --check` | clean |
| `node --check server.js` | OK |
| `node --check public/app.js` | OK |
| `external_tool_sandbox_manager.py --status --json` | OK |
| `external_tool_sandbox_manager.py --json` | OK |
| `external_tool_sandbox_manager.py --sync-approved --json` | OK — 5/5 cloned, degraded=false |
| `external_tool_sandbox_manager.py --scan --json` | OK — 5 scanned, installs_performed=false |
| `external_tool_sandbox_manager.py --generate-adapters --json` | OK — 5 adapters |
| `external_tool_sandbox_manager.py --write-approval-packet --json` | OK — packet written |
| `test_n4_8a_external_tool_sandbox_adapter_discovery` | OK — 35/35 |
| `test_n4_7a_one_command_product_launcher_demo_smoke` | OK — 25/25 |
| `test_n4_6a_productized_dashboard_control_center_usability` | OK — 33/33 |
| `test_n4_5a_parallel_agent_relay_command_center` | OK — 68/68 |
| `test_n4_4d_preview_path_containment_fix` | OK — 18/18 |
| `test_n4_4c_desktop_operator_recipe_runner_preview_polish` | OK — 16/16 |
| `test_n4_4b_desktop_operator_dashboard_action_center` | OK — 17/17 |
| `test_n4_4a_desktop_operator_control_plane` | OK — 20/20 |
| `test_n4_3a_supervised_content_studio_demo` | OK — 15/15 |
| `test_n4_2a_local_memory_intake` | OK — 26/26 |
| `test_n4_1_runtime_reliability` | OK — 19/19 (PYTHONPATH=src) |
| **Test total** | **292/292 pass** |
| `ghoti_product_launcher.py --status --json` | OK |
| `parallel_agent_relay.py --status --json` | OK — relay_mode=copy_paste_only |
| `local_memory_compression_bridge.py --json` | OK — local_only=true |
| `repo_skill_plugin_intake.py --validate-config` | PASS — 22 entries, all blocked flags false |
| `ghoti_readiness_check.py --status` | PASS — supervised_mvp_slice_score=100, 9/9 categories |
| `supervised_content_mvp_runner.py --validate-latest` | PASS |
| `check_runtime_mvp.ps1` | PASS — exit 0 |
| `check_dashboard_mvp.ps1` | PASS — exit 0 |

## Test totals

292/292 tests pass across 11 modules. N+4.8A contributes 35 tests (approved catalog,
unknown-repo rejection, manager status, truthful sync degradation, repo-local clone
targets, no-install guarantees, adapter stub generation + import-safety + interface,
approval packet, dashboard labels, server endpoints, safety).

## Safety summary

| Safety property | Status |
|-----------------|--------|
| Repos cloned (shallow, approved catalog only) | YES — 5/5, `git clone --depth 1` |
| Dependencies installed (npm/pnpm/pip) | NO — never |
| External repo code executed | NO — never |
| External repo scripts run | NO |
| UI-TARS started / given desktop control | NO |
| External APIs (Gemini/OpenAI/Anthropic) connected | NO |
| Runtime wiring of external tools into Ghoti | NONE — adapter stubs only |
| Adapter stubs import external repo packages | NO — stdlib `json` only |
| `--allow-install` flag | exists but never installs — only enters a plan |
| Arbitrary repo slug accepted | NO — approved catalog only; unknown rejected |
| Python/JS shell execution option | NONE — fixed argv, shell disabled |
| Cloned repos committed to Ghoti | NO — `21_repos/third_party/*` is gitignored |
| Secrets / API keys | NONE |
| Human approval required for wiring | YES — adapters + approval packet enforce it |
| Dirty primary worktree | untouched (read-only) |
| N+3 readiness score | 100 (9/9 categories) |

## Direct answers

1. **Did Ghoti clone approved repos?** YES — all 5 approved public repos were
   shallow-cloned into `21_repos/third_party/sandboxed/` for static inspection only.
2. **Did Ghoti install anything?** NO — no npm / pnpm / pip install was performed.
   `--allow-install` exists but only records intent; it never installs.
3. **Did Ghoti run external repo code?** NO — only `git clone --depth 1` and
   `git rev-parse HEAD`, plus reading files. No external scripts were executed.
4. **Is UI-TARS controlling the desktop yet?** NO — UI-TARS was not started; no
   desktop click/type/screenshot control is enabled. The adapter is a stub.
5. **Are adapter stubs generated?** YES — 5 safe local stubs under
   `02_automation/external_tool_adapters/`, each with `status()`,
   `capabilities()`, `safety_gates()`, and `requires_human_approval = true`.
6. **Can the user approve real runtime wiring later?** YES — the approval packet
   under `14_context/external_tools/approval_packets/` is the per-tool review +
   sign-off gate; nothing is wired until a human approves it.
7. **Are approval gates intact?** YES — external tools remain approval-gated;
   readiness `safety_gates` passes; no gate was weakened.
8. **Is this full production 100%?** NO — this is a sandbox + static-discovery
   MVP. `supervised_mvp_slice_score` is 100, but `production_public_release_ready`
   is false and `production_autonomy_score` is `not_applicable`.

## Verdict

**IMPLEMENTED_AND_PUSHED** — N+4.8A adds a safe External Tool Sandbox: it
shallow-clones the 5 approved public repos, statically scans them (no install, no
execution), generates 5 safe local adapter stubs, writes a human approval packet,
and surfaces it on the dashboard. 292/292 tests pass; both PowerShell checks PASS;
readiness 100. No installs, no external code execution, no desktop control, no live
APIs — external tools remain fully approval-gated. `main` was not pushed.
