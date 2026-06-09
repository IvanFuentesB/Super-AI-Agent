# Context Snapshot -- N+6.40A Working MVP: Runtime Recipes

**Milestone:** N+6.40A
**Date:** 2026-06-09
**Model used:** Fable (implementation lane)
**Branch:** `feat/ghoti-agent-claude-fable-n6-40a-working-mvp-runtime-recipes`
**Starting branch:** `feat/ghoti-agent-claude-n6-39b-demo-ready-operator-console` (86df4bf)
**origin/main at start:** `70755c89de926d4cf6a9083858287351757673ba` (N+6.38B)

---

## Goal

Make Ghoti actually useful: a Working Recipes layer where one click or one
command performs real local supervised work, writes Markdown reports, and shows
what happened - validated by the Rust deny-by-default policy checker.

## Files changed

| File | Change |
|------|--------|
| `03_scripts/operator_recipes/ghoti_operator_recipes.py` | New recipes CLI: 5 recipes + all-safe, policy bridge, honest reports |
| `03_scripts/operator_recipes/check_operator_recipes.ps1` | New ASCII-safe PowerShell checker (StrictMode Latest) |
| `23_configs/operator_recipe_policy.example.json` | New deny-by-default policy manifest |
| `rust/ghoti_policy_checker/src/main.rs` | Added `report_write_repo_local` + `local_model_status_read` capabilities, 2 new unit tests (6 total pass) |
| `01_projects/dashboard_mvp/server.js` | 3 operator-recipe endpoints (allowlisted ids, fixed argv, repo-local cache) |
| `01_projects/dashboard_mvp/public/index.html` | Working Recipes section (top of Home), Artifacts operator-reports card |
| `01_projects/dashboard_mvp/public/app.js` | Recipe wiring, registry check, latest-run refresh, idle-never-degraded guard |
| `01_projects/dashboard_mvp/public/styles.css` | Recipe card styles, vertical-title-text fix |
| `01_projects/runtime_mvp/tests/test_n6_40a_working_mvp_runtime_recipes.py` | 43 tests |
| `docs/GHOTI_N6_40A_WORKING_MVP_RUNTIME_RECIPES.md` | Full docs |
| `.gitignore` | `14_context/operator_reports/generated/` |
| `14_context/claude_fable_n6_40a_working_mvp_runtime_recipes.md` | This snapshot |

## Recipes implemented

1. `project-health` - git truth, launcher status, public audit, Rust status,
   PR queue, dashboard probe -> `project_health_<ts>.md`
2. `handoff-pack` - implementation/audit/local-model copy-paste packets ->
   `handoff_pack_<ts>.md`
3. `cleanup-preview` - untracked/modified/large/worktrees/caches/logs,
   strictly read-only -> `repo_cleanup_preview_<ts>.md`
4. `local-model-check` - ollama command + 127.0.0.1:11434 + llama3.1:8b /
   gemma3:4b, manual pull commands only -> `local_model_readiness_<ts>.md`
5. `fixture-replay-demo` - 5 tasks / 3 groups / 0 overlaps simulation ->
   `fixture_replay_demo_<ts>.md`
6. `all-safe` - all five + `all_safe_summary_<ts>.md`

Every JSON result carries: ok, recipe_id, mode, dry_run, report_path, summary,
safety_flags, policy, actions_taken, actions_blocked, next_actions, errors,
warnings. Every report carries the six honest sections including
"What happened" and "Next action:".

## Rust / policy integration status

- Real Rust invocation works: when `rust/target/{release,debug}/ghoti_policy_checker`
  is built, recipes call it with a plan JSON and record
  `rust_checker_available/used: true` (verified live in this environment).
- Capabilities added to the Rust allow list: `report_write_repo_local`,
  `local_model_status_read`. `cargo test`: 6/6 pass, including
  `operator_recipe_plan_is_allowed` and `recipe_external_write_is_denied_as_unknown`.
- Python mirror enforces the same deny-by-default lists from
  `23_configs/operator_recipe_policy.example.json` when no binary exists.
- The compiled binary itself is not committed (target/ stays gitignored);
  direct Rust enforcement on machines without a build falls back to the mirror.

## Dashboard changes

- "Working Recipes" is the first card on Home / Capabilities:
  "Start here: run a useful local recipe." Six cards (5 recipes + Run All),
  each with What it does / Why it matters / It will not / button / last result
  / report path.
- Endpoints: `GET .../operator-recipes`, `POST .../run-operator-recipe`
  (allowlisted ids only), `GET .../latest-operator-recipe-runs` (repo-local
  gitignored cache `runtime_data/operator_recipe_runs_latest.json`).
- Artifacts page: new "Operator reports" card referencing
  `14_context/operator_reports/generated/` and listing recorded runs.
- UI fixes: vertical-title-text CSS guard, recipe-card overflow protection,
  idle/degraded never styled as an error unless `criticalIssue` is true
  (text stays truthful; only alarm styling is reserved for critical).
- N+6.39B kept: hero, supervised wording, investor demo panel, roadmap.

## Tests

- `test_n6_40a_working_mvp_runtime_recipes.py`: 43 tests, all pass
  (1 skip: PowerShell executable not available in the validation environment;
  reported as not available, not passed - ASCII + structural checks still run).
- N+6.39B suite: 37 pass. N+6.39A suite: 26 pass.
- `cargo test -p ghoti_policy_checker`: 6 pass.
- Public audit: 0 blockers / 7 advisory warnings.

## Example generated reports (from validation; gitignored, not committed)

- `project_health_<ts>.md` - branch/HEAD/origin-main truth, 0 audit blockers,
  PR queue (#14, #15, this branch), blockers/next milestone.
- `fixture_replay_demo_<ts>.md` - 5 tasks / 3 parallel groups / 0 overlaps,
  simulation only, why this proves safe supervised planning.

## What stayed disabled

Live agents, account actions, provider/API keys, Telegram, Obsidian, MCP,
browser automation (beyond opening localhost), computer-use, auto-submit,
secrets, destructive deletes/moves, writes outside the repo. Outside-repo
`--output-dir` is preview-only (no allowlisted external paths exist yet).

## Obsidian touched?

No. Roadmap-only mention ("Obsidian curated memory" as next milestone).

## Telegram touched?

No. Roadmap-only mention ("Telegram status notifications", notification-only).

## Codex audit target

`audit/ghoti-agent-codex-n6-40a-working-mvp-runtime-recipes`
