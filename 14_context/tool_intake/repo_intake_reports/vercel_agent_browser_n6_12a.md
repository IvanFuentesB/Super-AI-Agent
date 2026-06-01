# Vercel agent-browser - Static Intake Report (N+6.12A)

**Priority:** high (named computer-use stack candidate)
**Source:** `https://github.com/vercel-labs/agent-browser.git` (confidence: high)
**Local clone:** `21_repos/third_party_static/agent-browser` (git-ignored)
**Commit:** `b4f2f37d7b4f954022bc77f8d6dce70e07072b00` (shallow `--depth 1`)
**License:** **Apache-2.0** (reuse permitted; `NOTICE`/attribution required if code reused)
**Static-inspected:** yes | **safe_to_run:** false | **runtime_wired:** false

## What it is

A native (Rust) browser-automation CLI invoked as discrete commands, using Chrome
for Testing (pinned, downloaded) rather than the user's daily browser. The
`LICENSE` is Apache-2.0, "Copyright 2025 Vercel Inc."

## Static inspection findings

- `files_scanned`: 275; license family: **Apache-2.0** (`LICENSE`); package files
  include `package.json`, `pnpm-workspace.yaml`, and the Rust `cli/Cargo.toml` /
  `cli/Cargo.lock`.
- **Package lifecycle hook:** `postinstall` in the root `package.json`.
- **Shell scripts:** 9. **Docker files:** `docker/docker-compose.yml`,
  `docker/Dockerfile.build`. No standalone install scripts; no binaries committed.
- Network/API references appear in `cli/src/install.rs`, `cli/src/upgrade.rs`,
  `cli/src/chat.rs` (consistent with a CLI that downloads a Chrome build and talks
  to a model provider).

## Useful patterns

1. Native browser-automation CLI invoked as discrete, auditable commands.
2. Uses a pinned **Chrome for Testing** build rather than the user's daily browser -
   a cleaner isolation choice than driving the real profile.

## Risks

- **Global npm install of a native binary**; downloads a Chrome build on first run
  (the `postinstall` hook + `install.rs`/`upgrade.rs` are the relevant surfaces).
- Live browser automation; binary-distribution trust.

## Decision

Patterns documented; **no code copied**. Because nothing is reused, no `NOTICE`
file is required this milestone; if any Apache-2.0 code is ever reused, its
attribution and `NOTICE` must be preserved.

## First safe next test

Read the CLI command surface + `Cargo.toml` read-only. **No** global install, **no**
Chrome download, **no** run.
