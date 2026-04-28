# Codex N+3.18 Video-to-Money Runner Review

Status: codex_followup_audit_only / runner_review / not_runtime_wired

## Expected Behavior

The N+3.18 `video_to_money` runner should let Ghoti take local notes or a transcript-like markdown/text file and ask the local Gemma/Ollama brain to produce structured money workflow artifacts.

The runner should:

- Accept local `.md` or `.txt` input only.
- Stay inside the repo root.
- Never fetch URLs.
- Never scrape YouTube or any third-party site.
- Never download videos or transcripts.
- Never post, sell, email, outreach, submit, pay, trade, or use live accounts.
- Write artifacts only.
- Treat all model output as suggestions, never executable instructions.
- Require human approval before any public, account, money-facing, or distribution action.

## Dirty Implementation Truth

The dirty `local_brain_router.py` implementation appears to satisfy the core shape:

- `--task video_to_money --input <path>` route exists.
- `.md` and `.txt` are the only allowed video-to-money extensions.
- Input path goes through the existing repo-root resolver.
- Prompt asks for source summary, product ideas, content angles, experiment candidates, distribution plan, and risk review.
- Run folder is created under `05_logs/money_runs/<run_id>/`.
- Request and source excerpt artifacts are written before model execution.
- Model output is split into separate markdown artifacts.
- `experiment_candidates.jsonl` is generated from the candidate section.
- `run_summary.json` records no external calls, no auto-post, no auto-sell, no auto-email, no model-output execution, and approval required.

## Artifact Requirements

Before Claude commits the implementation, a successful smoke run should produce at least:

- `request.json`
- `source_excerpt.md`
- `source_summary.md` or a clearly documented equivalent
- `product_ideas.md`
- `content_angles.md`
- `experiment_candidates.jsonl`
- `distribution_plan.md`
- `risk_review.md`
- `run_summary.json`

`run_summary.json` should include:

- `task_type: video_to_money`
- input file path
- provider and model
- exit code
- artifact list
- `api_usage: none`
- `external_calls: none`
- `model_output_executed: false`
- `auto_post: false`
- `auto_sell: false`
- `auto_email: false`
- `approval_required_for_any_use: true`

## Missing Docs And Tests

Still missing from Claude's partial N+3.18 work:

- `14_context/gemma_video_to_money_runner_n3_18.md`
- `14_context/money_experiment_scoring_n3_18.md`
- `14_context/money_runner_safety_review_n3_18.md`
- `14_context/distribution_exposure_system_n3_18.md`
- Gemma smoke output for the sample notes file.
- Confirmation that `experiment_candidates.jsonl` parses candidate records correctly.
- Confirmation that the runner handles missing Ollama/Gemma gracefully.
- State doc updates and finish-line log entry.

## Safety Requirements

The final implementation must preserve these safety requirements:

- Local input only; no URL fetch or scraping.
- Artifact output only; no live actions.
- No model output execution.
- No live posting, selling, outreach, email, payment, trading, app-store action, or account action.
- No fake proof, fake engagement, spam, or deceptive claims.
- No Paperclip/OpenClaw/n8n/Unity-MCP/Mythos/Dolphin/CUDA install or runtime wiring.
- Human approval required before any public or money-facing use.

## Review Verdict

The dirty implementation is promising and appears directionally correct, but it is not done. It should not be committed until Claude runs the Gemma smoke, validates candidate JSONL output, writes the missing docs, updates state, and stages only intentional N+3.18 files.
