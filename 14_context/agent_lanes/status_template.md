# Status Template

Copy this file to emit a status beacon. Append the filled record to
lane_status.jsonl using 03_scripts/agent_lane_status.py --new-status --apply.

status_id: "status_<YYYYMMDDTHHMMSSZ>_<hash8>"
agent_id: ""
lane_type: ""
model_or_tool: ""
branch: ""
task_slug: ""

current_state: ""

notes:
  - ""

safety_notes: |
  Any safety-relevant state for this beacon.

stop_conditions:
  - "Two consecutive failures on same root cause"
  - "Any outbound/live action without approval"

timestamp_utc: ""

## Valid States

| State | Meaning |
|-------|---------|
| started | Lane declared, work beginning |
| in_progress | Actively writing files |
| blocked | Waiting on lock from another agent |
| waiting_approval | Waiting for human approval gate |
| dry_run | Dry-run mode, no writes committed |
| complete | Work done, outputs ready for review |
| released | Lock released, branch merged or abandoned |
