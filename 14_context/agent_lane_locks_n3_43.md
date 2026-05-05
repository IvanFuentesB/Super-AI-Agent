# N+3.43 Agent Lane Locks And Parallel Execution Scaffolding

Status: implemented by Codex recovery lane.
Date: 2026-05-05
Branch: `feat/ghoti-visible-operator-stack`

## Scope

N+3.43 creates local scaffolding for controlled future parallel agents. It does not start parallel agents, connect external tools, install dependencies, create accounts, post, send, sell, pay, scrape, apply to jobs, enter giveaways, or touch live accounts.

## Files Created

- `14_context/agent_lanes/README.md`
- `14_context/agent_lanes/lane_template.md`
- `14_context/agent_lanes/lock_template.md`
- `14_context/agent_lanes/status_template.md`
- `14_context/agent_lanes/merge_checklist.md`
- `14_context/agent_lanes/shared_file_lock_policy.md`
- `14_context/agent_lanes/agent_lane_registry.json`
- `14_context/agent_lanes/active_locks.jsonl`
- `14_context/agent_lanes/lane_status.jsonl`
- `14_context/agent_lanes/examples/claude_code_impl_example_lock.md`
- `14_context/agent_lanes/examples/codex_audit_example_lock.md`
- `14_context/agent_lanes/examples/gemma_local_worker_example_lock.md`
- `14_context/agent_lanes/examples/python_automation_worker_example_lock.md`
- `03_scripts/agent_lane_status.py`

## Helper Script Usage

```powershell
python 03_scripts/agent_lane_status.py --help
python 03_scripts/agent_lane_status.py --check
python 03_scripts/agent_lane_status.py --list
```

Dry-run a new lock:

```powershell
python 03_scripts/agent_lane_status.py --new-lock --agent-id claude_code_n3_43 --lane-type claude_code_impl --task-slug agent-lane-scaffolding --branch feat/ghoti-visible-operator-stack --locked-file 14_context/current_state.md --locked-file 14_context/next_actions.md --dry-run
```

Append a lock only after operator-approved lane scope:

```powershell
python 03_scripts/agent_lane_status.py --new-lock --agent-id claude_code_next --lane-type claude_code_impl --task-slug small-safe-task --branch feat/ghoti-agent-claude-small-safe-task --locked-file 03_scripts/example.py --apply
```

Dry-run a status beacon:

```powershell
python 03_scripts/agent_lane_status.py --new-status --agent-id claude_code_n3_43 --lane-type claude_code_impl --task-slug agent-lane-scaffolding --branch feat/ghoti-visible-operator-stack --current-state dry_run --dry-run
```

## How To Start A Lane

1. Fetch origin.
2. Compare local HEAD to origin.
3. Choose a branch-per-agent branch name.
4. Create or dry-run a lock record.
5. Confirm no shared-file overlap.
6. Work only inside allowed paths.
7. Emit status beacons.
8. Validate.
9. Stage only intentional files.
10. Push the lane branch.
11. Merge one branch at a time.

## How To Check Lanes

Run:

```powershell
python 03_scripts/agent_lane_status.py --check
python 03_scripts/agent_lane_status.py --list
```

`--check` verifies required lane files, registry JSON, and lock/status JSONL. `--list` prints active locks and status records without mutating files.

## How To Merge Safely

Use `14_context/agent_lanes/merge_checklist.md`.

Key rule: shared state docs are owned by one state-owner lane per milestone. If a second lane needs the same file, stop and ask.

## Allowed After N+3.43

- Controlled lane planning.
- Dry-run lock/status records.
- Local-only status beacons.
- Branch-per-agent workflows.
- Codex audit/source/spec lanes.
- Claude implementation lanes with explicit path ownership.
- Gemma compression drafts.
- Python deterministic local helper lanes.

## Still Forbidden

- Uncontrolled parallel execution.
- External integrations.
- Live account use.
- Posting, sending, selling, payments, scraping, job applications, giveaway entries, app-store actions, or account creation.
- Fake engagement, fake accounts, spam, credential fabrication, or certificate fabrication.
- Model-output execution or autonomous public/money-facing actions.

## Controlled Parallel Pilot Note

Controlled parallel execution can begin only after this commit is pushed and Codex audit confirms the lane locks pass.

## Course/Certificate Future Lane Safety Note

Course support is limited to legitimate discovery, study plans, notes, quizzes, progress tracking, deadline reminders, certificate checklists, and portfolio evidence prep. It must not impersonate the user, cheat, bypass proctoring, fabricate certificates, submit assessments without user work/approval, or misrepresent credentials.

## Python Automation Worker Lane Note

Python automation is useful for cheap deterministic tasks: JSONL parsing, markdown/report generation, validation checks, file organization inside approved repo folders, study trackers, and dashboard summaries. It must not use external accounts, send emails, post, pay, scrape without legal/TOS review, use credentials, or bypass approvals.
