# N+4.5C — Parallel Agent Relay Runtime Route Fix

## Identifiers

| Field | Value |
|-------|-------|
| Milestone | N+4.5C — Parallel Agent Relay Runtime Route Fix |
| Branch | feat/ghoti-agent-claude-n4-5c-parallel-agent-relay-runtime-route-fix |
| Worktree | C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\claude_n4_5c_parallel_agent_relay_runtime_route_fix |
| Base main | 46e3b1d440d38cc0cc52343648e38a8fa5b7e385 |
| Branch created from | origin/main (46e3b1d) |

## Status correction — the route bug was already fixed before N+4.5C

The N+4.5C task brief states the N+4.5A merge gate was BLOCKED and the relay
route bug is still live. **That premise is out of date.** Verified against the
remote at the start of this task:

- The N+4.5A merge gate **succeeded** (`MERGED_AND_PUSHED`), not blocked.
- The exact `method`/`pathname` bug was already found and fixed in commit
  `473690f74df8cc4e90693de13738e52b63232fe6`
  (`fix(ghoti): use request.method/requestUrl.pathname in N+4.5A relay endpoints`).
- That fix was merged to `main` via merge commit `169cd76`; `origin/main` is
  `46e3b1d`.
- All 5 relay route guards on `origin/main`'s `server.js` already use
  `request.method` / `requestUrl.pathname`. Zero bare `if (method ===` remain.

So the **code repair was already on main**. What N+4.5A did NOT include — and
what this N+4.5C branch delivers — is the **regression test coverage** that
proves the bug class cannot recur and validates the relay endpoints against a
live Node server.

## Exact bug reproduced

Original (pre-`473690f`) relay route guards in `server.js`:

```js
if (method === "GET" && pathname === "/api/agent-relay/status") {
```

`method` and `pathname` are undefined in the `handleApiRequest` scope — every
other handler in that function uses `request.method` and `requestUrl.pathname`.
At runtime each relay endpoint threw `ReferenceError: method is not defined`,
caught by the request wrapper, returning:

```json
{"ok":false,"error":"method is not defined"}
```

## Root cause

- `node --check` validates **syntax only** — a reference to an undefined
  identifier is syntactically valid, so it passed.
- The N+4.5A test suite only checked **endpoint string presence** in `server.js`
  source — the path strings were present even in the buggy version.
- The N+4.5A audit did **not** start a live dashboard server.
- The bug surfaced only when `check_dashboard_mvp.ps1` ran the live relay status
  endpoint during the N+4.5A merge gate; it then cascaded into
  `check_runtime_mvp.ps1` (whose executor `run_checker` task runs the dashboard
  checker as a sub-task).

## Files changed (N+4.5C)

| File | Change |
|------|--------|
| `01_projects/runtime_mvp/tests/test_n4_5a_parallel_agent_relay_command_center.py` | +16 regression tests, +`_relay_section` helper, +`SERVER_JS` const, expanded imports |

`server.js` is **not** changed by N+4.5C — the route repair already landed in
`473690f` and is present on `main`.

## Fix summary

The code fix (already on `main`, commit `473690f`): in all 5 relay route guards,
`method` -> `request.method` and `pathname` -> `requestUrl.pathname` (5 insertions,
5 deletions). N+4.5C adds the test hardening so the bug cannot pass again:

**`TestRelayRouteGuards`** (static, 9 tests) — fails if the bug class returns:
- each of the 5 relay route guards uses `request.method`
- each uses `requestUrl.pathname`
- no bare `method` reference in the relay section (unless a local `const method` exists)
- no bare `pathname` reference in the relay section (unless a local `const pathname` exists)
- no `shell: true` in the relay section
- create-pair spawns the python relay script only (`runCommand(py.command, ...)`), never a literal/agent command
- relay status endpoint hardcodes `copy_paste_only` + `autonomous_launch: false`
- `resolveRelayPromptPath` uses the N+4.4D `isPathInside` containment helper

**`TestRelayLiveEndpoints`** (live, 7 tests) — spawns the real Node server on a
dedicated port and exercises every relay endpoint:
- `GET /api/agent-relay/status` -> 200, `ok:true`, `relay_mode:copy_paste_only`
- `GET /api/agent-relay/latest` -> 200, `ok:true`
- `POST /api/agent-relay/create-pair` -> 200, `ok:true`, manifest with claude+codex lanes
- `GET /api/agent-relay/pair?id=<id>` -> 200, `ok:true`, manifest
- `GET /api/agent-relay/prompt?path=<repo-local md>` -> 200, `ok:true`, content present
- `GET /api/agent-relay/prompt?path=<traversal>` -> 403 (containment holds)
- explicit assertion that no relay endpoint body contains `method is not defined`
  or `pathname is not defined`

## Live endpoint validation result

Real dashboard Node server spawned; every relay endpoint hit live:

```
[status]  HTTP 200  ok=True  relay_mode=copy_paste_only
[latest]  HTTP 200  ok=True  pair_id=20260517T002139Z_n_4_5c-route-fix-smoke
[create]  HTTP 200  ok=True  files=8  lanes=['claude','codex']
[pair]    HTTP 200  ok=True
[prompt]  HTTP 200  ok=True  content contains /ultraplan
[no "method is not defined" / "pathname is not defined" on any endpoint] 0 occurrences
```

`TestRelayLiveEndpoints`: 7/7 passed (not skipped — the server started and
responded). No `method is not defined`. No `pathname is not defined`.

## check_dashboard_mvp.ps1 result

**PASS** — exit 0. "Summary: dashboard MVP checks passed." No FAIL lines.
`[PASS] Parallel Agent Relay status endpoint: relay_mode=copy_paste_only`.

## check_runtime_mvp.ps1 result

**PASS** — exit 0. "Summary: runtime MVP checks passed." No FAIL lines. The
cascade from the dashboard checker is resolved.

## Regression totals (real output)

| Module | Result |
|--------|--------|
| test_n4_5a_parallel_agent_relay_command_center | OK — 68/68 (52 original + 16 new N+4.5C) |
| test_n4_4d_preview_path_containment_fix | OK — 18/18 |
| test_n4_4c_desktop_operator_recipe_runner_preview_polish | OK — 16/16 |
| test_n4_4b_desktop_operator_dashboard_action_center | OK — 17/17 |
| test_n4_4a_desktop_operator_control_plane | OK — 20/20 |
| test_n4_3a_supervised_content_studio_demo | OK — 15/15 |
| test_n4_2a_local_memory_intake | OK — 26/26 |
| test_n4_1_runtime_reliability | OK — 19/19 (PYTHONPATH=src) |
| **Total** | **199/199 pass** |

Other validation:
- `git diff --check` — clean
- `node --check server.js` / `node --check public/app.js` — OK
- `parallel_agent_relay.py --status --json` / `--json` / `--create-pair` smoke — OK (8 files, claude+codex lanes)
- `local_memory_compression_bridge.py --json` — OK (local_only=true, external_api_used=false)
- `repo_skill_plugin_intake.py --validate-config` — PASS (22 entries, all blocked flags false)
- `ghoti_readiness_check.py --status` — PASS (supervised_mvp_slice_score=100, 9/9 categories, all_required_pass=true)
- `supervised_content_mvp_runner.py --validate-latest` — PASS (slice score 100)
- Relay smoke pair: `14_context/agent_relay/pairs/20260517T002139Z_n_4_5c-route-fix-smoke`

## Safety summary

| Property | Status |
|----------|--------|
| Relay route guards use `request.method` / `requestUrl.pathname` | confirmed (static + live tests) |
| No `method is not defined` / `pathname is not defined` at runtime | confirmed live |
| No `shell: true` in server.js relay section | confirmed |
| No subprocess to `claude` / `codex` — create-pair spawns python only | confirmed |
| Prompt endpoint path containment uses N+4.4D `isPathInside` helper | confirmed (static + live traversal -> 403) |
| Relay remains copy-paste-only, no autonomous launch | confirmed |
| No external repo clone/install/run | confirmed |
| No live API / account / posting / money actions | confirmed |
| No secrets read | confirmed |
| N+3 readiness score | 100 (9/9 categories) |

## Direct answers

1. **Did this fix method/pathname undefined?** YES — the code repair already
   landed in `473690f` (on `main`); N+4.5C adds the static + live regression
   tests that prove it and prevent recurrence.
2. **Do relay endpoints work live?** YES — all 5 endpoints verified against a
   real Node server: status, create-pair, latest, pair, prompt all return valid
   JSON; no `method is not defined`; no `pathname is not defined`.
3. **Can the user generate paired Claude/Codex prompts?** YES — via
   `parallel_agent_relay.py --create-pair` or `POST /api/agent-relay/create-pair`;
   each pair is an 8-file packet with claude + codex lanes.
4. **Does this launch agents automatically?** NO — copy-paste only;
   `autonomous_launch` is false; a human must paste each prompt.
5. **Are external tools wired?** NO — `external_coordinator_repos` is
   planning-only; AEX / Cowork / The Agency / agent-skills-eval are
   future-compatible labels only; nothing is cloned, installed, or run.
6. **Are approval gates intact?** YES — human approval required for every
   prompt dispatch; readiness `safety_gates` category passes; no gate weakened.
7. **Is this full Ghoti production 100%?** NO — supervised MVP slice.
   `supervised_mvp_slice_score` is 100, but `production_public_release_ready`
   is false and `production_autonomy_score` is `not_applicable`.

## Verdict

**IMPLEMENTED_AND_PUSHED** — N+4.5C adds the regression + live-server test
coverage for the relay runtime route bug. The code repair was already on `main`
(`473690f`); N+4.5C proves it holds and guards against recurrence. All 199 tests
pass; both PowerShell checks PASS; readiness 100. `main` was not pushed.
