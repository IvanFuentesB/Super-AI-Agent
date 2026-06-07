# Ghoti N+6.27A - Repo-Backed Controlled Swarm Launcher (Dry Run)

## Summary

N+6.27A builds the **first Ghoti-side swarm launcher**, **dry-run only**. It reads a task
spec, validates scope, assigns roles, detects file-ownership overlap, proposes worktree
paths (placeholders), and emits a **dry-run execution plan** with kill-switch / approval
gates and an Agent-Arena-shaped status block. It **launches nothing**. It is **repo-backed**:
design patterns are adapted from inspected swarm repos; no third-party code is vendored.

This lane may run in parallel with Codex N+6.26B because it does **not** edit the N+6.26A
Claude swarm deep-intake files.

## Repo-backed approach

Per the lane's repo-backed rule, the candidate repos were **shallow-cloned into the
gitignored sandbox** `21_repos/third_party_runtime_sandbox/` and **read only** (LICENSE +
README + structure). Nothing was installed, executed, or committed from them. Patterns were
adapted into **original** Ghoti code. Attribution:
`14_context/swarm_launcher/repo_inspiration_manifest_n6_27a.json` (+ report).

| Repo | License | Adapted pattern |
|------|---------|-----------------|
| `am-will/swarms` | no LICENSE file (patterns only) | explicit task deps -> parallel waves; plan = coordinate |
| `affaan-m/claude-swarm` | MIT | dependency graph; **file conflict detection**; budget gate; quality gate; status/replay |
| `HKUDS/ClawTeam` | MIT | one-command goal -> team; roles; local file state |
| `affaan-m/ecc` | MIT | AGENTS.md/RULES.md governance; scanner patterns |

**Rust toolchain:** not required by any inspected repo (no `Cargo.toml`) and **not
installed**; the launcher is pure Python stdlib.

## Files

| Piece | Path |
|-------|------|
| Launcher | `03_scripts/swarm_launcher/ghoti_swarm_launcher.py` |
| PowerShell check | `03_scripts/swarm_launcher/check_swarm_launcher.ps1` |
| Task / plan schemas | `14_context/swarm_launcher/swarm_task_schema.json`, `swarm_plan_schema.json` |
| Examples | `14_context/swarm_launcher/examples/{basic_two_agent,parallel_safe,blocked_overlap}_task.json` |
| Attribution | `14_context/swarm_launcher/repo_inspiration_manifest_n6_27a.json` (+ report) |
| README | `14_context/swarm_launcher/README.md` |

## The launcher model

- **Roles:** planner, builder, auditor, summarizer, human_approver.
- **Default agents:** ChatGPT strategy (planner), Claude builder (builder), Codex auditor
  (auditor), Hermes coordinator (coordinator), local model summarizer (summarizer), plus the
  human approver.
- **Scope validation:** every task file must be a repo-relative path inside the allowed
  scope - no absolute paths, no drive letters, no `..`.
- **Overlap detection:** **one owner per file/path**. If two tasks claim the same path, the
  plan is **blocked**.
- **Waves:** tasks are ordered by `depends_on` into dependency waves, each bounded by
  `max_parallel` (a rolling-pool idea from am-will/swarms).
- **Proposed worktrees:** placeholder paths only (`<repo>/.claude/worktrees/<task>`); no
  worktree is created.
- **Plan status:** `dry_run_ready` or `blocked` (with reasons). Either way, nothing runs.

## Gates and refusals (always on)

- `live_launch_enabled = false`, `approval_required = true`, `kill_switch_required = true`.
- **Main merge only by the Codex gate.** One owner per path. Human approver required.
- **Refused live actions:** live agent launch; process / subprocess / shell launch; git
  worktree creation; starting a Claude/Codex/Hermes process; browser/computer-use; MCP;
  account login; money/trading; mass messaging; auto-submit; secret/token access.

## Safe to visualize in the Agent Arena

The plan includes an `arena_status` block (agents + states, `simulation: true`,
`live_execution: false`) so the Agent Arena can render the proposed swarm later without any
live execution.

## Real launching is deferred

This milestone produces a **plan only**. Real launching - actually creating worktrees and
starting agent processes - is **deferred to a later, audited, human-approved milestone**.
The next step is a kill-switch + approval implementation and a first **single-pair** real
launch (one Claude builder + one Codex auditor on a trivial task), fully logged.

## Validation

- `--check --json` -> `ok: true` (no_subprocess, no_shell_true, no_os_exec_or_popen,
  no_file_writes, no_worktree_creation; live_launch_enabled false; approval + kill required).
- `--task basic_two_agent_task.json --dry-run` -> `dry_run_ready`, two waves.
- `--task blocked_overlap_task.json --dry-run` -> `blocked` (one owner per path).
- `check_swarm_launcher.ps1` -> `ok: true`.
- Public security audit `failed_checks: 0`; launcher status / context-pack / repo-map ok.

## Safety posture

Dry-run only. No process spawn, no subprocess, no shell, no os-level exec, no worktree
creation, no file writes, no launching agents, no browser/computer-use, no MCP, no account
login, no auto-submit, no Docker, no hooks, no secrets, no real local paths/usernames
(placeholders only). No third-party code committed; the clone sandbox is gitignored. This
lane does not edit the N+6.26A Claude swarm deep-intake files (N+6.26B not yet merged).
