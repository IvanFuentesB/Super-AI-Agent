# Codex N+6.0C Report History Stability Repair

Date: 2026-05-24

## Final Verdict

CLEAN PASS / REPORT HISTORY STABILITY REPAIR READY.

The fresh N+6.0B final-main audit exposed a real regression: adding N+6.0B reports pushed older milestone reports out of the generated compact context pack and repo knowledge map. Existing N+5 tests require important history such as N+5.5B and N+5.6B to remain visible.

## Root Cause

Both report discovery helpers used fixed recent-report limits:

- `03_scripts/ghoti_context_pack_builder.py`: top 12 reports
- `03_scripts/ghoti_repo_knowledge_map.py`: top 10 reports

N+6.0A/N+6.0B added enough newer reports that required historical milestones were no longer included.

## Fix

The generators now keep the recent-report list and append a small pinned history set when missing:

- `codex_n5_5b_main_merge_local_memory_context_pack.md`
- `codex_n5_6a_local_model_gemma_setup_truth_easy_worker_lane.md`
- `codex_n5_6b_main_merge_local_model_easy_worker_lane.md`
- `codex_n5_7a_graphify_repo_knowledge_map_context_retrieval.md`

This keeps compact outputs useful for current work while preserving milestone continuity needed by tests and operator handoffs.

## Validation

Run from:

`C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n6_0c_report_history_repair`

Validation passed:

- Focused red/green tests:
  - `test_n5_5a_local_memory_context_pack`
  - `test_n5_7a_repo_knowledge_map`
- `git diff --check`
- N+4 runtime tests: 329 OK
- N+5 runtime tests: 97 OK
- N+6 runtime tests: 5 OK
- Context pack generation: PASS
- Repo knowledge status: PASS
- Public audit: 150 checks / 0 blockers / 7 warnings requiring human review
- Node syntax checks: PASS

## Safety

- No model pulls.
- No live APIs.
- No Hermes setup/provider config.
- No Telegram setup.
- No browser or computer-use actions.
- UI-TARS remains observation-only.
- Production routing remains disabled until N+6.1A adds the repo-bundle hallucination guard.
