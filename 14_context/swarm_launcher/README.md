# Ghoti Swarm Launcher - Dry Run Only (N+6.27A)

The first Ghoti-side controlled swarm launcher. It reads a **task spec** and emits a
**dry-run execution plan** that an operator could approve later. **It launches nothing.**

## Files here

- `swarm_task_schema.json` - shape of the input task spec.
- `swarm_plan_schema.json` - shape of the output dry-run plan.
- `examples/basic_two_agent_task.json` - build then audit (ready).
- `examples/parallel_safe_task.json` - plan, two parallel builders, audit + summary (ready).
- `examples/blocked_overlap_task.json` - two tasks claim one file (blocked).
- `repo_inspiration_manifest_n6_27a.json` / `repo_inspiration_report_n6_27a.md` -
  attribution for the inspected repos.

The launcher is `03_scripts/swarm_launcher/ghoti_swarm_launcher.py`.

## What the launcher does

1. reads a task spec (JSON),
2. validates task scope (repo-relative paths inside the allowed scope; no `..`, no absolute),
3. assigns roles (planner / builder / auditor / summarizer / human_approver) to default
   agents (ChatGPT strategy, Claude builder, Codex auditor, Hermes coordinator, local model
   summarizer),
4. checks **file-ownership overlap** (one owner per path),
5. proposes worktree paths using **placeholders** (`<repo>/.claude/worktrees/<task>`),
6. orders tasks into **dependency waves** (bounded by `max_parallel`),
7. writes a **dry-run execution plan** that **refuses live launch**,
8. exposes an **Agent-Arena-shaped status** block for later visualization,
9. defines **kill-switch / approval gates**,
10. records repo inspiration/attribution.

## What it never does

No process spawn, no `subprocess`, no `shell=True`, no `os.system`/exec, no git worktree
creation, no file writes, no launching Claude/Codex/Hermes, no browser/computer-use, no
MCP, no account login, no money/trading, no mass messaging, no auto-submit, no secret
access.

## Usage

```
python 03_scripts/swarm_launcher/ghoti_swarm_launcher.py --check --json
python 03_scripts/swarm_launcher/ghoti_swarm_launcher.py --task 14_context/swarm_launcher/examples/basic_two_agent_task.json --dry-run --json
python 03_scripts/swarm_launcher/ghoti_swarm_launcher.py --task 14_context/swarm_launcher/examples/blocked_overlap_task.json --dry-run --json
powershell -ExecutionPolicy Bypass -File 03_scripts/swarm_launcher/check_swarm_launcher.ps1
```

## Gates (always on)

`live_launch_enabled=false`, `approval_required=true`, `kill_switch_required=true`, main
merge by **Codex gate only**, one owner per path. **Real launching is deferred to a later,
audited, human-approved milestone.**
