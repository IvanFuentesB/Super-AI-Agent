# Money Runner Safety Review — N+3.18

Status: reviewed / artifact_only / no_live_actions / approval_gates_preserved

Date: 2026-05-01
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.18

## Scope

This review covers the safety posture of:

- `local_brain_router.py` `video_to_money` task path
- `money_workflow_new_experiment.py` scoring extension
- `experiment_tracker.schema.json` scoring schema

## Safety Properties Verified

### No External API Calls

The `video_to_money` path calls `ollama run` via subprocess only. No HTTP requests to external services, no cloud APIs, no CDN uploads.

### No Live Account Access

The runner does not authenticate to, read from, or write to any external platform (Whop, TikTok, YouTube, email service, LinkedIn, GitHub issues, Stripe, etc.).

### No Model Output Execution

The model response is parsed into structured markdown sections and written as draft artifacts. The response text is never passed to `eval`, `exec`, `subprocess`, or any shell.

### No Auto-Post / Auto-Sell / Auto-Email

All three flags are explicitly `false` in every `request.json` and `run_summary.json`.

### No Auto-Commit From Model Output

Model output does not trigger any git operations. The runner writes local artifact files only.

### Approval Gate Preserved

`approval_required_for_any_use: true` is hardcoded in every run summary. Candidate records always have `approval_required: True` (boolean). Model-emitted strings cannot override this — the parser forces boolean `True` after building each entry.

### Input Path Restriction

Uses existing `_resolve_input_path()` which:
- Rejects absolute paths outside the repo root
- Rejects traversal (e.g. `../../etc/passwd`)
- Further restricts to `.md` and `.txt` only for this task

### Input Size Bound

Clipped at `max_chars` (default 12000) before sending to model. Prevents unbounded token usage.

### Artifact-Only Outputs

All artifacts are written under `05_logs/money_runs/<run_id>/`. No writes to user home, system dirs, or external storage.

### No Fake Proof

The runner and its docs explicitly state all outputs are draft artifacts and planning estimates. No revenue claims, no testimonials, no income proof, no validated metrics are generated or implied.

## Known Limitations

| Limitation | Status |
|-----------|--------|
| Parser depends on model output format (## headings) | Accepted; falls back to raw_text if sections not found |
| Candidate count depends on model returning multiple candidates | Accepted; parser now splits on anchor key repeat to reduce collapse |
| Scoring is subjective heuristic | Documented in scoring docs; caveat present in help text |
| Ollama must be running locally | Graceful fail path documented and tested |
| Model output may vary across Gemma versions | Artifacts will vary; not a safety risk |

## Risk Classification

| Risk Category | Level | Notes |
|--------------|-------|-------|
| Legal/TOS risk | Low | No scraping, no posting, no accounts |
| Claims risk | Low | All outputs labeled as drafts |
| Fake proof risk | Low | Explicitly blocked by design and docs |
| Spam/fake engagement | Low | No outbound messages |
| Live account exposure | None | No auth, no sessions |
| Data leak | Low | Local-only; no external write paths |

## Approval Required Before Any Use

Before acting on any artifact from this runner:

1. Human reviews the draft artifact
2. Human approves the specific action (post, sell, email, etc.)
3. No automated pipeline consumes runner output
