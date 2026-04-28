# N+3.11 Codex Next Execution Review

Status: codex_parallel_audit / next_execution_review / no_runtime_changes / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## What Claude Code Should Do Next

Because the digest is known but Docker daemon access from this Codex shell is permission-blocked, Claude should first decide which truth applies in the shell it controls:

1. If Claude's shell can run `docker info` and see a real Server section, proceed to digest approval.
2. If Claude's shell also sees permission denied/no `docker-desktop` distro, stop and fix Docker Desktop user/session access first.

If Docker is usable in Claude's shell, the next safe milestone is:

```text
N+3.12 CUA screenshot-only smoke, only after digest approval and payload hash approval
```

Claude should:

- Use the platform-specific `linux/amd64` digest unless it proves another platform is correct.
- Ask the user to approve the exact digest.
- Create one screenshot-only ActionIntent.
- Compute and present the exact payload hash.
- Ask the user to approve the exact payload.
- Pull/run only the approved digest.
- Bind ports to localhost.
- Use no host mounts and no privileged mode.
- Capture only one approved observe/screenshot result.
- Write audit artifacts and stop/remove the container.

## What Codex Should Avoid

- Installing tools.
- Pulling Docker images.
- Running containers.
- Running CUA examples.
- Starting Screenpipe capture.
- Editing runtime/dashboard files in a parallel audit lane.
- Treating user-reported Docker readiness as equivalent to readiness in this shell.

## Is CUA Screenshot-Only Smoke Ready?

```text
conditionally_ready_for_Claude_if_Claude_shell_has_docker_info_server
not_ready_from_Codex_shell
```

Required gates still pending:

- Docker daemon access in the actual execution shell.
- Confirm WSL/docker-desktop distro state in the actual execution shell.
- Exact digest approval.
- Exact ActionIntent payload hash approval.

## Is Gemma/Ollama Local Brain Work Ready?

```text
ollama_installed_but_no_models
```

Gemma/Ollama local brain smoke is not ready until a model is pulled with explicit approval.

## Should Docker PATH Be Fixed?

Yes, but it is not a blocker if Claude always uses the explicit Docker path. A later cleanup milestone can add Docker to the user PATH or require new terminals after Docker Desktop install. Do not modify PATH in this Codex audit lane.

## App/Desktop Wrapper

Defer persistent app/desktop wrapper work until after one of these succeeds:

1. CUA screenshot-only smoke with audit artifacts.
2. Gemma/Ollama local brain smoke.
3. Dashboard route/operator visibility cleanup.

Do not start wrapper work while Docker/CUA truth is still split by shell/user context.

## Recommended Next Milestones

1. `N+3.12 CUA screenshot-only smoke` only after Docker daemon + WSL + digest approval + payload approval are all satisfied.
2. `N+3.12b Gemma/Ollama local brain smoke` after explicit model pull approval.
3. `N+3.13 persistent app/desktop wrapper or dashboard auto-launch service` after the core proof paths are less brittle.

## Runtime Wiring Truth

This Codex audit did not wire runtime, run Docker, pull images, run CUA, start capture, click/type, or use live accounts.
