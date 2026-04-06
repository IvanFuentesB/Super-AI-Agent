# Runtime MVP

Small local-first runtime sandbox for Super-AI-Agent.

## What This Is

This MVP is a file-backed Python runtime that can create tasks, hold approval-aware task state, and generate a handoff snapshot from `14_context`.

## What It Proves

- tasks can be created locally
- risky tasks can require approval state
- task state can persist in JSON files
- durable handoff files can be turned into a runtime snapshot
- the runtime can be checked with a repeatable script

## What It Does Not Do Yet

- no worker loop
- no wait or resume behavior
- no model routing
- no external integrations
- no background automation

## CLI Commands

- `init-data`
- `status`
- `enqueue`
- `list`
- `approve`
- `reject`
- `snapshot`

## Runtime Data

Runtime artifacts are stored in `01_projects/runtime_mvp/runtime_data/`.

## Checker

Run:

```powershell
powershell.exe -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1
```
