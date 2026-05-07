# Agent Lane Locks — N+3.43

## Purpose

Agent lanes are the safety foundation for controlled parallel execution in the Ghoti operator system. Each lane is a named, bounded work scope assigned to one agent at a time. Lanes use lock files, status beacons, and a shared-file ownership policy to prevent agents from colliding on shared state, overwriting each other's work, or triggering unsafe live actions without human approval.

## Why Parallel Work Needs Locks

Multiple agents (Claude Code, Codex, Gemma, ChatGPT) may work concurrently on this repo. Without explicit lock assignments:
- Two agents can write to the same file in the same commit cycle → merge conflict or silent overwrite
- An audit agent and an implementation agent may both update current_state.md → conflicting truth
- A worker can start a follow-on action before a prior action is reviewed → unsafe chaining

Lanes solve this by requiring each agent to declare its scope, branch, and locked files before starting any parallel work.

## Allowed Work

- Local repo reads, writes, appends within declared allowed_paths
- Commits and pushes on the agent's assigned branch
- Generating local artifacts under 05_logs/, output/, or task-scoped dirs
- Updating JSONL state files the agent owns (e.g. active_locks.jsonl, lane_status.jsonl)
- Calling the local Gemma/Ollama brain for cheap local summaries (no external API)
- Appending to compact memory files when explicitly in the merge plan

## Forbidden Work

- Writing outside the repo root (C:\Users\ai_sandbox\Documents\AI_Managed_Only)
- Writing to any shared file listed in shared_file_lock_policy.md without owning the lock
- Running external API calls, web requests, or live account actions
- Installing packages, cloning repos, or connecting new MCP servers
- Deleting history, memory, task, or audit files
- Posting, selling, applying, emailing, scraping, or paying without explicit human approval
- Impersonating the user in courses, exams, or job applications
- Fabricating certificates or credentials
- Running uncontrolled parallel agents (more agents than declared lanes)

## Branch-Per-Agent Rule

Each parallel agent must work on its own branch:
- feat/ghoti-agent-<agent_id>-<task_slug>
- docs/ghoti-agent-<agent_id>-<task_slug>
- audit/ghoti-agent-<agent_id>-<task_slug>

No two agents may commit to the same branch simultaneously without explicit sequential handoff.

## One-Writer-Per-Shared-File Rule

Shared files (listed in shared_file_lock_policy.md) may only be written by the agent that holds the active lock for that file. All other agents must read-only until the lock is released and merged.

## Status Beacons

Each agent appends status records to lane_status.jsonl using the status_template.md format. The helper script 03_scripts/agent_lane_status.py provides --new-status for this. Use --list to inspect current statuses.

## Active Locks

Lock records are appended to active_locks.jsonl when an agent claims a shared file. Use --new-lock --apply to create. Use --list to inspect. Locks are not deleted — they are superseded by new status records showing released.

## Merge Checklist

Before merging any agent branch, follow merge_checklist.md. Key gates: validate lane files, check for shared-file conflicts, confirm human approval for any outbound or risky actions, run --check on lane files.

## Claude/Codex/Gemma/ChatGPT Cooperation

| Lane | Role |
|------|------|
| chatgpt_strategy | Strategy, architecture, prompts, handoff decisions — no repo writes unless user explicitly requests artifacts |
| claude_code_impl | Hard implementation, commits, validation — must use a lock branch when parallel mode is active |
| codex_audit | Audit, source-check, spec writing — no runtime implementation unless explicitly asked |
| gemma_local_worker | Cheap local summaries, compression, scoring — never source of truth without human promotion |
| python_automation_worker | Safe local Python for repetitive deterministic tasks (parsing, validation, report gen, dashboard summaries) |

## Future Lanes (planning_only — not active)

- future_course_certificate_assistant: Legitimate learning support ONLY — course discovery, study plans, notes, quizzes, progress tracking, deadline reminders, certificate checklist, portfolio evidence preparation. FORBIDDEN: impersonation, cheating, bypassing proctoring, fabricating certificates, submitting assessments without human approval/work, misrepresenting credentials.
- future_browser_operator: CUA/Chrome DevTools/Firecrawl/Glif only after explicit approval; no live accounts until approval; no scraping without legal/TOS check; no posting/sending/payment.
- future_orchestrator: OpenClaw/Paperclip/Ruflo/n8n only after separate integration approval; cannot bypass approval gates.

## Python Automation Worker Lane

The python_automation_worker lane is for cheap, deterministic, stdlib-only Python scripts that replace expensive model-token work: file parsing, JSONL processing, report generation, study trackers, dashboard summaries, validation checks, queue processing, CSV/markdown generation. Scripts must be repo-local, no external API, no credential use, no live sends/posts/payments.

## No Uncontrolled Parallel Execution

Controlled parallel execution is permitted only after this commit is pushed and a Codex audit confirms lane locks pass. Until then, all agent work remains sequential.

## No External/Live/Money/Account Actions

No lane may initiate external API calls, live account operations, payments, job applications, posting, scraping, emailing, or giveaway entries without explicit per-action human approval documented in the commit message and approval inbox.

## Future Backlog Note

Future milestones may add: course/study tracking artifacts, Python automation scripts for study progress and quiz generation, certificate evidence packaging. These must be local-only, human-reviewed outputs — no submission, impersonation, or credential fabrication permitted.
