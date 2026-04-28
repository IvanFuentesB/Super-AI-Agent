# Codex N+3.18 Dirty Implementation Audit v2

Status: codex_followup_audit_only / dirty_runtime_not_staged / no_runtime_changes

## Repo Truth

| Item | Truth |
| --- | --- |
| Branch | `feat/ghoti-visible-operator-stack` |
| Local HEAD | `05aedf0 docs/analysis milestone N+3.18 - audit interrupted Claude video-to-money implementation` |
| Origin HEAD | `05aedf0 docs/analysis milestone N+3.18 - audit interrupted Claude video-to-money implementation` |
| Local/origin relationship | synced, `0 0` ahead/behind |
| Staged files before this Codex doc pass | none |

## Dirty Files Reviewed

Likely interrupted Claude N+3.18 partial work:

| File | Dirty state | Review result |
| --- | --- | --- |
| `01_projects/runtime_mvp/src/super_ai_agent/local_brain_router.py` | modified | Adds partial `video_to_money` Gemma runner route |
| `03_scripts/money_workflow_new_experiment.py` | modified | Adds optional scoring fields and score bucket logic |
| `14_context/money_workflows/experiment_tracker.schema.json` | modified | Adds optional `scoring` schema object |
| `14_context/money_workflows/sample_video_notes_n3_18.md` | untracked | Safe fictional local sample input for smoke testing |

Unrelated or pre-existing dirty/local-only files:

- `14_context/ghoti_external_repo_tool_intake.md`
- `21_repos/third_party/.gitkeep`
- `.claude/skills/`
- `01_projects/mcp_server/test.txt`
- `05_logs/local_brain_runs/*`
- `14_context/ghoti_current_prompt_N1_6.md`
- local CV `.docx` files
- `output/`

## Implementation Completeness Table

| Area | Present? | Complete? | Notes |
| --- | --- | --- | --- |
| `video_to_money` CLI route | yes | partial | Route exists and writes artifacts, but smoke test and docs are still missing |
| Local-only input policy | yes | mostly | `.md` and `.txt` only; repo-root safety depends on existing `_resolve_input_path` |
| No URL fetch / no scraping | yes | needs doc | Implementation uses local input path only |
| Artifact-only output | yes | partial | Writes run artifacts under `05_logs/money_runs/<run_id>/` |
| Model output execution blocked | yes | needs smoke | `run_summary.json` records no execution and no auto-post/sell/email |
| Experiment candidate JSONL | yes | needs smoke | Parser may be fragile with Gemma bullet formatting |
| Money experiment scoring | yes | partial | CLI args and scoring buckets exist; dry-run still needed |
| Schema scoring support | yes | partial | JSON parses; record-shape validation still needed |
| Required implementation docs | no | incomplete | Four N+3.18 docs still missing |
| State docs | no | incomplete | `current_state.md`, `next_actions.md`, and finish-line log not updated |
| Wait/resume seed | no diff | incomplete | `wait_resume_supervisor.py` currently has no N+3.18 dirty diff |
| Commit/push | no | incomplete | Claude partial implementation remains uncommitted |

## Static Validation Results

Codex ran static-only checks and did not run Gemma/Ollama inference.

| Check | Result |
| --- | --- |
| `local_brain_router.py` AST parse | PASS |
| `money_workflow_new_experiment.py` AST parse | PASS |
| `wait_resume_supervisor.py` AST parse | PASS |
| `experiment_tracker.schema.json` JSON parse | PASS |
| `git diff --check` | PASS with Git CRLF warnings only |
| `git diff --cached --check` | PASS, no staged files before doc staging |

## Risks

- The `video_to_money` artifact root is `05_logs/money_runs/<run_id>/`, while previous Codex specs referenced `05_logs/money_workflow_runs/<run_id>/`. Claude should either align this or document the shorter path as the chosen convention.
- The runner writes `source_summary.md`; earlier specs used names like `business_model_summary.md`. This is not unsafe, but it should be documented before commit.
- `_candidates_to_jsonl` may collapse candidate records if the model emits many `- key:` lines without blank lines between candidates.
- `approval_required` may become a string if Gemma emits `approval_required: true` and parsed fields override the default boolean.
- No Gemma smoke has confirmed the output sections, JSONL parsing, or run summary yet.
- No scoring dry-run has confirmed CLI score arguments produce the expected schema-compatible record.

## Exact Claude Continuation Checklist

1. Continue from the current dirty partial implementation. Do not reset or restart.
2. Review and, if needed, repair `video_to_money` output path naming and artifact names.
3. Normalize candidate JSONL parsing and `approval_required` boolean handling.
4. Run static checks.
5. Run one Gemma `video_to_money` smoke against `14_context/money_workflows/sample_video_notes_n3_18.md`.
6. Run one money experiment scoring dry-run.
7. Create the missing N+3.18 docs.
8. Update `wait_resume_supervisor.py` only if needed and intentionally.
9. Update `current_state.md`, `next_actions.md`, and `ghoti_finish_line_log.md`.
10. Stage only intentional N+3.18 files.
11. Commit `feat/ghoti milestone N+3.18 - add Gemma video-to-money runner and experiment scoring`.
12. Push to `origin feat/ghoti-visible-operator-stack`.
