# Codex N+3.30 Artifact Parser Tolerant Model

Status: codex_planning_only / artifact_parser_tolerant_model / not_runtime_wired

Date: 2026-04-29
Branch: feat/ghoti-visible-operator-stack

## Purpose

Specify the tolerant parser model for the future weekly review artifact dashboard route. The parser must safely summarize generated artifacts even when the directory is missing, individual files are absent, JSON is malformed, JSONL has bad lines, or Gemma output is imperfect.

## Source Root

Allowed root:

```text
05_logs/money_reviews/
```

The parser should not accept a query parameter for arbitrary paths in the first implementation. It should scan only this fixed root.

## Run Directory Detection

Valid run directory rules:

- child of `05_logs/money_reviews/`
- directory only
- name starts with `mrev_` or is otherwise timestamp-like if N+3.29 chooses a different safe prefix
- resolved path remains inside the money reviews root
- ignore hidden/system directories

Sort order:

1. parse timestamp from run ID if possible
2. fallback to modified time
3. newest first

Cap:

- inspect latest 20 directories
- return latest 10 summaries

## File Parsers

### JSON: `run_summary.json`

Behavior:

- parse if present
- tolerate missing file
- tolerate invalid JSON with warning
- include only safe scalar/array/object fields needed for dashboard
- do not expose huge raw payloads

Important fields:

- `run_id`
- `created_at_utc`
- `status`
- `artifact_files`
- `tracker_mutated`
- `queue_mutated`
- `live_actions_taken`
- `external_api_used`
- `model_output_executed`
- `manual_review_required`

### Markdown: `weekly_summary.md`, `next_10_shots.md`, `risk_review.md`

Behavior:

- read if present
- cap characters
- normalize line endings
- strip null bytes
- return excerpt only
- do not render HTML as trusted
- UI must escape text

Suggested cap:

- 1200 characters per excerpt

### JSONL: `decisions_recommended.jsonl`

Behavior:

- parse line by line
- skip blank lines
- continue after malformed lines
- cap parse errors to five samples
- count decision types
- return top three valid candidates
- reject candidates with missing required fields
- reject candidates with status other than `candidate`
- never append candidates to any queue

## Warning Model

Warnings should be objects, not just strings, when possible:

```json
{
  "level": "warn",
  "source": "decisions_recommended.jsonl",
  "code": "malformed_jsonl_line",
  "message": "Line 4 could not be parsed and was ignored."
}
```

Warning levels:

- `info`
- `warn`
- `safety`
- `error`

Safety warnings:

- run summary missing safety flags
- `tracker_mutated` is true
- `queue_mutated` is true
- `live_actions_taken` is true
- `external_api_used` is true
- `model_output_executed` is true
- candidate suggests automatic live action

## Decision Candidate Ranking

For dashboard top three:

1. Prefer valid candidates with `confidence: high`.
2. Then `confidence: medium`.
3. Then `confidence: low`.
4. Prefer decision types in this order:
   - `DOUBLE_DOWN`
   - `BUILD_NEXT`
   - `CREATE_CONTENT_BATCH`
   - `CREATE_LEAD_MAGNET`
   - `ITERATE`
   - `COLLECT_MORE_DATA`
   - `REVIEW_LAUNCH_CHECKLIST`
   - `PAUSE`
   - `KILL`
5. Preserve original file order as final tie-breaker.

Do not imply ranking is financial certainty.

## Zero-State Model

When root is missing:

- `status: "zero_state"`
- `runs_total: 0`
- `latest_run: null`
- warning: root missing
- all arrays empty
- all counts zero

When run exists but files missing:

- include run directory
- warning per missing required file
- return available fields
- do not fail whole route

When malformed files exist:

- include parse warnings
- return partial valid data
- flag run as `partial`

## Security Boundaries

The parser must not:

- follow symlinks outside root
- accept arbitrary path input
- serve raw files
- execute markdown, HTML, scripts, shell, or model output
- call external APIs
- run Gemma
- mutate source files
- append decision queue

## Response Flags

Include:

```json
{
  "read_only": true,
  "artifact_root": "05_logs/money_reviews",
  "mutation_enabled": false,
  "model_execution_enabled": false,
  "live_actions_enabled": false
}
```

## Validation Fixtures For Claude

Future tests or smoke fixtures should cover:

- missing `05_logs/money_reviews/`
- empty root
- one valid run
- run missing `run_summary.json`
- malformed `run_summary.json`
- malformed line in `decisions_recommended.jsonl`
- risk review with long content requiring truncation
- run summary with unsafe flag true

## Verdict

The parser should be boring, narrow, and defensive. It reads the weekly review packet and surfaces warnings; it does nothing else.
