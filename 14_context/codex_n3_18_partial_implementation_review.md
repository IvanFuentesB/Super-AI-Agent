# Codex N+3.18 Partial Implementation Review

Status: codex_recovery_audit_only / partial_implementation_review / no_runtime_changes

## Summary

Claude Code appears to have started the N+3.18 implementation and stopped before docs, smoke tests, state updates, validation, staging, commit, and push. The work should not be restarted from scratch. It should be continued carefully from the existing dirty files.

## `local_brain_router.py` Review

Observed additions:

- New `video_to_money` task route.
- New local output root: `05_logs/money_runs/<run_id>/`.
- Markdown/text-only input policy through `.md` and `.txt` extensions.
- Repo-root input resolution through the existing safe input path mechanism.
- Prompt template requiring model output sections:
  - `SOURCE SUMMARY`
  - `PRODUCT IDEAS`
  - `CONTENT ANGLES`
  - `EXPERIMENT CANDIDATES`
  - `DISTRIBUTION PLAN`
  - `RISK REVIEW`
- Artifact-only output files:
  - `request.json`
  - `source_excerpt.md`
  - `source_summary.md`
  - `product_ideas.md`
  - `content_angles.md`
  - `experiment_candidates.jsonl`
  - `distribution_plan.md`
  - `risk_review.md`
  - `run_summary.json`
- Safety truth in `run_summary.json`, including no model-output execution, no auto-posting, no auto-selling, no auto-emailing, and approval required for use.

Open review items:

- Codex N+3.18 spec expected `05_logs/money_workflow_runs/<run_id>/`; partial implementation uses `05_logs/money_runs/<run_id>/`. Claude should either align the path or document the intentional shorter name.
- Codex N+3.18 spec used names such as `business_model_summary.md`; partial implementation writes `source_summary.md`. This is acceptable if documented, but should be made consistent before commit.
- `_candidates_to_jsonl` may be fragile if Gemma returns multiple `- key:` lines without blank lines between candidates. Smoke testing should verify whether it creates multiple candidate records or collapses fields into one record.
- If model output includes `approval_required: true`, the parser may store the value as a string and override the default boolean because the generated record merges parsed fields after the default field. Claude should confirm or normalize this.

## `money_workflow_new_experiment.py` Review

Observed additions:

- Adds scoring CLI fields:
  - `speed_to_ship`
  - `pain_intensity`
  - `buyer_access`
  - `distribution_leverage`
  - `proof_difficulty`
  - `build_complexity`
  - `legal_tos_risk_score`
  - `monetization_clarity`
  - `content_volume_potential`
  - `email_list_potential`
- Requires all scoring fields if any scoring field is provided.
- Validates each score as an integer from 1 to 5.
- Inverts lower-is-better fields for total scoring:
  - `proof_difficulty`
  - `build_complexity`
  - `legal_tos_risk_score`
- Produces `total_score` and `priority_bucket` values:
  - `A` for 40+
  - `B` for 32+
  - `C` for 24+
  - `D` otherwise
- Adds scoring output to dry-run output when present.

Open review items:

- Claude should run at least one dry-run scoring command and one safe append command only if append is intended for the milestone.
- The script should remain local-only and must not post, sell, email, scrape, or use external APIs.

## `experiment_tracker.schema.json` Review

Observed additions:

- Optional `scoring` object with required:
  - `raw_scores`
  - `adjusted_scores`
  - `total_score`
  - `priority_bucket`
- Each raw score is constrained to integer 1-5.
- Priority bucket enum is `A`, `B`, `C`, or `D`.

Open review items:

- Claude should verify the JSON schema still matches the helper script's emitted record shape.
- Claude should validate existing starter JSONL records remain valid or intentionally schema-compatible.

## `sample_video_notes_n3_18.md` Review

Observed content:

- Fictional sample notes, not scraped from YouTube.
- Mentions a video-to-business-system extractor concept.
- Includes distribution/email list insight, a prompt pack product idea, content angles, and risk notes.
- Does not require live accounts, scraping, posting, or external actions.

## Static Validation Truth

Codex ran static-only checks and did not run Gemma/Ollama inference:

- `local_brain_router.py` AST parse: PASS.
- `money_workflow_new_experiment.py` AST parse: PASS.
- `experiment_tracker.schema.json` JSON parse: PASS.
- `git diff --check`: PASS with line-ending warnings only for existing dirty files.

## What Appears Complete

- Core `video_to_money` route scaffolding exists.
- Core money experiment scoring logic exists.
- Schema additions exist.
- Sample input file exists.
- Static syntax/JSON checks pass.

## What Is Incomplete

- Gemma video-to-money smoke test has not been run in this Codex pass.
- Scoring dry-run has not been run in this Codex pass.
- N+3.18 implementation docs are not yet created:
  - `14_context/gemma_video_to_money_runner_n3_18.md`
  - `14_context/money_experiment_scoring_n3_18.md`
  - `14_context/money_runner_safety_review_n3_18.md`
  - `14_context/distribution_exposure_system_n3_18.md`
- `wait_resume_supervisor.py` was not updated.
- `current_state.md`, `next_actions.md`, and `ghoti_finish_line_log.md` were not updated.
- Final validation, staging, commit, and push were not performed by Claude before interruption.
