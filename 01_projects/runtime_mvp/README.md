# Runtime MVP

Small execution-focused runtime sandbox for Super-AI-Agent.

## What This Is

This MVP is a file-backed Python runtime that manages approval-aware lifecycle state, generates handoff snapshots from `14_context`, and exposes lightweight workflow, GitHub, personal-ops, showcase, and diagnostic utilities.

## What It Proves

- tasks can be created locally
- risky tasks can require approval state
- task state can persist in JSON files
- durable handoff files can be turned into a runtime snapshot
- the runtime can be checked with a repeatable script
- provider, workflow, report, truth-plan, publishability, personal-ops, GitHub draft/action, remote smoke-test, internship-pack, and showcase utilities can be exercised locally

## What It Does Not Do Yet

- no live provider integrations
- no browser or app executor
- GitHub live read-only adapter exists
- GitHub draft generation exists
- approval-gated branch, issue, and PR actions exist
- remote smoke-test issue and PR actions exist
- remote GitHub issue and PR creation depend on runtime-detected `gh` presence and auth
- in the intended environment, authenticated `gh` makes remote smoke actions possible with explicit approval
- environment hardening and capability detection exist
- no destructive GitHub actions
- no live mail adapter
- no live LinkedIn adapter
- internship and job-search personal-ops scaffolding exists
- showcase and portfolio page scaffolding exists
- `career-ops` is cloned as reference material only
- official Claude Code and OpenClaw are cloned as intake and reference material only
- browser executor research now exists
- no real external execution
- no real remote auth layer
- no autonomous background loop
- no live Notion writes
- browser and app execution are still not implemented
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
- `github-gh-diagnose`
- `github-remote-capability`
- `env-diagnose`
- `gh-auth-status`
- `capability-matrix`
- `github-issue-draft`
- `github-pr-draft`
- `github-create-branch`
- `github-create-issue`
- `github-create-pr`
- `github-smoke-issue`
- `github-smoke-pr`
- `mail-plan`
- `notion-plan`
- `list-personal-workflows`
- `show-personal-workflow`
- `scaffold-inbox-triage`
- `scaffold-linkedin-pack`
- `scaffold-cv-pack`
- `scaffold-outreach-draft`
- `scaffold-internship-pack`
- `scaffold-showcase-case-study`
- `scaffold-portfolio-project-page`
- `snapshot`

## Runtime Data

Runtime artifacts are stored in `01_projects/runtime_mvp/runtime_data/`.

## Checker

Run:

```powershell
powershell.exe -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1
```

The checker stays non-mutating by default, even when remote GitHub smoke actions are possible.
