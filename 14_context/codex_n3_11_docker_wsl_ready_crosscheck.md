# N+3.11 Codex Docker/WSL Ready Crosscheck

Status: codex_parallel_audit / docker_wsl_crosscheck / no_pull / no_run / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: b63cc52
Origin HEAD after fetch: 61d2d9c
Local vs origin: local ahead by 2 commits, origin ahead by 0

## Repo State

| Item | Truth |
| --- | --- |
| Branch | `feat/ghoti-visible-operator-stack` |
| Starting local HEAD | `b63cc52 docs/ghoti N+3.10 - record commit hash and push_pending status in finish line log` |
| Origin HEAD | `61d2d9c docs/analysis milestone N+3.10 - audit Docker post-launch and CUA smoke readiness` |
| Ahead/behind | ahead 2 / behind 0 |
| Staged files at start | none |
| Dirty files intentionally excluded | `14_context/ghoti_external_repo_tool_intake.md`, `21_repos/third_party/.gitkeep`, `.claude/skills/`, `01_projects/mcp_server/test.txt`, prompt scratch, CV docs, `output/` |

## Operator-Reported Truth vs Codex Shell Truth

The user reported Docker Desktop and WSL2 are working, with `docker-desktop` running and `docker info` showing a real Server section.

Codex crosschecked from this shell and found a mixed state: Docker Desktop processes exist and WSL reports default version 2, but Docker API access from this shell fails with permission denied and `wsl --list --verbose` does not show installed distributions.

This likely means Docker is closer than N+3.10, but the current Codex shell is not yet a reliable execution context for CUA smoke.

## Command Results

| Command | Result |
| --- | --- |
| `& $DockerCli --version` | PASS: Docker version 29.4.0, build 9d7ad9f |
| `& $DockerCompose version` | PASS: Docker Compose version v5.1.2 |
| `Get-Process 'Docker Desktop'` | PASS: multiple Docker Desktop processes visible |
| `wsl --status` | PASS-ish: default version 2; warning says WSL1 unsupported unless optional component enabled |
| `wsl --list --verbose` | FAIL: says no WSL distributions are installed |
| `& $DockerCli context ls` | PASS: only `default *`, endpoint `npipe:////./pipe/docker_engine`; no `desktop-linux` context shown here |
| `& $DockerCli info` | FAIL: client/plugins print, but Server fails with `permission denied while trying to connect to the docker API at npipe:////./pipe/docker_engine` |

## Docker Desktop Process Status

Docker Desktop is running from this shell's process view:

```text
Docker Desktop process rows observed, including process IDs 39312, 39852, 57560, 63028.
```

## WSL Status

`wsl --status` reports:

```text
Versión predeterminada: 2
WSL1 no es compatible con la configuración actual del equipo...
```

`wsl --list --verbose` reports:

```text
Windows Subsystem for Linux has no installed distributions.
```

This differs from the user-provided `docker-desktop Running 2` report and should be resolved before Codex or Claude treats this shell as smoke-ready.

## Docker Context / Daemon Status

`docker context ls` from explicit CLI path reports only:

```text
default *  npipe:////./pipe/docker_engine
```

`docker info` does not include a usable Server section from this shell. It fails with permission denied against the Docker named pipe.

## CPU / Memory

Codex could not verify Docker Server CPU/memory because `docker info` did not return a Server section from this shell.

User-provided truth says Docker Desktop has 16 CPUs and approximately 15.27 GiB memory. Treat that as operator-observed truth, not Codex-verified in this shell.

## Final Verdict

```text
exact_blocker: docker_desktop_running_but_current_shell_cannot_access_daemon
docker_wsl_ready_from_codex_shell: no
operator_reports_docker_wsl_ready: yes
```

CUA smoke should not run from this Codex shell until `docker info` returns a real Server section and `wsl --list --verbose` shows the expected `docker-desktop` distro in the same execution context that will run the smoke.
