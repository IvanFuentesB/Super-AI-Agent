# Lock Template

Copy this file to declare a shared-file lock. Append the filled record to
active_locks.jsonl using 03_scripts/agent_lane_status.py --new-lock --apply.

lock_id: "lock_<YYYYMMDDTHHMMSSZ>_<hash8>"
agent_id: ""
lane_type: ""
model_or_tool: ""
branch: ""
task_slug: ""

locked_files:
  - ""

allowed_paths:
  - ""

forbidden_paths:
  - ""

expected_outputs:
  - ""

validation_plan: |
  How outputs will be validated before the lock is released.

merge_plan: |
  Merge strategy: branch, reviewer, checks.

human_approval_requirement: |
  Required for: outbound actions, live mutations, installs, external API calls.

safety_notes: |
  Constraints and known risks.

stop_conditions:
  - "Two consecutive failures on same root cause"
  - "Any attempt to write to files not in locked_files or allowed_paths"
  - "Any outbound/live action without approval"

timestamp_utc: ""
