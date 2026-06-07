# Ghoti N+6.27A - Repo-Backed Controlled Swarm Launcher (Dry Run) (Report)

## Verdict

IMPLEMENTED_AND_PUSHED

## Lane

- Branch: `feat/ghoti-agent-claude-n6-27a-repo-backed-controlled-swarm-launcher`
- Worktree: `<repo>/.claude/worktrees/n6_27a_repo_backed_controlled_swarm_launcher`
- Base main: `origin/main` `e1a6927` (docs: record n6.25b hermes memory status merge gate)
- Codex audit target: `audit/ghoti-agent-codex-n6-27a-repo-backed-controlled-swarm-launcher`
- Commit: `feat(ghoti): add repo-backed swarm launcher dry run`

## Start condition

- `git fetch origin --prune`; `origin/main` = `e1a6927`.
- N+6.25B (Hermes status packet) confirmed on main.
- N+6.26B (Claude swarm deep intake) **not merged** -> this lane did **not** edit any
  N+6.26A Claude swarm deep-intake file.
- Clean worktree from `origin/main`; dirty primary worktree untouched.

## Mission

Build the first Ghoti-side swarm launcher, **dry-run only**, using existing swarm repos as
reference where safe instead of rebuilding from scratch.

## Inspected repos (read-only, gitignored sandbox)

Shallow-cloned into `21_repos/third_party_runtime_sandbox/` (gitignored; contents never
committed) and read LICENSE/README only - not installed, not executed:

- `am-will/swarms` - no top-level LICENSE file (patterns only, no code reuse).
- `HKUDS/ClawTeam` - MIT (c) 2025 HKUDS.
- `affaan-m/claude-swarm` - MIT (c) 2026 Affaan Mustafa.
- `affaan-m/ecc` - MIT (c) 2026 Affaan Mustafa.

## What was adapted (patterns, not code)

- explicit per-task dependencies -> parallel **waves** (am-will/swarms),
- **file conflict detection** -> overlap detection; budget/quality-gate ideas; status/replay
  for visualization (affaan-m/claude-swarm),
- one-command goal -> orchestrated team; roles; local file state (HKUDS/ClawTeam),
- governance + scanner patterns (affaan-m/ecc).

No third-party code is vendored or committed. Attribution:
`14_context/swarm_launcher/repo_inspiration_manifest_n6_27a.json` (+ report).

## Dry-run launcher summary

`03_scripts/swarm_launcher/ghoti_swarm_launcher.py` (pure Python stdlib):

- reads a task spec, **validates scope** (repo-relative, no `..`, inside allowed paths),
- assigns **roles** (planner, builder, auditor, summarizer, human_approver) to **default
  agents** (ChatGPT strategy, Claude builder, Codex auditor, Hermes coordinator, local model
  summarizer),
- detects **file-ownership overlap** (one owner per path -> blocks on conflict),
- proposes **placeholder** worktree paths (`<repo>/.claude/worktrees/<task>`),
- orders tasks into **dependency waves** (bounded by `max_parallel`),
- emits a **dry-run plan** (`dry_run_ready` or `blocked`) that **refuses live launch**,
- exposes an **Agent-Arena-shaped status** block (`simulation: true`, `live_execution: false`),
- defines kill-switch / approval gates and records repo attribution.

Examples: `basic_two_agent_task.json` -> ready (2 waves); `parallel_safe_task.json` -> ready
(3 waves); `blocked_overlap_task.json` -> blocked (one owner per path).

## Gates and refused live actions

- `live_launch_enabled=false`, `approval_required=true`, `kill_switch_required=true`, main
  merge by Codex gate only, one owner per path, human approver required.
- Refused: live agent launch; process / subprocess / shell launch; git worktree creation;
  starting a Claude/Codex/Hermes process; browser/computer-use; MCP; account login;
  money/trading; mass messaging; auto-submit; secret/token access.

## Real launching deferred

This milestone is a **plan only**. Real launching (creating worktrees, starting agent
processes) is **deferred to a later, audited, human-approved milestone** - starting with a
kill-switch/approval implementation and a first single-pair (1 Claude builder + 1 Codex
auditor) launch on a trivial task.

## Rust toolchain status

Checked: no inspected repo has a `Cargo.toml`. **Rust is not required and was not
installed.** The launcher is pure Python standard library.

## Validation

- `python -m unittest discover -p "test_n6_27a_*.py"` -> all tests pass.
- `--check --json` -> `ok: true` (no_subprocess, no_process_spawn, no_file_writes,
  no_worktree_creation; live_launch_enabled false; approval + kill required).
- `--task basic_two_agent_task.json --dry-run` -> `dry_run_ready`; `blocked_overlap_task.json`
  -> `blocked`.
- `check_swarm_launcher.ps1` -> `ok: true`.
- `public_repo_security_audit.py --run --json` -> `failed_checks: 0`, `safe_to_make_public:
  true`, 0 blockers.
- `ghoti_product_launcher.py --status` -> ok; `--context-pack` and `--repo-map` -> ok.
- `git diff --check` / `git show --check` clean; residue restored; no third-party repo
  contents committed; no LAST_RUN committed.

## Safety summary

- Dry-run only. No process spawn, no subprocess, no shell, no os-level exec, no worktree
  creation, no file writes, no launching agents.
- No browser/computer-use, no MCP, no account login, no money/trading, no mass messaging,
  no auto-submit, no Docker, no hooks.
- No secrets/tokens/cookies/auth files. No real local paths/usernames/private images
  (placeholders only). No third-party code committed; clone sandbox gitignored.
- This lane did not edit the N+6.26A Claude swarm deep-intake files (N+6.26B not merged).

## Final verdict

IMPLEMENTED_AND_PUSHED
