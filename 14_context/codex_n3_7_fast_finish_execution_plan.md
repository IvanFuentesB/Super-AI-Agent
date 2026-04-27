# Codex N+3.7 Fast-Finish Execution Plan

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Status label: fast_finish_plan / no_runtime_changes / not_runtime_wired

## Goal

Finish the current operator/computer-use phase fast without creating unsafe autonomy or conflicting with Claude Code runtime work.

## Option A - Fastest Useful Progress Without Installs

Ranked sequence:

1. Screenpipe dashboard status route.
2. Obsidian vault sync route/doc updater.
3. Wait/resume dashboard UI card.
4. ActionIntent pending approval card.
5. Local-only artifact adapter.

Why:

- No Docker install.
- No CUA runtime.
- No capture start.
- Improves visibility and reduces babysitting immediately.
- Builds operator trust before full computer use.

## Option B - Fastest Real Computer-Use Path

Ranked sequence:

1. Docker Desktop install gate.
2. CUA Docker/Ubuntu smoke plan.
3. Screenshot-only CUA observe action.
4. ActionIntent approval for screenshot.
5. Audit trace + retention.
6. Only later click/type.

Why:

- Docker is the practical blocker for CUA local container path on this machine.
- CUA Docker/Ubuntu is the most concrete route toward real sandboxed computer use.
- Requires explicit operator approval and system-level install.

## Option C - Browser-First Path

Ranked sequence:

1. AutoBrowser Docker evaluation.
2. Obscura CDP Playwright smoke.
3. Local test page screenshot.
4. No live accounts.
5. No stealth.

Why:

- Browser-first has narrower blast radius than full CUA.
- Obscura already has a source build/CDP smoke recorded, but stealth/TOS risk means it must stay constrained.
- AutoBrowser likely still needs Docker, so Docker gate may also apply here.

## Recommended Next Claude Code Milestone

Recommended unless the user explicitly approves Docker Desktop install:

N+3.8 Screenpipe status route + Wait/Resume dashboard visibility.

Claude Code should edit:

- `01_projects/dashboard_mvp/server.js` for read-only routes only.
- dashboard public files only if adding a visible status card.
- docs/status files only if assigned.

Claude Code should not:

- start Screenpipe
- install Docker
- run CUA
- run capture
- add delete buttons
- claim computer-use is working

## Recommended Next Codex Milestone

N+3.8-CODEX audit of Docker Desktop install checklist and rollback plan.

Codex should audit:

- exact Docker Desktop install prerequisites
- WSL2 enablement steps
- disk/network risks
- rollback/uninstall/stop instructions
- safe first `docker --version`, `docker info`, and no-container validation

Codex should not:

- install Docker
- run containers
- edit runtime/dashboard implementation files during Claude runtime lane

## What User Must Approve

- Docker Desktop install.
- WSL2 install/enablement.
- Any reboot.
- Any Docker image pull/build/run.
- Any CUA container launch.
- Any screen/audio capture start.
- Any screenshot retention cleanup with deletion.
- Any click/type milestone.

## Exact Risks

- Docker introduces background services and disk/network usage.
- CUA can see/click/type; must remain screenshot-only first.
- Screenpipe can record sensitive information; must remain operator-start only.
- Obsidian vault can become bloated; must stay compact.
- Wait/resume visibility can overclaim readiness; status labels must stay honest.

## Exact Validation Commands For Next Claude Milestone

For Screenpipe route:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
curl http://127.0.0.1:3210/api/ghoti/screenpipe/status
git status --short
git diff --check
```

For wait/resume route/card:

```powershell
python 01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py
curl http://127.0.0.1:3210/api/ghoti/wait-resume/status
node --check 01_projects/dashboard_mvp/server.js
git status --short
```

For Docker gate audit only:

```powershell
docker --version
docker compose version
docker info
wsl --status
```

## What Done Looks Like

Done for no-install path:

- Screenpipe status route returns honest JSON.
- Dashboard shows read-only Screenpipe status.
- Wait/resume dashboard visibility reduces babysitting.
- Obsidian vault notes remain compact and referenced in handoffs.
- No capture started.
- No runtime artifacts staged.

Done for Docker path:

- Operator explicitly approves install.
- Docker and WSL install are verified.
- No CUA container run yet unless separately approved.
- Rollback/stop instructions are documented.

## Final Recommendation

Choose N+3.8 Screenpipe status route + Wait/Resume dashboard visibility unless the operator explicitly says:

`APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX`

If that exact approval is given, move to Docker Desktop install gate and verification before any CUA smoke.
