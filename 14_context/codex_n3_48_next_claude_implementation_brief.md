# Codex N+3.48 - Next Claude Implementation Brief

Milestone: N+3.48 - Post-Merge Audit + 80 Percent Roadmap Lock

Date: 2026-05-06

## Recommended Next Claude Milestone

```text
N+3.49 - Prompt Bus Dashboard + Context Pack Generator + Lane Status Beacon Helper
```

This is the highest-leverage next implementation because it makes the new N+3.45 rails usable day-to-day. Do not start Ruflo/OpenClaw/Paperclip/n8n/CUA runtime work yet.

## Current Truth To Inspect First

Claude should inspect:

- `03_scripts/prompt_bus.py`
- `03_scripts/local_worker_router.py`
- `03_scripts/agent_lane_status.py`
- `14_context/prompt_bus/README.md`
- `14_context/prompt_bus/templates/`
- `14_context/agent_lanes/active_locks.jsonl`
- `14_context/agent_lanes/lane_status.jsonl`
- `14_context/agent_lanes/shared_file_lock_policy.md`
- `23_configs/local_worker_routing.example.json`
- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`

## Implementation Goals

1. Add a context pack generator:

```text
03_scripts/prompt_context_pack.py
```

Requirements:

- Python stdlib only.
- Repo-local only.
- Dry-run by default.
- `--apply` required for writes.
- Inputs:
  - current goal text or `--goal-file`
  - branch
  - lane id
  - allowed paths
  - forbidden paths
  - validation commands
  - source files
- Outputs under:
  - `05_logs/prompt_context_packs/<run_id>/`
- Artifacts:
  - `context_pack.md`
  - `context_pack.json`
  - `claude_prompt.md`
  - `codex_prompt.md`
  - `chatgpt_handoff.md`
  - `run_summary.json`

2. Add a read-only dashboard route/card:

Suggested route:

```text
GET /api/ghoti/prompt-bus/summary
```

Must read:

- `14_context/prompt_bus/`
- `14_context/ghoti_current_prompt.md` if present
- `14_context/agent_lanes/active_locks.jsonl`
- `14_context/agent_lanes/lane_status.jsonl`
- `23_configs/local_worker_routing.example.json`
- optional latest `05_logs/prompt_context_packs/<run_id>/run_summary.json`

Must tolerate:

- missing files
- empty JSONL
- malformed JSONL lines
- no prompt packs yet
- stale locks

No mutation buttons.

3. Add lane status beacon helper behavior:

Option A:

- Extend `03_scripts/agent_lane_status.py` with a safe status append mode if not already enough.

Option B:

- Add `03_scripts/lane_beacon.py`.

Rules:

- Append-only JSONL.
- Dry-run default.
- `--apply` required.
- Validate repo-relative paths.
- Never edit/delete existing lock/status entries.

## Safety Boundaries

Forbidden:

- live accounts
- posting
- sending email
- payment
- scraping
- job applications
- giveaway entries
- Ruflo/OpenClaw/Paperclip/n8n/CUA/browser runtime
- external APIs
- installing dependencies
- secrets or `.env` reads
- dashboard mutation buttons

Allowed:

- local file reads
- local dry-run previews
- local `--apply` writes to approved repo paths
- read-only dashboard route/card
- append-only JSONL status records
- generated prompt/context artifacts under `05_logs/prompt_context_packs/`

## Validation Commands

Run at minimum:

```powershell
git diff --check
python -m py_compile 03_scripts/prompt_context_pack.py
python -m py_compile 03_scripts/agent_lane_status.py
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
python 03_scripts/prompt_context_pack.py --help
python 03_scripts/prompt_context_pack.py --goal "N+3.49 smoke" --lane-id claude_code_n3_49 --branch feat/ghoti-visible-operator-stack --dry-run
python 03_scripts/agent_lane_status.py --check
python 03_scripts/prompt_bus.py --status
```

If JSON files are touched:

```powershell
python -m json.tool 23_configs/local_worker_routing.example.json
```

## Staging Rules

Stage only intentional N+3.49 files. Do not stage:

- unrelated local dirt
- generated logs unless explicitly approved
- Ruflo eval repo files
- CV docs
- prompt scratch files
- live-account or connector files

## Commit Message Suggestion

```text
feat(ghoti): add prompt bus context packs and dashboard read view
```

## Expected Outcome

If implemented well, this should move Ghoti from roughly **68%** to about **74%** by making prompt/lane/local-worker coordination visible and repeatable.
