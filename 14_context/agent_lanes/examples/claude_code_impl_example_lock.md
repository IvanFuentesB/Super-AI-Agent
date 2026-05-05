# Example Lock: Claude Code Implementation Lane

This is an example only. It is not an active lock.

- lock_id: lock_example_claude_code_impl
- agent_id: claude_code_example
- lane_type: claude_code_impl
- model_or_tool: Claude Code
- branch: feat/ghoti-agent-claude-example-implementation
- task_slug: example-implementation
- locked_files:
  - `03_scripts/example_helper.py`
  - `14_context/current_state.md`
- allowed_paths:
  - `03_scripts/`
  - `14_context/`
- forbidden_paths:
  - `.env`
  - `05_logs/`
  - live account config files
- expected_outputs:
  - local helper script
  - implementation doc
  - validation evidence
- validation_plan:
  - `python -m py_compile 03_scripts/example_helper.py`
  - `git diff --check`
- safety_notes:
  - no external tools
  - no live actions
  - no generated logs staged unless approved
- human_approval_required_for_merge: yes
