# Ghoti Control Center

## Purpose

Ghoti is a supervised local-first operator / builder / guide. The control center is the shortest honest way to see what Ghoti can do now, what needs approval, what is blocked, what just failed, and what the operator should do next.

This control surface stays inside the existing safety model:

- no task deletion without explicit user approval
- prefer archive, filter, and history visibility instead of deletion
- Ctrl+8 is the emergency stop for the current desktop action or operator recipe
- Codex-to-ChatGPT handoff must not fall back to terminal or PowerShell targets
- if the intended handoff source or destination cannot be resolved confidently, Ghoti blocks before any paste
- no unrestricted desktop control
- no admin automation
- no arbitrary shell passthrough

The operator core stays separate from the model / provider brain so future model swaps and later OpenClaw-style channel or control-surface integration do not require a rewrite of the local operator stack.

## Launch Ghoti

### Dashboard mode

From the repo root:

```powershell
node .\01_projects\dashboard_mvp\server.js
```

Then open:

```text
http://127.0.0.1:3210
```

The top-level Ghoti Control Center shows:

- current Ghoti state and reason
- Ctrl+8 emergency stop reminder
- current running task if one exists
- pending approvals
- blocked tasks
- recent actionable tasks
- recent failures
- what Ghoti can do now
- what the operator should do next

### CLI mode

From the repo root:

```powershell
python -m super_ai_agent.cli ghoti-help
python -m super_ai_agent.cli ghoti-status
python -m super_ai_agent.cli ghoti-hotkeys
python -m super_ai_agent.cli ghoti-recent
```

Use them like this:

- `ghoti-help`: quick launch, stop, safety, and next-step overview
- `ghoti-status`: current local state, current task, counts, recent actionable work, and recent failures
- `ghoti-hotkeys`: the emergency stop path and what happens after interruption
- `ghoti-recent`: recent actionable tasks, active-only work, failures, pending approvals, and recent artifacts

## Stop Ghoti Safely

Use:

```text
Ctrl+8
```

Ctrl+8 stops the current desktop action or operator recipe run. After interruption:

- the task is marked `interrupted`
- the interruption reason is kept in task history
- the operator must review the task before any re-queue

Ctrl+8 is not a delete path and does not bypass approvals or workspace boundaries.

## Inspect Tasks

### Dashboard

Use the Ghoti Control Center first:

- `Refresh Ghoti State`
- `Show Pending Approvals`
- `Show Active / Recent Tasks`
- task filters for recent-only, active-only, type, and status
- `Recent Actionable Tasks`
- `Recent Failures`

You can also use the fuller task panels lower in the dashboard when you need task detail, review, resume, re-queue, or execute actions.

### CLI

Use:

```powershell
python -m super_ai_agent.cli ghoti-status
python -m super_ai_agent.cli ghoti-recent
python -m super_ai_agent.cli list-executor-tasks
python -m super_ai_agent.cli supervisor-status
```

## Inspect Approvals

### Dashboard

Use `Show Pending Approvals` from the Ghoti Control Center, then inspect the approval item and choose the next operator step deliberately.

### CLI

Use:

```powershell
python -m super_ai_agent.cli pending-approvals
python -m super_ai_agent.cli approval-status
python -m super_ai_agent.cli approval-status --approval-id <approval-id>
```

## Inspect Recent Artifacts

### Dashboard

Use `Show Recent Artifacts`, then preview, open, or reveal the artifact from the artifact panel.

### CLI

Use:

```powershell
python -m super_ai_agent.cli ghoti-recent
```

That command includes the most recent artifact paths and timestamps.

## Common Quick Actions

The dashboard control center keeps a narrow practical set of operator actions:

- refresh Ghoti state
- show pending approvals
- show active / recent tasks
- show recent artifacts
- queue desktop observation
- queue clipboard read
- queue clipboard write
- queue focus window
- queue handoff
- run runtime checker
- run dashboard checker

These actions keep the existing approval-aware and workspace-boundary model intact. They do not add free-roaming autonomy.

## Handoff Safety Reminder

Codex-to-ChatGPT handoff is paste-only by default. It must:

- resolve an explicit Codex source and ChatGPT destination
- re-verify the intended active destination immediately before paste
- block if the wrong window stays foreground
- never use terminal or PowerShell as a substitute destination

Explicit terminal-targeted actions are still allowed elsewhere when the operator intentionally targets a terminal.
