# N+3.9 Codex CUA Image Source Review

Status: codex_source_review / inspect_only / no_build / no_container_run / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack

## Source Repo Truth

Path inspected:

```text
21_repos/third_party/evals/cua
```

Plain `git -C` initially hit Git's dubious ownership guard because the clone is owned by a different Windows user. Codex used a one-command `-c safe.directory=...` override for read-only inspection only and did not change global Git config.

| Field | Value |
| --- | --- |
| Repo exists | YES |
| Git HEAD | `46dbcb47802e2c712c87e9a34d4d5b06829a2932` |
| Remote URL | `https://github.com/trycua/cua.git` |
| Runtime wired | NO |
| Dependencies installed by Codex | NO |
| Containers run by Codex | NO |

## Key Docker/Kasm Paths Found

| Path | Finding |
| --- | --- |
| `README.md` | Describes Cua Sandbox, local/cloud sandboxes, and screenshot/click/type examples. |
| `Dockerfile` | Python 3.12 slim workspace image; uses build script and local source copy. |
| `libs/kasm/README.md` | Identifies Kasm-based Ubuntu desktop container for computer-using agents. |
| `libs/kasm/Dockerfile` | Uses `kasmweb/core-ubuntu-jammy:1.17.0`, installs Python 3.12, Firefox, Playwright, `cua-computer-server`, and `cua-agent[all]`. |
| `libs/qemu-docker/linux/README.md` | Ubuntu 22.04 virtual desktop container with QEMU/KVM. |
| `examples/sandboxes/test_linux_local_container.py` | Shows `Sandbox.ephemeral(Image.linux("ubuntu", "24.04"), local=True)` and `sb.screenshot()`. |

## Prebuilt Image vs Local Build

The local Kasm Dockerfile references a prebuilt base image:

```text
kasmweb/core-ubuntu-jammy:1.17.0
```

However, the reviewed local files do not establish a single approved CUA image/tag for Ghoti's first smoke. The next smoke should therefore pause before any `docker pull`, `docker build`, or `docker run` and ask the operator to approve the exact image/tag or build path.

## Practicality For Next Smoke

The CUA source supports a local Linux container screenshot path conceptually:

- Local container example exists.
- Kasm Ubuntu desktop Dockerfile exists.
- Screenshot API example exists.
- The repo's Python workspace expects Python 3.12+ and includes external LLM dependencies for agent use.

But the smoke is not practical yet because this machine still lacks a running Docker daemon and installed/usable WSL.

## Risks

- Image pull/build supply-chain risk.
- Large image/disk usage.
- Network access from container unless constrained.
- Kasm browser/desktop exposes ports that must bind to localhost only.
- CUA examples include click/type abilities; Ghoti must permit screenshot/observe only for first smoke.
- CUA agent operation may involve OpenAI/Anthropic keys; first smoke must avoid provider keys and agent autonomy.
- QEMU/KVM path may require host capabilities not suitable for first Windows smoke.

## Recommendation

Do not run CUA yet.

Next source step after daemon/WSL verification:

1. Re-read `libs/kasm/README.md`, `libs/kasm/Dockerfile`, and the official CUA docs for the exact current Kasm image/build command.
2. Ask the operator to approve the exact image/tag or build path.
3. Use Kasm/local container only for screenshot/observe first.
4. Keep click/type disabled until a later milestone.

## Verdict

CUA source remains a good candidate for sandboxed screenshot-only smoke, but the image/source choice still needs explicit approval and the Docker daemon/WSL gates are not ready.
