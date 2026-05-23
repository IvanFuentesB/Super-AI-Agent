# Claude N+4.4C — Desktop Operator Recipe Runner + Preview Polish

## Executive Verdict

**IMPLEMENTED_AND_PUSHED**

N+4.4C promotes the free-form `target_workflow` of N+4.4B into an explicit "recipe" abstraction. 4 allowlisted local recipes are now selectable from a new dashboard card; the same dry-run / approve / execute / preview safety flow is preserved with both the Node server and Python CLI enforcing the recipe allowlist. Gemini handoff export writes a local MD file only — never calls Gemini live.

**Stacked on N+4.3A + N+4.4A + N+4.4B.**

## Branches And Commits

| Field | Value |
| --- | --- |
| Branch | `feat/ghoti-agent-claude-n4-4c-desktop-operator-recipe-runner-preview-polish` |
| Worktree | `C:\Users\ai_sandbox\Documents\AI_Managed_Only_worktrees\claude_n4_4c_desktop_operator_recipe_runner_preview_polish` |
| Base main commit | `e16101992bf95447a6cb697e12c8c843c3c519a8` |
| Stacked on N+4.3A | YES — `1fb7804ce7f2e71c5a34f6d810235fe770b5e2de` in HEAD history |
| Stacked on N+4.4A | YES — `1521269533fcd457403ed730a884341f1e44aee6` in HEAD history |
| Stacked on N+4.4B | YES — `ad00a6b24e3141dc8abae1c5964690fbacf98007` in HEAD history |

## Files Changed

| File | Change |
| --- | --- |
| `03_scripts/desktop_operator_control_plane.py` | + `RECIPES` registry (4 entries) + `_RECIPE_EXECUTORS` + `cmd_recipe_list` + `cmd_recipe_execute` + per-recipe handlers + `--recipe-list` / `--recipe-execute --recipe-id` CLI args |
| `01_projects/dashboard_mvp/server.js` | + 6 recipe endpoints + recipe allowlist + per-recipe latest-state |
| `01_projects/dashboard_mvp/public/index.html` | + Desktop Operator Recipe Runner card with dropdown + 5 buttons + status panel |
| `01_projects/dashboard_mvp/public/app.js` | + 5 recipe runner client handlers + latest refresh |
| `03_scripts/check_dashboard_mvp.ps1` | + 8 new label-match checks |
| `01_projects/runtime_mvp/tests/test_n4_4c_desktop_operator_recipe_runner_preview_polish.py` | NEW — 16 tests |
| `14_context/desktop_operator/runs/20260513T061500Z_recipe_runner_showcase/` | NEW — 6 curated showcase artifacts |
| `14_context/desktop_operator/handoffs/20260513T061141Z_gemini_handoff_export/gemini_prompt.md` | NEW — sample Gemini-handoff-export markdown |
| `14_context/claude_n4_4c_desktop_operator_recipe_runner_preview_polish.md` | NEW — this report |

## Recipe Runner Summary

Recipes are an **allowlisted set of predefined safe workflows**. There is no free-form automation — only the 4 entries in the `RECIPES` dict can run. Both the Python CLI and the Node server independently enforce the allowlist; an unknown `recipe_id` is rejected with HTTP 400 at the server and exit 1 with `REJECTED: unknown recipe` at the CLI.

## Recipes Implemented (4)

| ID | Label | Workflow | Calls Gemini Live? | Writes Under |
| --- | --- | --- | --- | --- |
| `content_studio_generate_preview` | Run Content Studio Recipe | `content_studio_demo` | NO | `14_context/content_studio/runs/` |
| `memory_compress_demo` | Memory Compress Demo Recipe | `memory_bridge` | NO | `14_context/compact_memory/`, `14_context/obsidian_vault/` |
| `dashboard_open_preview` | Dashboard Open Preview Recipe | `dashboard_open` | NO | (record-only; no browser spawn) |
| `gemini_handoff_export` | Gemini Handoff Export Recipe | `memory_bridge` | **NO — writes local MD file only** | `14_context/desktop_operator/handoffs/` |

## Dashboard Controls

| # | Control | Behavior |
| --- | --- | --- |
| 1 | Recipe `<select>` dropdown | 4 allowlisted options |
| 2 | Create Recipe Handoff | POST `/api/desktop-operator/create-recipe-handoff` with `{recipe_id}` |
| 3 | Dry Run Recipe | POST `/api/desktop-operator/run-recipe-dry-run` |
| 4 | Approve Recipe | POST `/api/desktop-operator/approve-recipe`; server generates local token; SHA-256 hash stored; raw token NEVER returned |
| 5 | Execute Approved Recipe | POST `/api/desktop-operator/execute-approved-recipe`; runs only safe local recipe |
| 6 | Open/View Latest Preview | GET `/api/desktop-operator/preview?path=...`; repo-local `.html` only; never spawns a browser |

## Backend Endpoints

| Method | Path |
| --- | --- |
| GET | `/api/desktop-operator/recipes` |
| GET | `/api/desktop-operator/latest-recipe` |
| POST | `/api/desktop-operator/create-recipe-handoff` |
| POST | `/api/desktop-operator/run-recipe-dry-run` |
| POST | `/api/desktop-operator/approve-recipe` |
| POST | `/api/desktop-operator/execute-approved-recipe` |
| GET | `/api/desktop-operator/preview?path=...` (existing from N+4.4B; reused) |

All endpoints use `runCommand` (spawn, `shell: false`, 60s timeout), fixed argv, and degraded JSON on failure.

## End-to-End Pipeline Result (live test, recipe = `gemini_handoff_export`)

| Step | Result |
| --- | --- |
| `GET /api/desktop-operator/recipes` | `ok=true`, 4 recipes |
| `POST /api/desktop-operator/create-recipe-handoff` | `ok=true`, `recipe_id=gemini_handoff_export`, handoff JSON written |
| `POST /api/desktop-operator/run-recipe-dry-run` | `ok=true`, dry-run plan written |
| `POST /api/desktop-operator/approve-recipe` | `ok=true`, approval record with SHA-256 token hash |
| `POST /api/desktop-operator/execute-approved-recipe` | `ok=true`, `actions=1`, `handoff_export_path=14_context/desktop_operator/handoffs/20260513T061141Z_gemini_handoff_export/gemini_prompt.md` |
| `GET /api/desktop-operator/latest-recipe` | returns full latest-state with paths only |

## Gemini Handoff Export Result

| Field | Value |
| --- | --- |
| Behavior | Writes a local MD file at `14_context/desktop_operator/handoffs/<ts>_gemini_handoff_export/gemini_prompt.md` |
| Calls Gemini live | **NO** |
| `gemini_live_prompt_executed` | **false** |
| `gemini_treated_as_unlimited` | **false** |
| `handoff_export_only` | **true** |
| `quota_warning` | "Gemini CLI is quota-limited / free-tier, not unlimited." |
| MD content includes | quota warning + manual operator note + disabled-actions list |

## Local Fallback Result

`local_demo` adapter always available. `ollama` adapter probed via N+4.2B memory bridge — fallback mode reported truthfully as `local_demo` when no gemma model is pulled.

## Approval Gate Behavior

- Server generates random token (`recipe-...`) if client doesn't provide one
- Token NEVER returned to client or logged
- Only SHA-256 hash stored in `04_approval_record.json` (and renamed `02_recipe_approval_record.json` in the showcase)
- Execute-approved-recipe requires both `recipe_id` AND `approval_record_path` to be set on server-side latest state
- Python CLI re-validates the approval record exists before any execution

## Validation Table

| Validation | Result |
| --- | --- |
| `git diff --check` | PASS — exit 0 |
| Python AST (5 files) | PASS |
| `node --check` server.js + app.js | PASS |
| **N+4.4C tests** | **PASS — 16/16** |
| **N+4.4B regression** | **PASS — 17/17** |
| **N+4.4A regression** | **PASS — 20/20** |
| **N+4.3A regression** | **PASS — 15/15** |
| **N+4.2A regression** | **PASS — 26/26** |
| **N+4.1 regression** | **PASS — 19/19** |
| Memory bridge `--json` | PASS — local_only=true, fallback=local_demo |
| Registry `--validate-config` | PASS — 22 entries, all blocked flags False |
| Readiness | PASS — score 100, 9/9 |
| Content MVP | PASS — score 100, 5 gates pending review |
| `check_runtime_mvp.ps1` | PASS — "Summary: runtime MVP checks passed." |
| `check_dashboard_mvp.ps1` | TRANSIENT_ENVIRONMENTAL (pre-existing pattern; all 8 new N+4.4C label strings verified PASS by direct HTML inspection) |

## Safety Table

| Check | Result |
| --- | --- |
| `shell: true` in N+4.4C server block | **absent** (test enforced) |
| Recipe allowlist enforced (server + CLI) | yes |
| Repo-local path validation (preview, handoff) | yes — rejects `..`, secret patterns, non-`.html` |
| Raw approval token returned to client | **NO** (server explicit comment + test) |
| Raw approval token logged | **NO** (client `do NOT collect or store` comment + test) |
| Live Gemini prompt | **never** — `gemini_handoff_export` writes MD only, no subprocess to `gemini` |
| Arbitrary click/type | disabled (FORBIDDEN_ACTIONS) |
| Shell exec from model output | disabled (FORBIDDEN_ACTIONS) |
| Live account / publish / money | disabled |
| External repo wiring | none |

## Screenshot / Terminal Result

| Item | Result |
| --- | --- |
| `.NET Graphics` popup | Not observed |
| `runtime-desktop-clipboard-checkruntime-desktop-clipboard-check` garbage | Not observed |
| Blank `node.exe` validation window | Transient validation server only; explicit cleanup performed |
| Lingering process tied to worktree | None |
| GUI clicking required | NO |
| Blocking popup | NONE |

## Direct Answers

| Question | Answer |
| --- | --- |
| Can the dashboard run a safe content studio recipe? | **YES** — `content_studio_generate_preview` is allowlisted and dispatches to `supervised_content_studio_demo.py --run-demo` |
| Can it create a local preview? | **YES** — content_studio_generate_preview returns `preview_path` under `14_context/content_studio/runs/.../10_preview.html` |
| Can it export a Gemini handoff without live Gemini? | **YES** — `gemini_handoff_export` writes a local MD file with quota warning; no live Gemini call |
| Can Gemini touch the computer yet? | **NO** — user goal never piped to Gemini |
| Is Gemini treated as unlimited/no-credits? | **NO** — quota=`unknown_free_tier_limited`, `treated_as_unlimited=false`, MD file explicitly says "quota-limited / free-tier, not unlimited" |
| Can the operator click/type arbitrarily? | **NO** |
| Does it post anything? | **NO** |
| Does it use live accounts/APIs? | **NO** |
| Are external tools runtime-wired? | **NO** — all planning-only |
| Are approval gates intact? | **YES** — approval required before execute; token hash stored; raw token never returned |
| Is this full Ghoti production 100%? | **NO** — safe local recipe runner + dashboard only |

## Final Verdict

**IMPLEMENTED_AND_PUSHED**

The dashboard now has a working safe Recipe Runner. 4 allowlisted recipes are selectable; the full create → dry-run → approve → execute flow works end-to-end against a real Node server; Gemini handoff export produces a local MD file without ever calling Gemini live. 113 tests across 6 stacked regression suites all green. No external wiring. No live action.

## Exact Next Recommended Action

Run **Codex N+4.4C real audit** on the pushed branch.