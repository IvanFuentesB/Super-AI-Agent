# Agent OS - Runner Base Ready

Machine/human signal that main is the clean base for the sandboxed local
agent runner. Generated after PR #18 (approved execution substrate) landed.

## Current main

- `origin/main` = `f23a8f9d96006dd5fce5e58a667c1a683cc5d4dc`
  (merge commit of PR #18; previous main was `19450a1` = PR #17).
- Main now contains the **integrated Agent OS MVP (PR #17)** plus the
  **approved execution substrate (PR #18)**: one dashboard, one memory/search,
  one workflow launchpad, one handoff path, one approval queue, two role-distinct
  Rust guards (`ghoti_policy_checker` = ownership/recipe, `agent_os_guard` =
  approved-action). No duplicate `context_memory/`, `agent_command_center/`, or
  `14_context/memory/` exist in main.

## Rule for the next branch

- The next branch MUST be created from this new main (`f23a8f9`).
- Expected clean branch name:
  `feat/ghoti-agent-os-sandboxed-local-agent-runner-clean`.

## Codex runner porting instruction

- The existing runner branch
  `feat/ghoti-agent-codex-sandboxed-local-agent-runner`
  (tip `94749a200835bf02a676a988c3508c177419e172`) was built on the OLD substrate
  chain `96c8d627`, which still carries the duplicate memory/command-center
  systems. **Do not merge it as-is.**
- From the new clean branch, **cherry-pick or path-port ONLY the runner-specific
  code** from commit `94749a2` (the sandboxed process runner: timeout, kill path,
  capped logs, repo-local IO, full trace, its tests and docs, and any
  runner-only Rust/CLI/dashboard additions).
- **Do NOT import** `03_scripts/context_memory/`, `03_scripts/agent_command_center/`,
  `14_context/memory/`, or any committed runtime residue. Reuse the existing
  approval queue (`03_scripts/agent_os/approval_queue.py`), bounded executor
  (`approved_executor.py`), and the `agent_os_guard` Rust binary already on main.
- Keep one product path: extend the existing approval queue / guard / dashboard;
  do not add a parallel runner, memory system, or command center.

## Runner safety bounds (must hold)

The runner runs exactly ONE allowlisted local worker process, behind the Rust
guard + approval queue, with: wall-clock timeout, explicit kill path, capped
stdout/stderr logs under `14_context/agent_os/runs/`, repo-local IO only
(reuse `approved_executor` allowed roots + path normalization), and a full JSON
trace. No network, no shell-from-model-output, no new capabilities, no live
account/browser/computer-use actions.

## Status

Main is ready for the Codex runner clean branch.
