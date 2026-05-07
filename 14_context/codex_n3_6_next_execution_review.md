# Codex N+3.6 Next Execution Review

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 2e9ffec
Status label: codex_review / next_execution_options / not_runtime_wired

## Option A: N+3.7 Docker Desktop Install Gate

Pros:

- Unlocks CUA Docker/Ubuntu local container path.
- Also helps future AutoBrowser Docker path.
- Provides a practical path on Windows Home where Windows Sandbox is blocked.
- Enables screenshot-only CUA smoke later.

Cons:

- Admin/system install.
- WSL2/backend complexity.
- Background Docker services.
- Image pulls and disk usage.
- Network access.
- Potential container permission mistakes.

Use if:

- The operator wants fastest progress toward real computer-use capability.
- The operator explicitly approves Docker Desktop install.
- The next milestone validates Docker/WSL first before any CUA container run.

Required approval phrase:

`APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX`

## Option B: N+3.7 Screenpipe Dashboard Route

Pros:

- Lower risk than Docker install.
- Useful immediately for visibility.
- Can remain read-only/status-only.
- Reinforces local-only capture and retention truth.
- Does not require starting capture.

Cons:

- Does not unlock actual CUA execution.
- Still needs careful wording to avoid implying recording is active.

Use if:

- The operator wants safer progress while avoiding installs.
- The next milestone can add a read-only route/status panel without starting capture.

## Option C: N+3.7 Obsidian Vault Sync / Token-Saving Prompt System

Pros:

- Reduces repeated context cost.
- Improves continuity across ChatGPT, Claude, and Codex.
- Low risk.
- No install needed.
- Helps every future milestone.

Cons:

- Does not unlock autonomous execution.
- Requires discipline to keep notes compact.

Use if:

- The project is starting to lose time from context sprawl.
- The operator wants better continuity before deeper runtime work.

## Option D: N+3.7 CUA Descriptor / Read-Model Polish

Pros:

- Safe architecture progress.
- No external install.
- Keeps CUA visibility honest.
- Can prepare dashboard/operator status for later Docker/Ubuntu path.

Cons:

- Still no real execution.
- May feel incremental unless paired with clear Docker gate.

Use if:

- Docker install is not approved yet.
- The operator still wants CUA-specific progress.

## Recommendation

If the operator wants speed toward autonomous computer use:

1. N+3.7 Docker Desktop install gate.
2. Verify Docker/WSL.
3. Only then plan CUA screenshot-only sandbox smoke.

If the operator wants safer progress while avoiding installs:

1. N+3.7 Screenpipe dashboard route.
2. N+3.8 Obsidian vault sync/update script.
3. Revisit Docker/CUA after install approval.

CUA screenshot-only smoke should come after Docker is installed and verified. It should not be attempted on the current machine state.

## Risks To Watch

- Installing Docker without explicit approval.
- Pulling large images without disk/network approval.
- Exposing container ports broadly instead of localhost-only.
- Mounting the repo or user home into containers by default.
- Starting Screenpipe capture while reviewing retention.
- Letting vault notes grow into another giant log.
- Claiming CUA is ready before Docker/WSL and sandbox path are proven.

## Runtime Wiring Truth

This Codex lane made no runtime changes, no dashboard changes, no script changes, no config changes, no third-party changes, and no capture/execution calls.
