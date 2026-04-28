# N+3.13 Codex Docker/WSL/CUA Ready Audit

Status: codex_parallel_audit / docs_only / no_runtime_changes / no_docker_execution

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 697e7cd
Origin HEAD after fetch: 7af7321
Local vs origin: local ahead by 4 commits, origin ahead by 0

## Repo Truth

| Item | Truth |
| --- | --- |
| Branch | `feat/ghoti-visible-operator-stack` |
| Starting local HEAD | `697e7cd docs/ghoti N+3.12 - record commit hash 585bb10 and push_pending status in finish line log` |
| Origin HEAD after fetch | `7af7321 docs/analysis milestone N+3.11 - audit Docker WSL CUA digest and local brain truth` |
| Ahead/behind | ahead 4 / behind 0 |
| Staged files at start | none |
| Dirty files excluded | `14_context/ghoti_external_repo_tool_intake.md`, `21_repos/third_party/.gitkeep`, `.claude/skills/`, `01_projects/mcp_server/test.txt`, prompt scratch, CV docs, `output/` |

## Docker/WSL Crosscheck Results From Codex Shell

| Check | Result |
| --- | --- |
| Docker CLI path exists | YES |
| Docker CLI version | `Docker version 29.4.0, build 9d7ad9f` |
| Docker Compose version | `Docker Compose version v5.1.2` |
| Docker Desktop process running | YES, multiple `Docker Desktop` processes visible |
| `wsl --status` | Default version 2; WSL1 warning in Spanish |
| `wsl --list --verbose` | FAIL from this shell: reports no installed WSL distributions |
| Docker context | `default *`, endpoint `npipe:////./pipe/docker_engine`; no `desktop-linux` context shown from this shell |
| `docker info` Server section | NO from this shell; fails with `permission denied while trying to connect to the docker API at npipe:////./pipe/docker_engine` |
| CPU/memory from Server section | Not available from Codex shell because Server section failed |

## Claude/User-Reported Readiness

The user reports a healthier Docker context than Codex sees:

- Docker Desktop process running.
- `wsl --status` shows default distribution `docker-desktop`, default version `2`.
- `wsl --list --verbose` shows `docker-desktop Running 2`.
- Explicit Docker CLI path works.
- `docker info` shows a real `Server:` section.
- Docker Server Version `29.4.0`.
- Docker context `desktop-linux`.
- Docker Desktop has 16 CPUs and about 15.27 GiB memory.

N+3.12 docs also record a GO state from Claude's lane, with Docker Desktop running, `desktop-linux` active, WSL2 installed, and Docker server info available.

## Reconciliation

Codex shell truth and Claude/user truth differ. This likely reflects user/session/context permissions rather than CUA source readiness.

Claude Code may proceed only from a shell where these commands succeed in the same execution context that will pull/run:

```powershell
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' context ls
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' info
wsl --list --verbose
```

Required successful signs:

- Active Docker context is `desktop-linux`.
- `docker info` includes a real `Server:` section.
- `wsl --list --verbose` shows `docker-desktop Running 2`.

## GO / NO-GO Verdict

| Perspective | Verdict |
| --- | --- |
| Codex shell | NO-GO for execution: Docker daemon access is permission-blocked here. |
| Claude/user reported shell | CONDITIONAL GO for digest/pull gate if `docker info` still works there. |
| CUA smoke execution | Not GO until digest approval and payload-hash approval are both present. |

## Safety Boundary

Codex did not install, pull, build, run, start capture, execute CUA, click/type, or use live accounts.
