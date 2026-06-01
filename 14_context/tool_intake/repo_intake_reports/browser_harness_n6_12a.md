# Browser Harness - Static Intake Report (N+6.12A)

**Priority:** high (named computer-use stack candidate)
**Source:** `https://github.com/browser-use/browser-harness.git` (confidence: high)
**Local clone:** `21_repos/third_party_static/browser-harness` (git-ignored)
**Commit:** `6d20866664ea3d9691b27bbf64f42ae097437dc3` (shallow `--depth 1`)
**License:** MIT (reuse permitted)
**Static-inspected:** yes | **safe_to_run:** false | **runtime_wired:** false

## What it is

A deliberately thin "connect an LLM directly to your real browser" harness: one
CDP websocket to Chrome, with the agent writing missing helper code during a task.
The README states the goal plainly ("You will never use the browser again") and
that "the agent writes what's missing during execution."

## Static inspection findings

- `files_scanned`: 150; license family: **MIT** (`LICENSE`); one package file
  (`pyproject.toml`).
- Top level includes `.env.example`, `install.md`, `src/`, `agent-workspace/`,
  `interaction-skills/`, `tests/`.
- **No** shell scripts, **no** binaries, **no** Dockerfiles, **no** package
  lifecycle hooks. The only install entrypoint is `install.md` (a doc).
- Browser/computer-control references and credential/auth references are present
  (the harness is about driving a real browser and reads `.env.example`-style keys).

## Useful patterns

1. Thin CDP websocket-to-Chrome harness (one socket, minimal layers).
2. Editable agent-workspace helpers the agent extends during a task.

## Risks

- **Direct live control of a real Chrome over CDP** once run.
- **Self-modifying:** the agent writes new helper code during execution. This must
  never be enabled inside Ghoti without strict approval gating.
- Autonomy framing ("you will never use the browser again") conflicts with Ghoti's
  supervised, approval-gated model.

## Decision

Patterns documented; **no code copied**. The self-writing-code behaviour is captured
as a disabled flag (`self_writing_code_enabled = False`) in the computer-use
contract and must stay off.

## First safe next test

Read `install.md` and the harness source read-only. **Do not** connect to Chrome,
**do not** run, **do not** let it self-write code.
