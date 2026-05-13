# Codex N+4.4B Real Audit — Desktop Operator Dashboard Action Center

## Verdict

**BLOCKED_VALIDATION**

The N+4.4B branch is real, fetched, stacked on the expected N+4.3A and N+4.4A commits, and most dashboard/operator validation passes. However, direct live endpoint testing found a repo-boundary bug in `/api/desktop-operator/preview`: a sibling directory whose absolute path starts with the audit repo path prefix is accepted as repo-local. This violates the required "preview endpoint validates repo-local HTML only / outside-repo paths rejected" safety condition.

## Remote Truth

| Item | Result |
| --- | --- |
| Audit branch | `audit/ghoti-agent-codex-n4-4b-desktop-operator-dashboard-action-center-real-audit` |
| Target branch | `origin/feat/ghoti-agent-claude-n4-4b-desktop-operator-dashboard-action-center` |
| Target commit audited | `ad00a6b24e3141dc8abae1c5964690fbacf98007` |
| Base main commit | `e16101992bf95447a6cb697e12c8c843c3c519a8` |
| Remote/local target match | PASS |
| Stacked on N+4.3A `1fb7804ce7f2e71c5a34f6d810235fe770b5e2de` | YES |
| Stacked on N+4.4A `1521269533fcd457403ed730a884341f1e44aee6` | YES |
| No-commit merge into `origin/main` | PASS, no conflicts |

## Changed Files Inspected

| File / area | Result |
| --- | --- |
| `01_projects/dashboard_mvp/server.js` | N+4.4B endpoint block inspected |
| `01_projects/dashboard_mvp/public/index.html` | Action Center labels inspected |
| `01_projects/dashboard_mvp/public/app.js` | Client handlers inspected |
| `03_scripts/check_dashboard_mvp.ps1` | New label checks inspected |
| `03_scripts/desktop_operator_control_plane.py` | N+4.4A control plane inspected |
| `03_scripts/supervised_content_studio_demo.py` | N+4.3A content studio regression inspected |
| `01_projects/runtime_mvp/tests/test_n4_4b_desktop_operator_dashboard_action_center.py` | N+4.4B tests inspected |
| `14_context/claude_n4_4b_desktop_operator_dashboard_action_center.md` | Claude report inspected |
| Seed run folders under `14_context/content_studio/runs/` and `14_context/desktop_operator/runs/` | Present; no external media/assets found |

No committed temp logs, secrets, env files, external repo clones, or downloaded media/assets were found in the changed file set.

## Backend Endpoint Validation

Live server validation was run on an isolated port.

| Endpoint / check | Result |
| --- | --- |
| `GET /api/desktop-operator/status` | PASS, JSON valid, `default_mode=dry_run` |
| `POST /api/desktop-operator/create-handoff` | PASS, safe handoff written under `14_context/desktop_operator/runs/...` |
| `POST /api/desktop-operator/dry-run` | PASS, `actions_executed=0` |
| `POST /api/desktop-operator/approve` | PASS, approval record path returned; raw token not returned |
| `POST /api/desktop-operator/execute-approved` | PASS, local-only status probe executed |
| `GET /api/desktop-operator/latest` | PASS |
| `GET /api/desktop-operator/preview` with committed repo-local preview HTML | PASS |
| Unsafe workflow `uncontrolled_browser` | PASS, rejected with HTTP 400 |
| Outside path `C:\Windows\win.ini` | PASS, rejected with HTTP 400 |
| Non-HTML repo path | PASS, rejected with HTTP 400 |
| Sibling outside path with repo-prefix absolute path | FAIL, returned `ok=true` |

### Blocking Preview Boundary Finding

The implementation uses string-prefix containment in `isRepoLocalPath()`:

`normalized.startsWith(repoRoot)`

That accepts an absolute sibling path such as:

`C:\w\n4_4b_dashboard_action_center_real_audit_outsideprefix\audit_preview\preview.html`

because it starts with the repo path string:

`C:\w\n4_4b_dashboard_action_center_real_audit`

The audit created a temporary sibling HTML file, requested `/api/desktop-operator/preview?path=<absolute-sibling-html>`, and received `ok=true`. The temporary file was removed after the test. This is a real path-boundary validation bug. The endpoint should use a resolved relative path boundary check, for example `path.relative(repoRoot, normalized)` and reject values that are absolute, empty outside-policy, or start with `..`.

## Dashboard Action Center Validation

| Required visible text / behavior | Result |
| --- | --- |
| `Desktop Operator Action Center` | PASS |
| `Create Safe Handoff` | PASS |
| `Dry Run Handoff` / `Dry-Run Handoff` | PASS |
| `Generate Approval Record` | PASS |
| `Execute Approved Local Action` | PASS |
| `Open Latest Preview` | PASS |
| `Gemini CLI: status-only` | PASS |
| `local fallback available` | PASS |
| `default mode: dry_run` | PASS |
| `safe handoff payload enabled` | PASS |
| `approval required` | PASS |
| `arbitrary click/type disabled` | PASS |
| `shell execution disabled` | PASS |
| `live account actions disabled` | PASS |
| `publish/money actions disabled` | PASS |
| `content studio workflow: local preview only` | PASS |

## Handoff / Approval / Execute Results

| Flow step | Result |
| --- | --- |
| Handoff payload | PASS, created safe `content_studio_demo` handoff |
| Dry-run | PASS, plan written, zero actions executed |
| Approval record | PASS, SHA-256 `approval_token_hash` stored; raw token absent |
| Execute-approved | PASS, local-only `content_studio_status_probe_only`; no posting/account/API/money action |
| Latest state | PASS, latest path metadata returned |
| Preview | BLOCKED by prefix-boundary bug despite normal repo-local preview passing |

## Gemini / Local Fallback Behavior

| Check | Result |
| --- | --- |
| Gemini CLI status detection only | PASS |
| User goal sent to Gemini | NO |
| Gemini treated as unlimited/no-credits | NO, `treated_as_unlimited=false` |
| Gemini live prompt executed | NO |
| Local fallback | PASS, `local_demo.available=true` |
| Ollama/Gemma bridge | PASS, Ollama present, Gemma missing, truthful `local_demo` fallback |

## Content Studio Link Validation

| Check | Result |
| --- | --- |
| `supervised_content_studio_demo.py --status` | PASS |
| `--run-demo --json` | PASS |
| Agent count | PASS, 8 |
| Title variants | PASS, 100 |
| Thumbnail variants | PASS, 100 |
| Preview HTML | PASS, local preview generated |
| `local_only` | PASS, true |
| `external_api_used` | PASS, false |
| `publish_enabled` | PASS, false |

## Static / Test / Regression Table

| Validation | Result |
| --- | --- |
| `git diff --check` | PASS |
| `git diff --cached --check` during merge rehearsal | PASS |
| `git show --check --stat HEAD` | PASS |
| `git show --check --stat <target>` | PASS |
| Python AST for changed Python files | PASS, 5 files |
| Produced JSON parse | PASS, 9 files |
| `node --check server.js` | PASS |
| `node --check app.js` | PASS |
| N+4.4B unit tests | PASS, 17/17 |
| N+4.4A unit tests | PASS, 20/20 |
| N+4.3A unit tests | PASS, 15/15 |
| N+4.2A unit tests | PASS, 26/26 |
| N+4.1 unit tests | PASS, 19/19 |
| `local_memory_compression_bridge.py --json` | PASS |
| `repo_skill_plugin_intake.py --validate-config` | PASS, 22 entries |
| `ghoti_readiness_check.py --status` | PASS, score 100, 9/9 |
| `supervised_content_mvp_runner.py --validate-latest` | PASS |
| `check_runtime_mvp.ps1` | PASS, exit 0 |
| `check_dashboard_mvp.ps1` | PASS on rerun, exit 0 |

Note: the first dashboard checker run failed with a transport interruption because an unrelated helper process from `claude_n4_4c_desktop_operator_recipe_runner_preview_polish` was actively killing all Node processes. After stopping that interfering helper and the orphaned checker server, the dashboard checker rerun passed. This was documented as environment interference, not the N+4.4B blocker.

## Safety Table

| Safety item | Result |
| --- | --- |
| No committed secrets/API keys | PASS |
| No live Gemini prompts | PASS |
| No user goal sent to Gemini | PASS |
| No arbitrary shell execution from model output | PASS |
| No arbitrary click/type endpoint added by N+4.4B | PASS |
| No live account/API actions | PASS |
| No posting/uploading | PASS |
| No money/trading actions | PASS |
| No external repo clone/install/run | PASS |
| No UI-TARS/The Agency/Weavy/Manychat/Vouch/AEX/AirLLM/OpenFang/MoneyPrinter runtime wiring | PASS |
| Approval gate intact | PASS |
| Raw approval token not stored or returned | PASS |
| Default mode dry-run | PASS |
| Repo-local preview boundary | FAIL, sibling-prefix absolute path accepted |

## Screenshot / Terminal Behavior

| Item | Result |
| --- | --- |
| Blocking GUI popup | Not observed |
| `.NET Graphics` popup | Not observed |
| `runtime-desktop-clipboard-checkruntime-desktop-clipboard-check` garbage command | Not observed |
| Blank `node.exe` window | Only validation server behavior; no manual clicking required |
| Lingering audit server after cleanup | Not observed after rerun cleanup |

## Direct Answers

| Question | Answer |
| --- | --- |
| Can the dashboard create a safe handoff payload? | YES |
| Can the dashboard dry-run it? | YES |
| Can the dashboard approve it? | YES |
| Can the dashboard execute approved local-only action? | YES |
| Can Gemini touch the computer yet? | NO |
| Is Gemini treated as unlimited/no-credits? | NO |
| Can the operator click/type arbitrarily? | NO |
| Does it post anything? | NO |
| Does it use live accounts/APIs? | NO |
| Are external tools runtime-wired? | NO |
| Are approval gates intact? | YES |
| Is this full Ghoti production 100%? | NO |
| Is merge to main recommended? | NO, not until the preview path boundary bug is fixed |

## Final Verdict

**BLOCKED_VALIDATION**

N+4.4B should not merge as-is. Fix `/api/desktop-operator/preview` path containment so absolute sibling paths whose string prefix matches the repo root are rejected, add a regression test for that sibling-prefix escape, and rerun this audit.
