# Claude Code Slash Commands — N+3.45A

**Milestone:** N+3.45A
**Date:** 2026-05-05
**Branch:** feat/ghoti-agent-claude-n3-45-tooling-prompt-bus

---

## What Was Built

Four Claude Code project slash commands in `.claude/commands/`:

| Command | File | Purpose |
|---------|------|---------|
| `/goal` | `.claude/commands/goal.md` | Long-horizon Ghoti execution from current prompt |
| `/ultraplan` | `.claude/commands/ultraplan.md` | Deep planning mode |
| `/ghoti-status` | `.claude/commands/ghoti-status.md` | Repo + lane + prompt bus status |
| `/prompt-bus` | `.claude/commands/prompt-bus.md` | Prompt bus status and copy-paste guide |

---

## How to Use

In any Claude Code session in this repo, type:

```
/goal
```
→ Reads and executes `14_context/ghoti_current_prompt.md` as the full milestone prompt.

```
/ultraplan
```
→ Reads current state, lane locks, and prompt bus, then produces a detailed implementation plan without executing it.

```
/ghoti-status
```
→ Runs safe read commands (git status, branch, log, lane checks, prompt bus status) and summarizes.

```
/prompt-bus
```
→ Shows prompt bus status, explains how to write prompts, lists outbox files.

---

## Commands Detail

### /goal

- Reads `14_context/ghoti_current_prompt.md` and executes it
- Uses `Bash, Read, Write, Edit, Glob, Grep` tools
- Safety: no live actions, no cap bypass, stage intentional files only

### /ultraplan

- Read-only mode (Bash, Read, Glob, Grep)
- Produces: milestone summary, implementation plan, file ownership, risk list, validation plan, safety gates
- Does NOT implement — only plans

### /ghoti-status

- Bash-only (read commands)
- Runs: git status, git branch, git log, agent_lane_status --check/--list, prompt_bus --status
- Summarizes current lane state

### /prompt-bus

- Bash + Read
- Shows: canonical prompt path, outbox files, copy-paste instructions, template locations

---

## Validation

Verify commands are present:
```bash
ls .claude/commands/
# goal.md  ultraplan.md  ghoti-status.md  prompt-bus.md
```

Test /ghoti-status manually:
```bash
git status --short
git branch --show-current
git log --oneline -8
python 03_scripts/agent_lane_status.py --check
python 03_scripts/agent_lane_status.py --list
python 03_scripts/prompt_bus.py --status
```

---

## Safety Gates

- No commands run live/external/account actions
- No commands bypass usage limits
- `/goal` respects the same safety rules as `ghoti_current_prompt.md`
- All writes are inside repo root

---

## What Is Not Wired Yet

- No `/approve` command (approval inbox is still manual)
- No `/deploy` or `/push` command (push requires explicit user confirmation)
- No `/gemma` command (Gemma routing not yet wired to commands)

---

## Next Steps

- Add `/approve` command for approval inbox review
- Add `/lane-check` as alias for `python 03_scripts/agent_lane_status.py --check`
- Consider `/next-milestone` that calls `--recommend` from local_worker_router
