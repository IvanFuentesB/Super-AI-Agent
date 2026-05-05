# Example: Claude Code Implementation Lock (N+3.43 scaffolding)

This is an EXAMPLE ONLY — not an active lock.
Append real lock records to 14_context/agent_lanes/active_locks.jsonl
using 03_scripts/agent_lane_status.py --new-lock --apply.

{
  "lock_id": "lock_20260505T120000Z_a1b2c3d4",
  "agent_id": "claude_code_n3_43",
  "lane_type": "claude_code_impl",
  "model_or_tool": "claude-sonnet-4-6",
  "branch": "feat/ghoti-visible-operator-stack",
  "task_slug": "agent-lane-scaffolding",
  "locked_files": [
    "14_context/current_state.md",
    "14_context/next_actions.md",
    "14_context/ghoti_finish_line_log.md"
  ],
  "allowed_paths": [
    "03_scripts/agent_lane_status.py",
    "14_context/agent_lanes/",
    "14_context/agent_lane_locks_n3_43.md",
    "14_context/current_state.md",
    "14_context/next_actions.md",
    "14_context/ghoti_finish_line_log.md",
    "14_context/obsidian_vault/07_Agent_Routing.md",
    "14_context/compact_memory/agent_routing_memory.md"
  ],
  "forbidden_paths": [
    "21_repos/third_party/",
    "01_projects/runtime_mvp/src/super_ai_agent/server.js",
    "01_projects/runtime_mvp/src/super_ai_agent/app.js"
  ],
  "expected_outputs": [
    "14_context/agent_lanes/README.md",
    "14_context/agent_lanes/agent_lane_registry.json",
    "14_context/agent_lanes/active_locks.jsonl",
    "14_context/agent_lanes/lane_status.jsonl",
    "03_scripts/agent_lane_status.py",
    "14_context/agent_lane_locks_n3_43.md"
  ],
  "validation_plan": "AST check agent_lane_status.py; --check PASS; --list PASS; --new-lock dry-run PASS; --new-status dry-run PASS; registry JSON valid; JSONL valid",
  "merge_plan": "Commit to feat/ghoti-visible-operator-stack; push to origin; Codex audit confirms lane locks pass before controlled parallel begins",
  "human_approval_requirement": "Push to remote requires human awareness; no outbound/live actions in this lane",
  "safety_notes": "Scaffolding only — no parallel agents run, no external tools, no live actions",
  "stop_conditions": [
    "Two consecutive failures on same root cause",
    "Any attempt to write outside allowed_paths",
    "Any outbound/live action without approval"
  ],
  "timestamp_utc": "2026-05-05T12:00:00Z"
}
