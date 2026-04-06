# Runtime MVP

Small execution-focused runtime sandbox for Super-AI-Agent.

## What This Is

This MVP is a file-backed Python runtime that can manage approval-aware lifecycle state, generate handoff snapshots from `14_context`, and expose lightweight council, workflow, report, truth, publishability, personal-ops, and integration-adapter utilities.

## What It Proves

- tasks can be created locally
- risky tasks can require approval state
- task state can persist in JSON files
- durable handoff files can be turned into a runtime snapshot
- the runtime can be checked with a repeatable script
- provider, workflow, report, truth-plan, publishability, personal-ops, and integration-adapter utilities can be exercised locally

## What It Does Not Do Yet

- no live provider integrations
- no browser or app executor
- GitHub adapter is live read-only only
- no live mail adapter
- no live LinkedIn adapter
- no real external execution
- no real remote auth layer
- no autonomous background loop
- no live Notion writes
- future outbound actions should stay approval-gated

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
- `truth-plan`
- `publish-check`
- `publish-check-core`
- `list-integrations`
- `github-status`
- `mail-plan`
- `notion-plan`
- `list-personal-workflows`
- `show-personal-workflow`
- `scaffold-inbox-triage`
- `scaffold-linkedin-pack`
- `scaffold-cv-pack`
- `scaffold-outreach-draft`
- `snapshot`

## Runtime Data

Runtime artifacts are stored in `01_projects/runtime_mvp/runtime_data/`.

## Checker

Run:

```powershell
powershell.exe -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1
```
