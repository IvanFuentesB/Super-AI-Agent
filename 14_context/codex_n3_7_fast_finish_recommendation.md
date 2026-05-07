# N+3.7 Codex Fast-Finish Recommendation

Status: recommendation / no_runtime_changes / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Observed local/origin HEAD: b902dca

## Path A: Docker/CUA Unlock

Best if the operator wants fastest progress toward real sandboxed computer-use capability.

Sequence:

1. Operator approves the exact phrase: `APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX`.
2. Install and verify Docker Desktop/WSL2.
3. Re-check CUA Docker/Ubuntu path.
4. Run no CUA action yet unless separately approved.
5. Next milestone defines/executes screenshot-only observe smoke.
6. Click/type remains blocked until a later milestone.

Pros:

- Unlocks the likely practical Windows path for CUA/TryCUA.
- Supports future screenshot-only sandbox proof.
- Moves toward real computer-use adapters.

Cons:

- Requires admin/system install.
- May require WSL2 and reboot.
- Adds background services, disk/network risk, and container-permission review.

## Path B: Screenpipe Route + Obsidian Sync

Best if the operator does not approve Docker yet or wants safe progress without installs.

Sequence:

1. Implement read-only `GET /api/ghoti/screenpipe/status`.
2. Add dashboard visibility for retention/capture-policy truth.
3. Add Obsidian vault sync/update workflow.
4. Surface Wait/Resume status if not already visible.
5. Keep capture start/delete/manual cleanup behind explicit approval.

Pros:

- No install required.
- Improves observability and reduces babysitting.
- Improves token/context efficiency immediately.
- Lower risk than CUA sandbox setup.

Cons:

- Does not unlock actual CUA execution.
- Does not prove computer-use actions.

## Recommendation

If the user approves Docker, choose Docker first because it unlocks the CUA sandbox path.

If the user does not approve Docker, choose Screenpipe status route + Obsidian vault sync first because it is no-install, lower-risk, and improves visibility/token savings immediately.

## Next Milestone Options

Recommended Claude Code milestone if no Docker approval:

```text
N+3.8 Screenpipe status route + Obsidian vault sync
```

Recommended Claude Code milestone if Docker approval is given:

```text
N+3.8 Docker Desktop install gate verification, no CUA run yet
```

Recommended Codex lane:

```text
N+3.8-CODEX Docker install checklist/rollback audit or Screenpipe route implementation review
```

## Runtime Wiring Truth

This audit adds no runtime wiring. It does not install Docker, start Screenpipe, run CUA, execute screen capture, click/type, browse, or connect external services.
