# Example: Python Automation Worker Lock (weekly review)

This is an EXAMPLE ONLY — not an active lock.

{
  "lock_id": "lock_20260505T180000Z_d4e5f6a7",
  "agent_id": "python_automation_worker_weekly_review_001",
  "lane_type": "python_automation_worker",
  "model_or_tool": "python3",
  "branch": "feat/ghoti-agent-python_automation_worker-weekly-review",
  "task_slug": "weekly-money-review-run",
  "locked_files": [],
  "allowed_paths": [
    "05_logs/money_reviews/",
    "output/"
  ],
  "forbidden_paths": [
    "14_context/current_state.md",
    "14_context/next_actions.md",
    "14_context/compact_memory/",
    "21_repos/third_party/"
  ],
  "expected_outputs": [
    "05_logs/money_reviews/<run_id>/weekly_review.json",
    "05_logs/money_reviews/<run_id>/weekly_review.md",
    "05_logs/money_reviews/<run_id>/decisions_recommended.jsonl"
  ],
  "validation_plan": "AST check script; dry-run PASS; verify output files created; confirm no external calls; confirm approval_required=true on all decisions",
  "merge_plan": "Script output is local artifact only. Human reviews weekly_review.md. No merge to main required for run outputs.",
  "human_approval_requirement": "Human must review decisions_recommended.jsonl before any decision is acted on. No live actions from this lane.",
  "safety_notes": "stdlib only; no external API; no model calls; no live sends/posts/payments; all outputs are local artifacts",
  "stop_conditions": [
    "Any external API call attempt",
    "Any live action attempt",
    "Two consecutive failures on same root cause"
  ],
  "timestamp_utc": "2026-05-05T18:00:00Z"
}
