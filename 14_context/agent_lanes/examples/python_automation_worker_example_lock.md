# Example Lock: Python Automation Worker Lane

This is an example only. It is not an active lock.

- lock_id: lock_example_python_automation_worker
- agent_id: python_worker_example
- lane_type: python_automation_worker
- model_or_tool: Python stdlib
- branch: feat/ghoti-agent-python-example-jsonl-summary
- task_slug: example-jsonl-summary
- locked_files:
  - `03_scripts/example_jsonl_summary.py`
  - `14_context/example_summary.md`
- allowed_paths:
  - `03_scripts/`
  - `14_context/`
  - `05_logs/`
- forbidden_paths:
  - `.env`
  - external account config files
  - files outside the repo
- expected_outputs:
  - deterministic parser
  - local markdown summary
  - validation output
- validation_plan:
  - `python -m py_compile 03_scripts/example_jsonl_summary.py`
  - local JSONL parse smoke
  - `git diff --check`
- safety_notes:
  - no network
  - no scraping
  - no emails/posts/payments
  - no credential use
- human_approval_required_for_merge: yes
