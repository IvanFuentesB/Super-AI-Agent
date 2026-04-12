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

## Brain / Provider Truth

Ghoti now exposes the current brain/provider state directly in both dashboard and CLI.

- Default local brain target: `gemma_local`
- Default model target: `gemma3:4b`
- Live local call path when ready: `cli -> super_ai_agent.brain -> Ollama /api/generate`
- Honest current truth: Ghoti's operator stack is still mostly rules, approvals, queue logic, and recipes unless a task explicitly uses model inference

Use these commands to inspect the real state:

```powershell
python -m super_ai_agent.cli brain-status
python -m super_ai_agent.cli ghoti-status
```

The dashboard `Brain / Provider Truth` card and the CLI `brain-status` output show:

- active brain provider
- active model name
- whether inference is actually ready
- whether the current task used model inference
- last model-call status and error

If Ollama is installed but the configured Gemma model is not pulled yet, Ghoti should report that clearly instead of pretending Gemma is live.

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
- floating Ghoti overlay with the live state, watchdog summary, and current target reminder
- visible target marker for the current handoff, focus, pointer, or input destination
- current desktop action truth for aiming, clicking, typing, waiting, or blocked work when a desktop task is active
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
- `ghoti-status`: current local state, current task, watchdog summary, overlay target, recent actionable work, and recent failures
- `ghoti-hotkeys`: the emergency stop path, overlay reminder, and what happens after interruption
- `ghoti-recent`: recent actionable tasks, active-only work, failures, pending approvals, recent artifacts, and the current watchdog summary

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
- the floating overlay and target marker for the current state and next local destination
- the `Operator Watchdog` card for wrong-window blocks, stalled work, and did-not-complete summaries
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

## Visible Desktop Actions

Ghoti now exposes a small visible supervised desktop-action layer instead of hiding those steps in logs.

- `move_mouse` can aim at coordinates or a named allowlisted target and show a visible target marker first
- `left_click` uses the same visible target cue before clicking
- `wait_seconds` shows that Ghoti is intentionally waiting rather than stuck
- `type_text` is now available only for explicit allowlisted targets and only for narrow one-line text

Both dashboard and CLI expose desktop action truth:

- current desktop action
- current target
- whether typing is enabled for that action
- last desktop action status
- cue visibility status

Typing is still intentionally narrow:

- no freeform typing into arbitrary contexts
- no auto-Enter or submit by default
- no bypass of approval, workspace, or handoff safety rules

## Operator Watchdog

Ghoti now surfaces a small watchdog summary instead of silently leaving the operator to infer trouble from raw task history. The watchdog is intentionally narrow and local:

- it shows `idle`, `active`, `waiting`, `approval_needed`, `interrupted`, or `blocked`
- it highlights wrong-active-window handoff blocks before any input is sent
- it surfaces stalled or did-not-complete work so the operator can decide what to inspect next
- it shows the current visible target reminder for focus, handoff, pointer, and input-oriented actions
- it can hint when a clean human handoff is likely needed because the current state is blocked or overloaded

This is not a daemon or autonomous recovery loop. It is an operator-facing visibility layer that keeps the current supervised model intact.

## Handoff Safety Reminder

Codex-to-ChatGPT handoff is paste-only by default. It must:

- resolve an explicit Codex source and ChatGPT destination
- re-verify the intended active destination immediately before paste
- block if the wrong window stays foreground
- never use terminal or PowerShell as a substitute destination

Explicit terminal-targeted actions are still allowed elsewhere when the operator intentionally targets a terminal.
