# Example: Gemma Local Worker Lock (context compression)

This is an EXAMPLE ONLY — not an active lock.

{
  "lock_id": "lock_20260505T160000Z_c3d4e5f6",
  "agent_id": "gemma_local_worker_compress_001",
  "lane_type": "gemma_local_worker",
  "model_or_tool": "gemma3:4b",
  "branch": "feat/ghoti-agent-gemma_local_worker-compress-context",
  "task_slug": "compress-context-batch-01",
  "locked_files": [],
  "allowed_paths": [
    "05_logs/local_brain_runs/",
    "output/"
  ],
  "forbidden_paths": [
    "14_context/current_state.md",
    "14_context/next_actions.md",
    "14_context/compact_memory/",
    "03_scripts/",
    "01_projects/"
  ],
  "expected_outputs": [
    "05_logs/local_brain_runs/<run_id>/compressed_context.md",
    "05_logs/local_brain_runs/<run_id>/summary.json"
  ],
  "validation_plan": "Verify output files created; model output is draft only; human reviews before any canonical use",
  "merge_plan": "No merge to main — outputs are draft artifacts only. Human operator promotes if useful.",
  "human_approval_requirement": "Human must review and explicitly promote any Gemma output before it becomes canonical state",
  "safety_notes": "gemma3:4b via Ollama only — no external API; outputs are never source of truth without human promotion",
  "stop_conditions": [
    "Ollama unavailable",
    "Any attempt to write canonical state files",
    "Any external API call"
  ],
  "timestamp_utc": "2026-05-05T16:00:00Z"
}
