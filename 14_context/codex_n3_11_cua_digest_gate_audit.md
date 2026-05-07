# N+3.11 Codex CUA Digest Gate Audit

Status: codex_parallel_audit / digest_gate_inspected / no_pull / no_run / no_build / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## CUA Repo Truth

| Field | Value |
| --- | --- |
| Repo path | `21_repos/third_party/evals/cua` |
| HEAD | `46dbcb47802e2c712c87e9a34d4d5b06829a2932` |
| Remote | `https://github.com/trycua/cua.git` |
| Git ownership note | Read-only inspection used `-c safe.directory=...`; no global config changed |
| Third-party files staged | NO |

## Image Tag Inspected

```text
trycua/cua-ubuntu:latest
```

Allowed inspection commands run:

```powershell
docker manifest inspect trycua/cua-ubuntu:latest
docker buildx imagetools inspect trycua/cua-ubuntu:latest
```

No `docker pull`, `docker run`, or `docker build` was run.

## Digest Results

`docker buildx imagetools inspect` reported the OCI image index digest:

```text
sha256:e2a800152d7d0a2a43b1f7f715f964ecb4a7501b262f3ca626f15a9e6b083e32
```

Platform manifests:

| Platform | Digest |
| --- | --- |
| `linux/amd64` | `sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a` |
| `linux/arm64` | `sha256:266524f436686423973a06de65dc5e5c4e656a7f6fb25b5161b2e5cbd004c34c` |
| attestation for amd64 | `sha256:0a9d4aab02b89b4760ee18c7b4adcd50ddec1dbb180bd976f885206dbf72e374` |
| attestation for arm64 | `sha256:2d647b7bef4362be5b10ebc2ef08f0ac418d7a67e3c1df237ae1968b6bda8a46` |

For this Windows/Docker Desktop host, the likely first target is `linux/amd64`, but Claude must confirm the actual Docker platform before approving a pull.

## Source Evidence

- `21_repos/third_party/evals/cua/blog/ubuntu-docker-support.md:55` documents `docker pull --platform=linux/amd64 trycua/cua-ubuntu:latest`.
- `21_repos/third_party/evals/cua/blog/ubuntu-docker-support.md:70` and `:132` reference `image="trycua/cua-ubuntu:latest"`.
- `21_repos/third_party/evals/cua/blog/ubuntu-docker-support.md:91` describes Ubuntu 22.04 + Xfce with web viewer at `http://localhost:8006`.
- `21_repos/third_party/evals/cua/blog/ubuntu-docker-support.md:97` says the container starts as non-root `kasm-user`, has isolated filesystem unless volumes are mounted, and uses KasmVNC.
- `21_repos/third_party/evals/cua/libs/kasm/Dockerfile:1` uses `kasmweb/core-ubuntu-jammy:1.17.0`.

## Mutable Tag Risk

`latest` is mutable. Approval must bind to a digest, not the tag. The digest can still change in future if `latest` is updated, so future smoke prompts should record the timestamp, exact digest, and platform.

## Required Approval Phrase

Before any pull/run:

```text
APPROVE CUA IMAGE DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a FOR SCREENSHOT-ONLY SMOKE
```

If Claude chooses to approve the multi-arch index instead, it must say so explicitly and still bind the platform. For the first smoke, prefer the platform-specific `linux/amd64` digest.

## What Must Stay Blocked Before Approval

- No image pull.
- No image build.
- No container run.
- No CUA execution.
- No click/type.
- No live accounts.
- No host mounts.
- No privileged container.
- No runtime adapter promotion.

## Verdict

```text
digest_gate_ready_for_human_approval
daemon_access_from_codex_shell_blocked
```

The digest gate is ready as a planning artifact because exact digests are known. The actual pull/run gate is not ready from this Codex shell because Docker daemon access is permission-blocked here.
