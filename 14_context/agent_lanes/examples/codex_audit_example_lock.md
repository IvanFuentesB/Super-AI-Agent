# Example: Codex Audit Lock (post N+3.43 audit)

This is an EXAMPLE ONLY — not an active lock.

{
  "lock_id": "lock_20260505T140000Z_b2c3d4e5",
  "agent_id": "codex_audit_n3_44",
  "lane_type": "codex_audit",
  "model_or_tool": "codex",
  "branch": "audit/ghoti-agent-codex_audit-n3_44-lane-verification",
  "task_slug": "n3-44-lane-verification",
  "locked_files": [],
  "allowed_paths": [
    "14_context/"
  ],
  "forbidden_paths": [
    "03_scripts/",
    "01_projects/",
    "21_repos/third_party/"
  ],
  "expected_outputs": [
    "14_context/codex_n3_44_post_n3_43_audit.md",
    "14_context/codex_n3_44_next_sequence_lock.md"
  ],
  "validation_plan": "Verify all 9 Part-A files exist; run agent_lane_status.py --check; confirm PASS; document findings in audit doc",
  "merge_plan": "Push audit branch; human reviews audit doc; if PASS, controlled parallel execution may begin",
  "human_approval_requirement": "Human must review audit doc before declaring parallel execution safe",
  "safety_notes": "Audit only — no implementation, no runtime changes, no live actions",
  "stop_conditions": [
    "Any attempt to write implementation files",
    "Any outbound/live action"
  ],
  "timestamp_utc": "2026-05-05T14:00:00Z"
}
