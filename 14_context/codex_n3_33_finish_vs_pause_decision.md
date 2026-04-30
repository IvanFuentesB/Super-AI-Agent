# Codex N+3.33 Finish Vs Pause Decision

Status: codex_audit_only / finish_vs_pause / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 384a5fe

## Recommendation

Prefer finishing N+3.18 later with Claude Code.

The dirty work is coherent and bounded enough that throwing it away would waste useful implementation progress. It should not be committed as-is, but it is a good continuation point once Claude credits return.

## Decision Criteria

Finish N+3.18 if:

- Python files compile
- schema JSON parses
- existing tracker JSONL parses
- `video_to_money` smoke writes expected artifacts
- scoring dry-run produces expected scoring object
- parser brittleness is fixed or explicitly documented
- policy/config/docs/state logs are updated
- only intentional N+3.18 files are staged

Pause N+3.18 if:

- the router cannot pass AST/compile validation
- the Gemma/Ollama call path is broken in the current environment
- parser fixes expand into a larger refactor
- the operator wants to prioritize planning-only docs until Claude credits return
- dirty N+3.18 files block other urgent work and the operator approves parking them safely

## Risks Of Finishing

- Claude may need tokens to understand dirty diffs before implementing.
- `video_to_money` parser may need repair to avoid losing multiple experiment candidates.
- Policy/config updates may be required to make the route discoverable.
- Generated artifacts under `05_logs/money_runs/` could add staging noise.
- If N+3.18 is mixed with later dashboard milestones, staging mistakes become more likely.

## Risks Of Pausing

- Dirty runtime/script/schema files remain in the working tree.
- Later N+3.29 through N+3.32 implementation depends on N+3.18 foundations.
- More planning docs can pile up without executable Money OS progress.
- Claude may spend future tokens rediscovering the same dirty-state truth.
- The branch remains harder to reason about because tracked files are modified but not committed.

## Preferred Path

Preferred path:

```text
Finish N+3.18 with Claude Code as the next implementation action.
```

If Claude credits are still unavailable:

```text
Do not implement runtime changes with Codex. Keep Codex to narrow audit/source review only.
```

## Minimum Viable Finished Definition

N+3.18 is minimally finished when:

- `local_brain_router.py` includes stable `video_to_money`
- `money_workflow_new_experiment.py` includes stable scoring
- `experiment_tracker.schema.json` matches the produced scoring shape
- `sample_video_notes_n3_18.md` is either intentionally staged or intentionally omitted
- `video_to_money` smoke writes artifacts under `05_logs/money_runs/<run_id>/`
- scoring dry-run command passes
- implementation docs are written:
  - `14_context/gemma_video_to_money_runner_n3_18.md`
  - `14_context/money_experiment_scoring_n3_18.md`
  - `14_context/money_runner_safety_review_n3_18.md`
  - `14_context/distribution_exposure_system_n3_18.md`
- wait/resume/current_state/next_actions/finish_line_log are updated if that remains the repo convention
- validation commands pass
- only intentional files are staged
- commit and push complete

## Minimum Viable Paused Definition

N+3.18 is minimally paused when:

- Claude records a pause note under `14_context/`
- dirty files are not lost
- exact dirty files and reason for pause are documented
- no runtime files are staged
- the next action says whether to finish, branch, stash, or revert later
- any cleanup is done only with explicit operator approval

Codex should not pause by reverting or cleaning files. That is an implementation/worktree operation that requires explicit operator direction.

## Why More Codex Planning Cannot Replace Implementation

The missing work is not more strategy. It is validation and code completion:

- compile the dirty Python files
- run local smoke commands
- inspect generated artifacts
- harden parser behavior
- align schema/config/docs
- stage only intentional implementation files
- commit and push

Codex can map and preserve the path, but it should not substitute for Claude's implementation lane while the user explicitly asked Codex not to touch runtime files.

## Verdict

Finish later with Claude. Do not commit the dirty work as-is. Do not continue stacking implementation-dependent milestones until N+3.18 is either finished or consciously parked.
