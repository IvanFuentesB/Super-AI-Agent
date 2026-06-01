# TryCUA / CUA Driver - Static Intake Report (N+6.12A)

**Priority:** high (named computer-use stack candidate)
**Source:** `https://github.com/trycua/cua.git` (confidence: high)
**Local clone:** `21_repos/third_party_static/cua` (git-ignored)
**Commit:** `4c54f43ffd9a46cf9c96b06f477a986316d19260` (shallow `--depth 1`, partial Windows checkout)
**License:** MIT (reuse permitted)
**Static-inspected:** yes | **safe_to_run:** false | **runtime_wired:** false

## What it is

A large computer-use monorepo: a background "driver" (Rust/Swift) plus Python/TS
libraries, containerised desktop sandboxes (Docker / QEMU / KASM / Lumier), agent
libs, and benchmarks. `LICENSE.md` is MIT.

## Static inspection findings

- `files_scanned`: 2185; license family: **MIT** (`LICENSE.md` plus per-lib
  `libs/*/LICENSE`); 12 package files (`package.json`, `pyproject.toml`,
  `pnpm-lock.yaml`, ...).
- **Install scripts:** `libs/cua-driver/scripts/install.ps1`,
  `libs/cua-driver/scripts/install.sh`, `libs/lume/scripts/install.sh`,
  `libs/cua-bench/.../install.bat`, plus a `build.sh`.
- **Lifecycle hook:** `postinstall` in `docs/package.json` (plus `prepublishOnly`
  across `libs/typescript/*`).
- **Shell scripts:** 189. **Binaries:** 1. **Docker files:** root `Dockerfile`,
  `libs/cua-bench/Dockerfile`, an MCP-server `Dockerfile`, plus compose templates.
- Browser/computer-control, credential/auth, and network references are present
  (expected for a desktop-control driver + CI).

### Partial Windows checkout (recorded honestly)

The clone is a **partial Windows checkout**: some CI/workflow files with
invalid-on-Windows names did not materialize on disk. Key files (README, LICENSE,
`package.json`, `pyproject.toml`, `Dockerfile`) **are** present, so the static
inspection is sound; the gap is limited to a few CI YAMLs.

## Useful patterns

1. Observation -> plan -> action computer-use loop for desktop agents.
2. Containerised desktop sandbox (Docker / QEMU / KASM / Lumier) to isolate control.
3. Background **driver** separating capability from policy on macOS/Windows.

## Risks

- **Live desktop control (click/type)** once run.
- Docker/QEMU/KASM container runtime; very large monorepo; 189 shell scripts.
- Live model-provider APIs.

## Decision

Patterns documented; **no code copied**. The capability/policy-separation and
containerised-sandbox ideas inform the disabled `container_sandbox_enabled` and
`desktop_control_enabled` flags in the computer-use contract (both `false`).

## First safe next test

Read `README` + `pyproject.toml` + `Dockerfile` read-only to map the agent loop.
**No** Docker build/run, **no** driver start, **no** desktop control. Computer-use
stays disabled by default behind a feature flag and the global kill switch.
