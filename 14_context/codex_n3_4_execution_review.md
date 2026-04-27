# Codex N+3.4 Execution Review

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: ad022a0
Status label: parallel_execution_review / no_runtime_changes / not_runtime_wired

## What Claude Code Should Implement

Claude Code should focus on one of these narrow next slices:

### Option A: CUA Source Evaluation

- Verify exact source as `trycua/cua`.
- Clone only if the operator explicitly approves.
- Inspect package/install scripts without running them.
- Map which package supports Windows sandbox use versus macOS Cua Driver use.
- Produce a source/license/security audit.
- Do not install, launch, or wire runtime.

### Option B: CUA Descriptor-Only Adapter

- Add a descriptor-only config/read model for CUA.
- Set `can_execute=false`.
- Set `sandbox_required=true`.
- Set `host_desktop_allowed=false`.
- Expose status honestly.
- Do not launch CUA.
- Do not screenshot/click/type.

### Option C: Screenpipe Read-Only Dashboard Route

- Add read-only local retention policy/status route.
- Do not install Screenpipe.
- Do not start capture.
- Do not start audio.
- Show default `retention_days=3`.
- Show `enabled=false`.

## What Codex Should Avoid

- Do not touch runtime Python files while Claude is implementing runtime work.
- Do not edit dashboard `server.js` in a parallel lane.
- Do not stage third-party repos.
- Do not stage Claude prompt files.
- Do not stage untracked clone audit docs unless explicitly assigned.
- Do not claim CUA, Screenpipe, RUFLO, AutoBrowser, or Obscura is wired unless route/runtime proof exists.

## What User Must Approve

- Any clone of `trycua/cua`.
- Any `pip install`, `npx`, shell installer, or package manager command.
- Any sandbox/VM launch.
- Any screenshot/capture start.
- Any CUA Driver/MCP server launch.
- Any click/type execution.
- Any cloud/provider account connection.
- Any Screenpipe install.
- Any deletion/cleanup execution.

## Recommended Next Milestone

Recommended: N+3.5 CUA screenshot-only sandbox smoke, but only after an explicit N+3.4 source-evaluation approval confirms the exact CUA repo, platform path, and install risk.

If the user wants lower risk first, choose Screenpipe dashboard route instead:

- no capture
- no install
- read-only policy/status route
- retention shown as 3 days
- local-only language

## Decision Matrix

| Candidate next step | Value | Risk | Recommendation |
|---|---:|---:|---|
| CUA source evaluation | High | Low | Best immediate step |
| CUA descriptor-only adapter | High | Low-medium | Good if source identity is already accepted |
| CUA screenshot-only sandbox smoke | Very high | Medium-high | Do only after source and sandbox approval |
| Screenpipe dashboard route | Medium | Low | Good stabilization/visibility step |
| Obsidian vault sync | Medium | Low | Good token-saving step, less urgent than CUA |
| Click/type CUA action | Very high | High | Defer |

## Risks To Watch

- Overclaiming "computer use" before any sandbox execution exists.
- Treating Cua Driver macOS docs as proof of Windows host support.
- Installing via shell command before source review.
- Letting background/no-foreground driver behavior hide actions from the user.
- Capturing screenshots of sensitive content.
- Storing screenshots or traces in git.
- Accidentally staging nested third-party repos.
- Letting an observe/screenshot action evolve into click/type without a new milestone.

## Runtime Wiring Truth

No runtime wiring was performed by this Codex lane.

Current recommended truth label:

`cua_source_identified_likely / sandbox_required / not_installed / not_runtime_wired`

## Final Recommendation

Proceed with CUA source evaluation first. Then choose either descriptor-only adapter or screenshot-only sandbox smoke depending on how clean the source/platform review is.
