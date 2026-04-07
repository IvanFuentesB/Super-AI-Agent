# Supervisor Foundation

## Purpose

The supervisor is the local control layer that keeps work understandable over time instead of trying to rush every task through one immediate run.

## What The Supervisor Is Responsible For

- track task state for longer-running local work
- know when a task is queued, running, waiting, blocked, or complete
- stop on risky or uncertain actions instead of guessing
- surface human-needed moments clearly in the dashboard
- make pause and resume explicit instead of hidden

## Why Patience Matters

A useful operator system has to wait well. It should be able to pause for approval, pause for a human reply, and resume later without losing the task state or pretending the work is done.

## Pause And Resume Model

- `queued`: ready to continue
- `running`: actively being worked
- `waiting`: paused for a human reply or another external event
- `pending_approval`: paused until the human approves or denies a risky step
- `blocked_human_needed`: paused because the operator must make a judgment call or perform a missing step
- `completed`, `rejected`, `failed`: terminal outcomes

## Approval Boundary

Remote writes, uncertain terminal actions, and anything admin-like must stop for explicit human approval. This foundation treats those cases as visible state, not as hidden background behavior.

## What This Batch Adds

- a clearer supervisor state model
- structured approval requests with risk and status
- a local-only notification abstraction
- dashboard visibility for pending approvals and human-needed tasks

## What This Batch Does Not Add

- no external notification channel
- no hidden always-on daemon
- no autonomous admin execution
- no desktop or app executor
