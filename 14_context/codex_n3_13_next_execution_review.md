# N+3.13 Codex Next Execution Review

Status: codex_parallel_audit / next_execution_review / no_runtime_changes / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## What Claude Code Should Do Next

Claude Code can move on three tracks, but should keep them separate:

1. Pull Gemma3:4B because the user approved it.
2. Pull the approved CUA image digest if Docker is ready in Claude's shell.
3. Implement the dashboard launcher only as a simple PowerShell launcher, not a service/app.

## CUA Approval State

Provided:

```text
APPROVE CUA IMAGE DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a FOR SCREENSHOT-ONLY SMOKE
```

Still needed before actual screenshot smoke run:

```text
APPROVE CUA SCREENSHOT-ONLY SMOKE WITH DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a AND PAYLOAD 69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4
```

Codex recommendation: Claude may pull the approved digest if Docker works in Claude's shell, but should not run the container until the payload-hash approval is present.

## Gemma Approval State

Provided:

```text
APPROVE OLLAMA PULL GEMMA3:4B FOR LOCAL BRAIN SMOKE
```

Claude may pull `gemma3:4b` and then run a tiny local smoke:

```powershell
ollama run gemma3:4b "Return exactly: GHOTI_LOCAL_BRAIN_OK"
```

Do not wire Gemma to CUA or autonomous actions yet.

## Should N+3.13 Execute CUA Smoke Now?

Not yet, unless Claude has the exact payload-hash approval phrase. The image digest approval is present, but the payload-hash execution approval is still a separate gate.

## Should N+3.13 Pull Gemma Now?

Yes in the main Claude lane, because the user explicitly approved the model pull. Codex did not pull because this lane is docs-only.

## Should N+3.13 Implement Dashboard Launcher Now?

Yes, if scoped to:

```text
03_scripts/run_dashboard.ps1
```

Do not implement Windows service, Electron/Tauri, Startup folder entry, or autostart without separate approval.

## How Close Ghoti Is To Reducing API Credit Reliance

| Area | Status |
| --- | --- |
| Docker/WSL | Ready per Claude/user docs; Codex shell still cannot access Docker daemon |
| CUA local operator path | First screenshot smoke pending |
| Gemma local brain | Model pull approved, not installed in Codex shell yet |
| Local dashboard persistence | Launcher pending |
| Fully autonomous local agent | Not yet; still needs approval loop, safe adapter, and local model routing |

Expected progression:

- After Gemma pull + smoke: local brain available for simple summaries/diagnostics.
- After CUA screenshot smoke: observe-only local computer-use path validated.
- After one safe adapter route: low-risk local repo/document tasks can start reducing API use.
- Claude/ChatGPT/Codex should still handle complex architecture until local brain quality is proven.

## What Codex Should Avoid

- Pulling models or Docker images in this lane.
- Running CUA.
- Starting Screenpipe.
- Editing runtime/dashboard files in parallel.
- Promoting descriptor-only adapters to executable.
- Treating digest approval as full execution approval.

## Recommended Next Claude Code Milestone

```text
N+3.13 main lane: Gemma3:4B pull + smoke, approved CUA digest pull, dashboard launcher script; defer CUA container run until payload-hash approval.
```

If the user provides the exact payload-hash approval, then:

```text
N+3.14 CUA screenshot-only smoke execution
```
