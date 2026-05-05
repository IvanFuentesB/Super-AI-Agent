# Agent Lanes

Status: N+3.43 local scaffolding.

Agent lanes let Ghoti run multiple helpers later without letting them collide, overwrite shared memory, or turn local planning into live action. This folder is a coordination layer only: it defines branches, locks, status beacons, examples, and merge rules.

## Purpose

- Make parallel Claude, Codex, Gemma, ChatGPT, and future worker lanes safer.
- Keep every agent's write scope explicit before work starts.
- Prevent two active lanes from editing the same shared state file.
- Preserve auditability with append-only lock and status records.
- Keep local scaffolding separate from live account, money, public, browser, and scraping actions.

## Allowed Work

- Local repo docs, specs, audits, and implementation on the assigned branch.
- Local validation commands that do not mutate unrelated files.
- Append-only lane lock/status records.
- Local summaries, compression drafts, and deterministic Python helper work inside approved repo paths.
- Human-reviewed handoffs and merge checklists.

## Forbidden Work

- Uncontrolled parallel execution.
- External tool installation, cloning, or wiring.
- New MCP/connector/live-account connections.
- Account creation, email sending, social posting, product listing, payments, scraping, job applications, giveaway entries, or app-store actions.
- Fake accounts, fake engagement, spam, contest botting, credential fabrication, certificate fabrication, or impersonation.
- Model-output execution or auto-approval.
- Resetting, deleting, or overwriting history/memory files without explicit human approval.

## Core Rules

- Branch per agent: use a dedicated branch for each real parallel lane.
- One writer per shared file: no two active lanes may edit the same locked shared file.
- Lock before write: write scope and shared-file locks must be visible before work begins.
- Status beacons: each active lane should update status in a local, append-only way.
- Merge one branch at a time: do not merge multiple lanes without inspection and validation.
- State owner: only the designated state-owner lane edits `current_state.md`, `next_actions.md`, and finish-line logs during a milestone.

## How Lanes Cooperate

- ChatGPT strategy lane: strategy, prompts, architecture, and decisions. No repo writes unless the user explicitly asks for generated artifacts.
- Claude Code implementation lane: implementation, tests, docs tied to implementation, commits, and pushes. No live actions and no shared-file edits without a lock in parallel mode.
- Codex audit lane: audits, source checks, specs, planning docs, and verification. Runtime implementation only when explicitly requested.
- Gemma local worker lane: cheap local summaries, compression, scoring, and draft artifacts. Gemma output is never source of truth unless promoted by human review.
- Python automation worker lane: deterministic local parsing, validation, report generation, JSONL processing, and file organization inside approved repo folders.

## Future Safe Concepts

### Course/Certificate Assistant

Safe future support only:

- Find legitimate courses.
- Create study plans.
- Track progress.
- Summarize lessons.
- Quiz the user.
- Create notes.
- Remind deadlines.
- Prepare certificate checklists.
- Organize proof and portfolio artifacts.

Forbidden:

- Impersonating the user.
- Cheating exams.
- Bypassing proctoring.
- Fabricating certificates.
- Submitting assessments without explicit user work and approval.
- Misrepresenting credentials.

### Python Automation Worker

Safe future support:

- Use cheap local Python scripts for deterministic repetitive work.
- Parse JSONL.
- Generate markdown reports.
- Summarize dashboard data.
- Organize files inside approved repo folders.
- Maintain study trackers and local queue summaries.
- Run validation checks.

Forbidden:

- External accounts.
- Live emails, posts, payments, job applications, or public actions.
- Scraping without legal/TOS review.
- Credential use.
- Bypassing approval gates.

## Current N+3.43 Truth

This milestone creates scaffolding only. It does not start parallel agents. Controlled parallel execution can begin only after this commit is pushed and a Codex audit confirms the lane locks pass.
