# N+3.43 — Agent Lane Locks And Parallel Execution Scaffolding

Delivered: 2026-05-05
Branch: feat/ghoti-visible-operator-stack
Status: scaffolding_only — no parallel agents run, no external tools, no live actions

## Scope

This milestone creates the local safety foundation for future controlled parallel agent execution. It does NOT run parallel agents, connect external tools, or perform any live actions. It adds: lane templates, registry, append-only JSONL state files, example lock files, docs, and a helper script.

## Files Created

### Agent Lane Folder (Part A)
- 14_context/agent_lanes/README.md — lane system overview
- 14_context/agent_lanes/lane_template.md — machine-readable lane declaration template
- 14_context/agent_lanes/lock_template.md — shared-file lock record template
- 14_context/agent_lanes/status_template.md — status beacon template
- 14_context/agent_lanes/merge_checklist.md — pre-merge validation checklist
- 14_context/agent_lanes/shared_file_lock_policy.md — shared files requiring locks
- 14_context/agent_lanes/agent_lane_registry.json — 8 agent role definitions
- 14_context/agent_lanes/active_locks.jsonl — append-only active lock records (starts empty)
- 14_context/agent_lanes/lane_status.jsonl — append-only status beacons (starts empty)

### Helper Script (Part B)
- 03_scripts/agent_lane_status.py — CLI: --check, --list, --new-lock, --new-status

### Example Lock Files (Part C)
- 14_context/agent_lanes/examples/claude_code_impl_example_lock.md
- 14_context/agent_lanes/examples/codex_audit_example_lock.md
- 14_context/agent_lanes/examples/gemma_local_worker_example_lock.md
- 14_context/agent_lanes/examples/python_automation_worker_example_lock.md

## Helper Script Usage

  python 03_scripts/agent_lane_status.py --check
  python 03_scripts/agent_lane_status.py --list
  python 03_scripts/agent_lane_status.py --new-lock --agent-id claude_code_n3_43 --lane-type claude_code_impl --task-slug agent-lane-scaffolding --branch feat/ghoti-visible-operator-stack --locked-file 14_context/current_state.md --locked-file 14_context/next_actions.md --dry-run
  python 03_scripts/agent_lane_status.py --new-status --agent-id claude_code_n3_43 --lane-type claude_code_impl --task-slug agent-lane-scaffolding --branch feat/ghoti-visible-operator-stack --current-state dry_run --dry-run

## How to Start a Lane

1. Copy lane_template.md, fill all required fields.
2. Create a branch: feat/ghoti-agent-<agent_id>-<task_slug>
3. Declare locked shared files in locked_files field.
4. Run --new-lock --apply to record the lock.
5. Run --new-status --apply --current-state started to emit a beacon.
6. Do the work within declared allowed_paths only.
7. On completion: run --new-status --apply --current-state complete.

## How to Check Lanes

  python 03_scripts/agent_lane_status.py --check
  python 03_scripts/agent_lane_status.py --list

--check exits non-zero only on true validation failure (missing files, invalid JSON/JSONL).
--list prints active locks and latest statuses; works with empty JSONL files.

## How to Merge Safely

1. Run --check -> PASS
2. Review merge_checklist.md — every item ticked
3. Confirm no shared-file lock conflicts
4. Confirm no outbound/live actions in diff
5. Merge branch; push to origin
6. Append released status: --new-status --current-state released --apply
7. Update current_state.md and next_actions.md concisely

## What Is Allowed After N+3.43

- Use agent_lane_status.py to declare and track lanes
- Use lane templates to plan parallel agent work
- Use example lock files as reference for real locks
- Read agent_lane_registry.json to understand role boundaries
- Run --check and --list at any time

## What Is Still Forbidden

- Uncontrolled parallel agent execution (no lane declaration)
- Parallel execution before Codex audit confirms lane locks pass
- Writing shared locked files without owning the lock
- Any external/live/account/money actions without approval
- Installing packages, cloning repos, connecting new MCP servers
- Course impersonation, credential fabrication
- Deleting history, memory, task, or audit files

## Exact Command Examples

  python 03_scripts/agent_lane_status.py --check
  python 03_scripts/agent_lane_status.py --list
  python 03_scripts/agent_lane_status.py --new-lock --agent-id claude_code_n3_43 --lane-type claude_code_impl --task-slug agent-lane-scaffolding --branch feat/ghoti-visible-operator-stack --locked-file 14_context/current_state.md --locked-file 14_context/next_actions.md --dry-run
  python 03_scripts/agent_lane_status.py --new-status --agent-id claude_code_n3_43 --lane-type claude_code_impl --task-slug agent-lane-scaffolding --branch feat/ghoti-visible-operator-stack --current-state dry_run --dry-run

## Controlled Parallel Pilot Note

Controlled parallel execution can begin only after this commit is pushed and Codex audit confirms the lane locks pass.

## Course/Certificate Future Lane Safety Note

The future_course_certificate_assistant lane is planning_only. When activated it must only provide: course discovery, study plans, notes, quizzes, progress tracking, deadline reminders, certificate checklists, and portfolio evidence preparation — all as local artifacts for human review. Forbidden: impersonation, cheating, proctoring bypass, fabricating certificates, submitting assessments without explicit human work and approval, misrepresenting credentials.

## Python Automation Worker Lane Note

The python_automation_worker lane handles cheap, deterministic, stdlib-only automation: file parsing, JSONL processing, report generation, markdown/CSV generation, study trackers, queue processing, dashboard summaries. No external accounts, no scraping, no credential use, no live sends/posts/payments.

## Statement: Parallel Execution Gate

Controlled parallel execution is permitted only after this commit is pushed and Codex audit confirms the lane locks pass.
