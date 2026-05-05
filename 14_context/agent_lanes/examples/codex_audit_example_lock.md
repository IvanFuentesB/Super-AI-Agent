# Example Lock: Codex Audit Lane

This is an example only. It is not an active lock.

- lock_id: lock_example_codex_audit
- agent_id: codex_example
- lane_type: codex_audit
- model_or_tool: Codex
- branch: audit/ghoti-agent-codex-example-source-check
- task_slug: example-source-check
- locked_files:
  - `14_context/codex_example_source_check.md`
- allowed_paths:
  - `14_context/`
- forbidden_paths:
  - `01_projects/`
  - `03_scripts/`
  - live account config files
- expected_outputs:
  - audit doc
  - risk matrix
  - next-sequence recommendation
- validation_plan:
  - `git diff --check`
- safety_notes:
  - docs/source-check only
  - no runtime implementation
  - no installs, clones, or external tool execution
- human_approval_required_for_merge: yes
