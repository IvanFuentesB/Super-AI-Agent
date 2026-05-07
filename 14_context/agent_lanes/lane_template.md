# Lane Template

Copy this file and fill all fields before starting any parallel agent work.
Machine-readable fields required for lock validation.

lane_id: "lane_<YYYYMMDDTHHMMSSZ>_<agent_id>"
agent_id: ""
lane_type: ""
model_or_tool: ""
branch: ""
task_slug: ""

allowed_paths:
  - ""

forbidden_paths:
  - "14_context/current_state.md"
  - "14_context/next_actions.md"
  - "14_context/ghoti_finish_line_log.md"

locked_files: []

expected_outputs:
  - ""

validation_plan: |
  Describe how outputs will be validated before merge.

merge_plan: |
  Describe the merge strategy: which branch, who reviews, what checks run.

human_approval_requirement: |
  List every action type that requires explicit human approval before execution.
  Outbound actions, live account mutations, installs, external API calls = always required.

safety_notes: |
  Any constraints, known risks, or edge cases for this lane.

stop_conditions:
  - "Two consecutive failures on same root cause"
  - "Any attempt to write outside allowed_paths"
  - "Any attempt to execute live/outbound action without approval"
  - "Any attempt to write a locked shared file without owning the lock"
