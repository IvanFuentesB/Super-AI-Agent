# Example Lock: Gemma Local Worker Lane

This is an example only. It is not an active lock.

- lock_id: lock_example_gemma_local_worker
- agent_id: gemma_example
- lane_type: gemma_local_worker
- model_or_tool: Gemma/Ollama
- branch: docs/ghoti-agent-gemma-example-compression
- task_slug: example-compression
- locked_files:
  - `14_context/compact_memory/project_state.md`
- allowed_paths:
  - `14_context/compact_memory/`
  - `05_logs/local_brain_runs/`
- forbidden_paths:
  - runtime files
  - credentials
  - live account config files
- expected_outputs:
  - compact memory draft
  - source pointer list
  - unknown-facts list
- validation_plan:
  - human review against source files
  - `git diff --check` if draft is promoted
- safety_notes:
  - model output is draft only
  - no external API calls
  - no canonical overwrite without human promotion
- human_approval_required_for_merge: yes
