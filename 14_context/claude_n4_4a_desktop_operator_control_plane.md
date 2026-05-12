# Claude N+4.4A — Desktop Operator Control Plane MVP

## Executive Verdict

**IMPLEMENTED_AND_PUSHED**

N+4.4A introduces the first safe desktop-operator control plane in Ghoti. The plane converts a user goal into a validated handoff payload, probes available model adapters (gemini_cli / local_demo / ollama) and operator adapters (dry_run / local_preview_open / screenshot_probe-status), and gates every action behind an explicit approval token. Default mode is dry_run. No live Gemini prompts. No arbitrary click/type. No shell execution from model output. No live accounts. No posting.

This branch is **stacked on N+4.3A** so the content studio link is exercised end-to-end.

## Branches And Commits

| Field | Value |
| --- | --- |
| Branch | `feat/ghoti-agent-claude-n4-4a-desktop-operator-control-plane` |
| Worktree | `C:\Users\ai_sandbox\Documents\AI_Managed_Only_worktrees\claude_n4_4a_desktop_operator_control_plane` |
| Base main commit | `e16101992bf95447a6cb697e12c8c843c3c519a8` |
| Stacked on N+4.3A | YES — `origin/feat/ghoti-agent-claude-n4-3a-supervised-multi-agent-content-studio-demo` @ `1fb7804ce7f2e71c5a34f6d810235fe770b5e2de` merged into this worktree |

## Files Changed

| File | Change |
| --- | --- |
| `03_scripts/desktop_operator_control_plane.py` | NEW — 32 157 bytes, full control plane |
| `01_projects/runtime_mvp/tests/test_n4_4a_desktop_operator_control_plane.py` | NEW — 20 tests |
| `01_projects/dashboard_mvp/public/index.html` | MODIFIED — "Desktop Operator Truth" card |
| `03_scripts/check_dashboard_mvp.ps1` | MODIFIED — 6 new N+4.4A label-match checks |
| `14_context/desktop_operator/runs/20260512T180853Z_.../` | NEW — seed showcase run (7 artifacts) |
| `14_context/claude_n4_4a_desktop_operator_control_plane.md` | NEW — this report |

(Plus all 17 files inherited via the N+4.3A merge.)

## Handoff Schema Summary

| Field | Default Value |
| --- | --- |
| `task_id` | UUID-based `task-<hex>` |
| `user_goal` | from `--goal` |
| `requested_model_adapter` | one of `gemini_cli` / `local_demo` / `ollama` / `manual` |
| `requested_operator_adapter` | one of `dry_run` / `local_preview_open` / `screenshot_probe` |
| `target_workflow` | one of `content_studio_demo` / `memory_bridge` / `dashboard_open` |
| `risk_level` | one of `low` / `medium` / `high` |
| `allowed_actions` | safe whitelist for the workflow |
| `forbidden_actions` | full FORBIDDEN_ACTIONS list (arbitrary_click/type/shell_exec/live posting/etc.) |
| `requires_human_approval` | **true** (rejected if false) |
| `approval_token_required` | **true** (rejected if false) |
| `live_account_actions_enabled` | **false** (rejected if true) |
| `external_api_actions_enabled` | **false** (rejected if true) |
| `money_actions_enabled` | **false** (rejected if true) |
| `publish_actions_enabled` | **false** (rejected if true) |
| `external_repo_clone_install_run_enabled` | **false** (rejected if true) |
| `ui_tars_runtime_wired` and other external-tool flags | **false** (rejected if true) |

## CLI Modes

| Command | Behavior |
| --- | --- |
| `--status` | text status with model/operator adapter probes |
| `--status --json` | machine-readable JSON status |
| `--json` (bare) | delegates to `--status --json` |
| `--create-handoff --goal "<g>" --workflow <w>` | creates run folder, writes `00_handoff_payload.json` + validation + model status + safety review |
| `--validate-handoff <path>` | re-validates a handoff JSON, returns errors list |
| `--dry-run <path>` | writes `03_operator_plan.md`, executes 0 actions |
| `--approve <path> --approval-token <tok>` | writes `04_approval_record.json` with token hash; requires non-empty token |
| `--execute-approved <path>` | requires existing approval record; runs only safe local operations |

## Gemini CLI Status Behavior

| Field | Value |
| --- | --- |
| Detection method | `shutil.which("gemini")` + `gemini --version` with 10s timeout |
| Catches | `FileNotFoundError`, `TimeoutExpired`, `OSError` |
| `treated_as_unlimited` | always **false** |
| `live_prompt_executed` | always **false** in this milestone |
| `quota` | always reported as `unknown_free_tier_limited` |
| User goal piped to Gemini? | **NO** — only `--version` ever invoked |
| If `gemini` missing | returns `available: false`, `probe_error: "gemini executable not found in PATH"`, no crash |

## Local Fallback Behavior

`local_demo` adapter: deterministic, always-available status-only adapter. No prompt execution. `ollama` adapter status is probed indirectly via the N+4.2B `local_memory_compression_bridge.py --status --json` so it inherits the existing fallback truth (`local_demo` when no gemma model is found).

## Desktop Operator Adapter Summary

| Adapter | Available? | Side effects |
| --- | --- | --- |
| `dry_run` | YES | none |
| `local_preview_open` | YES (record-only) | The plane **records** the repo-local HTML path; never spawns a browser process this milestone |
| `screenshot_probe` | NO | Status-only placeholder; not enabled in N+4.4A |
| arbitrary click | DISABLED | `arbitrary_click` is in FORBIDDEN_ACTIONS |
| arbitrary type | DISABLED | `arbitrary_type` is in FORBIDDEN_ACTIONS |
| shell exec | DISABLED | `shell_exec` / `run_shell` / `sudo` / `install_package` all in FORBIDDEN_ACTIONS |

## Approval Gate Behavior

| Step | Behavior |
| --- | --- |
| `--approve` with empty token | REJECTED, exit 1 |
| `--approve` with short token | REJECTED (`min 4 chars`), exit 1 |
| `--approve` with valid token | writes `04_approval_record.json` containing SHA-256 token hash (raw token NEVER stored) |
| `--execute-approved` without approval record | REJECTED, exit 1, error `APPROVAL_RECORD_MISSING; run --approve first` |
| `--execute-approved` with malformed approval record | REJECTED, exit 1 |
| `--execute-approved` with `screenshot_probe` operator | REJECTED — operator not in `{dry_run, local_preview_open}` |
| `--execute-approved` with `content_studio_demo` workflow | invokes `supervised_content_studio_demo.py --status --json` only (status probe), records `content_studio_status_probe_only` action |

## Action Log Path

| Item | Value |
| --- | --- |
| Runs root | `14_context/desktop_operator/runs/` |
| Per-run slug | `<timestamp_slug>_<user_goal_slug>_<task_id>` |
| Showcase committed | `14_context/desktop_operator/runs/20260512T180853Z_create_a_local_video_style_conte_task-57af7fa5ec58/` |
| Artifacts | 7 files: `00_handoff_payload.json`, `01_validation_report.json`, `02_model_adapter_status.json`, `03_operator_plan.md`, `04_approval_record.json`, `05_execution_result.json`, `06_safety_review.md` |

## Dashboard Integration

New "Desktop Operator Truth" card in `01_projects/dashboard_mvp/public/index.html` shows:

- `default_mode: dry_run`
- `local_only: true`
- `live_account_actions_enabled: false`
- `external_api_actions_enabled: false`
- `money_actions_enabled: false`
- `publish_actions_enabled: false`
- `arbitrary_click_or_type_enabled: false`
- `shell_exec_from_model_output_enabled: false`
- `approval_gate: required_with_token`
- `Gemini CLI: status-only, quota=unknown_free_tier_limited, treated_as_unlimited=false`
- `local fallback: available (local_demo)`
- `external repos/tools: planning-only`
- `content studio workflow: local preview only`
- `safe handoff payload: enabled`
- `last handoff path: 14_context/desktop_operator/runs/<timestamp_slug>/`

`check_dashboard_mvp.ps1` extended with 6 new label-match checks.

## Content Studio Link Result

Because N+4.3A is merged into this worktree:
- `_probe_operator_adapters()` returns `content_studio_demo_present: true`
- `--execute-approved` on a `content_studio_demo` workflow successfully invokes `supervised_content_studio_demo.py --status --json` and records `content_studio_status_probe_only` as the executed action.
- It does NOT run `--run-demo` from within the control plane in this milestone (that step requires explicit operator approval to execute and is left for a future milestone or for the user to run directly).

## Validation Table

| Validation | Result |
| --- | --- |
| `git diff --check` | PASS — exit 0 |
| Python AST (7 files) | PASS |
| BOM in `desktop_operator_control_plane.py` | absent |
| BOM in test file | absent |
| `--status`, `--status --json`, `--json` (bare) | PASS |
| `--create-handoff` | PASS — 4 artifacts written |
| `--validate-handoff` | PASS |
| `--dry-run` | PASS — 0 actions executed |
| `--execute-approved` without approval | REJECTED, exit 1 |
| `--approve` with empty token | REJECTED, exit 1 |
| Full pipeline (create → approve → execute) | PASS — content_studio_link=available |
| N+4.4A tests | PASS — 20/20 |
| N+4.3A regression | PASS — 15/15 |
| N+4.2A regression | PASS — 26/26 |
| N+4.1 regression | PASS — 19/19 |
| Memory bridge `--json` | PASS |
| Registry `--validate-config` | PASS — 22 entries, all blocked flags false |
| Readiness | PASS — score 100, 9/9 |
| Content MVP | PASS — score 100, 5 gates pending |
| `node --check` | PASS server.js + app.js |
| `check_runtime_mvp.ps1` | PASS — "Summary: runtime MVP checks passed." |
| `check_dashboard_mvp.ps1` | PASS — "Summary: dashboard MVP checks passed." |

## Safety Table

| Check | Result |
| --- | --- |
| No secrets/API keys committed | PASS |
| No live Gemini prompts (only `--version`) | PASS |
| No arbitrary shell exec from model output | PASS — `shell_exec` in FORBIDDEN_ACTIONS |
| No arbitrary click/type | PASS — both in FORBIDDEN_ACTIONS |
| No live account/API actions | PASS |
| No posting/upload | PASS |
| No money/trading actions | PASS |
| No external repo clone/install/run | PASS |
| No UI-TARS/The Agency/Weavy/Manychat/Vouch/AEX/AirLLM/OpenFang/MoneyPrinter runtime wiring | PASS |
| All dangerous handoffs rejected | PASS — 8 validation rejection tests cover live/publish/money/external/UI-TARS/forbidden_action |
| Approval gate intact | PASS — token required, stored as SHA-256 hash, never raw |
| Default mode = dry_run | PASS |

## Direct Answers

| Question | Answer |
| --- | --- |
| Can dashboard/app create a safe handoff payload? | YES — `--create-handoff` produces a validated payload with default-safe flags |
| Can Gemini CLI touch the computer yet? | NO — Gemini probe is `--version` only; no user goal is piped |
| Is Gemini treated as unlimited/no-credits? | NO — `quota: unknown_free_tier_limited`, `treated_as_unlimited: false` |
| Can the operator click/type arbitrarily? | NO — `arbitrary_click` and `arbitrary_type` are in FORBIDDEN_ACTIONS and rejected by validation |
| Can it run content studio locally? | YES — only as a status probe within `--execute-approved` for `content_studio_demo` workflow; the user can still run `supervised_content_studio_demo.py --run-demo` directly |
| Does it post anything? | NO — `publish_actions_enabled: false`; `publish_to_social`, `publish_to_youtube`, `publish_to_tiktok` all forbidden |
| Does it use live accounts/APIs? | NO |
| Are external tools runtime-wired? | NO — all planning-only |
| Are approval gates intact? | YES — token required, hash stored, execute fails without record |
| Is this full Ghoti production 100%? | NO — local safe control plane MVP only |

## Final Verdict

**IMPLEMENTED_AND_PUSHED**

The first safe desktop-operator control plane lands. The dashboard/app can now safely create handoff payloads that pass validation, get dry-run, get human-approved with a token, and execute only local safe operations. Gemini CLI is detected but never receives a live prompt and is reported with truthful free-tier-limited quota. All regressions (N+4.1 / N+4.2A / N+4.3A) remain green; both check scripts PASS.

## Exact Next Recommended Action

Run **Codex N+4.4A real audit** on the pushed branch.