# Runtime MVP

Small execution-focused runtime sandbox for Super-AI-Agent.

## What This Is

This MVP is a file-backed Python runtime that can create tasks, hold approval-aware task state, generate a handoff snapshot from `14_context`, and expose lightweight council/workflow/report planning utilities.

## What It Proves

- tasks can be created locally
- risky tasks can require approval state
- task state can persist in JSON files
- durable handoff files can be turned into a runtime snapshot
- the runtime can be checked with a repeatable script
- provider, workflow, and report planning utilities can be exercised locally

## What It Does Not Do Yet

- no live provider integrations
- no browser or app control
- no real external execution
- no autonomous background loop
- no real Notion integration

## CLI Commands

- `init-data`
- `status`
- `enqueue`
- `list`
- `approve`
- `reject`
- `wait`
- `resume`
- `run-once`
- `list-providers`
- `council-plan`
- `list-workflows`
- `show-workflow`
- `scaffold-report`
- `snapshot`

## Runtime Data

Runtime artifacts are stored in `01_projects/runtime_mvp/runtime_data/`.

## Checker

Run:

```powershell
powershell.exe -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1
```
