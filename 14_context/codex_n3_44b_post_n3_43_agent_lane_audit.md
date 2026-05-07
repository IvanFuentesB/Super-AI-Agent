# N+3.44b Post N+3.43 Agent Lane Audit

Status: Codex audit/spec only.
Date: 2026-05-05

## Repo Truth

- Branch: `feat/ghoti-visible-operator-stack`
- Audit starting HEAD: `98b6b8bae3d41218cade962b46c6ed143a337c3c`
- Current HEAD during audit: `98b6b8bae3d41218cade962b46c6ed143a337c3c`
- Origin HEAD during audit: `a1ade6b020a12cb7ff5ef6624ff436b42761afe2`
- Local/origin status: local was ahead of origin by 1 commit and not diverged.
- Expected implementation commit `a1ade6b020a12cb7ff5ef6624ff436b42761afe2`: pushed to origin and reachable from current HEAD.
- Additional local N+3.43 commit: `98b6b8b feat(ghoti): add N+3.43 agent lane locks`; this appears to be a same-milestone cleanup/normalization commit on top of `a1ade6b`.

No reset or destructive git action was used.

## Files Inspected

- `03_scripts/agent_lane_status.py`
- `14_context/agent_lane_locks_n3_43.md`
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
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `14_context/compact_memory/agent_routing_memory.md`
- `14_context/obsidian_vault/07_Agent_Routing.md`

## Validation Commands And Results

- `python -c "import ast, pathlib; ast.parse(pathlib.Path('03_scripts/agent_lane_status.py').read_text(encoding='utf-8')); print('AST OK agent_lane_status.py')"`: PASS
- `python 03_scripts/agent_lane_status.py --help`: PASS
- `python 03_scripts/agent_lane_status.py --check`: PASS; all required lane files present, registry JSON valid, JSONL files valid with 0 records.
- `python 03_scripts/agent_lane_status.py --list`: PASS; empty locks/status handled safely.
- `python 03_scripts/agent_lane_status.py --new-lock ... --dry-run`: PASS; printed JSON lock record and did not write.
- `python 03_scripts/agent_lane_status.py --new-status ... --dry-run`: PASS; printed JSON status record and did not write.
- JSON/JSONL validation snippet: PASS for `agent_lane_registry.json`, `active_locks.jsonl`, and `lane_status.jsonl`.
- `git diff --check`: PASS with only an LF-to-CRLF warning for unrelated dirty `14_context/ghoti_external_repo_tool_intake.md`.

## Required File Checklist

- `14_context/agent_lanes/README.md`: present
- `14_context/agent_lanes/lane_template.md`: present
- `14_context/agent_lanes/lock_template.md`: present
- `14_context/agent_lanes/status_template.md`: present
- `14_context/agent_lanes/merge_checklist.md`: present
- `14_context/agent_lanes/shared_file_lock_policy.md`: present
- `14_context/agent_lanes/agent_lane_registry.json`: present and valid JSON
- `14_context/agent_lanes/active_locks.jsonl`: present, valid empty append-only JSONL
- `14_context/agent_lanes/lane_status.jsonl`: present, valid empty append-only JSONL
- example lock files for Claude, Codex, Gemma, and Python worker: present
- `03_scripts/agent_lane_status.py`: present
- `14_context/agent_lane_locks_n3_43.md`: present

Checklist verdict: PASS.

## Helper Script Safety Review

`03_scripts/agent_lane_status.py` uses Python stdlib imports only: `argparse`, `datetime`, `hashlib`, `json`, `pathlib`, and `sys`.

Safety properties verified:

- No network libraries.
- No subprocess execution.
- No model calls.
- No package installation.
- No git mutation.
- No delete/unlink/rmdir calls.
- `--check` and `--list` are read-only.
- `--new-lock` and `--new-status` print dry-run records unless `--apply` is passed.
- `--apply` appends one JSONL line to the appropriate lane file.
- Locked file paths are validated to stay inside the repo root.

Non-blocking caveats:

- `allowed_paths` and `forbidden_paths` are recorded but not validated as strictly as `locked_files`.
- There is no dedicated `--release-lock`; release is represented by appending a status record such as `released`.
- Status records are intentionally compact and do not enforce all fields from `status_template.md`.

These caveats do not block a tiny controlled pilot, but future hardening should validate all path-list fields and add clearer release semantics.

## Lock/Status JSONL Review

- `active_locks.jsonl`: valid, empty, append-only by design.
- `lane_status.jsonl`: valid, empty, append-only by design.
- Dry-run lock generation produced a record with `lock_id`, `agent_id`, `lane_type`, `branch`, `task_slug`, `locked_files`, `allowed_paths`, `forbidden_paths`, `expected_outputs`, `notes`, and `timestamp_utc`.
- Dry-run status generation produced a record with `status_id`, `agent_id`, `lane_type`, `branch`, `task_slug`, `current_state`, `notes`, and `timestamp_utc`.

Verdict: sufficient for the first pilot when paired with human review and the merge checklist.

## Registry Review

The registry defines all required lanes:

- `chatgpt_strategy`
- `claude_code_impl`
- `codex_audit`
- `gemma_local_worker`
- `python_automation_worker`
- `future_course_certificate_assistant`
- `future_browser_operator`
- `future_orchestrator`

Each lane includes allowed work, forbidden work, approval gates, branch prefix, and default paths. Future lanes are marked planning-only where appropriate.

## Shared File Lock Review

`shared_file_lock_policy.md` protects:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- compact memory files
- Obsidian vault current/index/next-actions/dirty-state/handoff notes
- agent lane meta files
- implementation scripts

The policy states that during declared parallel execution, locks are required before writing shared files, and disputes stop for human resolution.

One caveat: the listed dashboard runtime paths use `01_projects/runtime_mvp/src/super_ai_agent/server.js` and `app.js`, while the current dashboard project commonly uses `01_projects/dashboard_mvp/server.js` and `01_projects/dashboard_mvp/public/app.js`. The N+3.45 pilot plan should explicitly lock the real dashboard paths.

## Course/Certificate Assistant Safety Review

The future course/certificate lane is bounded to legitimate learning support:

- course discovery
- study plans
- notes
- quizzes
- progress tracking
- deadline reminders
- certificate checklists
- portfolio evidence prep

Forbidden actions are explicit:

- impersonation
- cheating
- proctoring bypass
- fake certificates
- submitting assessments without human work/approval
- misrepresenting credentials

Verdict: safe as planning-only and not active.

## Python Automation Worker Safety Review

The Python automation lane is bounded to deterministic local tasks:

- file parsing
- JSONL processing
- validation checks
- report generation
- markdown/CSV generation
- study trackers
- dashboard summaries
- queue processing

Forbidden actions are explicit:

- external account access
- web scraping
- credential use
- live sends/posts/payments
- job applications
- installing packages
- cloning repos
- connecting external APIs or MCP servers

Verdict: safe for local deterministic work when path ownership is locked.

## Dirty Files Left Unstaged

Recurring unrelated dirty files were observed and intentionally left unstaged:

- `14_context/ghoti_external_repo_tool_intake.md`
- `21_repos/third_party/.gitkeep`
- `.claude/skills/`
- `01_projects/mcp_server/test.txt`
- `03_scripts/test_perm.tmp`
- `05_logs/local_brain_runs/`
- `05_logs/money_reviews/`
- `05_logs/money_runs/`
- `14_context/ghoti_current_prompt_N1_6.md`
- CV `.docx` files
- `output/`

## PASS/FAIL Verdict

PASS.

N+3.43 lane locks are sufficient to allow a tiny, explicitly scoped controlled parallel pilot after this audit is committed and pushed.

## Fixes If FAIL

No blocking fixes are required before the first pilot.

Recommended hardening after the pilot:

- validate `allowed_paths` and `forbidden_paths` in the helper
- add a release-lock helper action or release-status convenience command
- add dashboard project paths to shared-file lock policy
- optionally expand status records with validation status and latest commit fields
