# ECC + Claude Swarm - Separate-Profile Test Plan (N+6.26A)

Milestone: N+6.26A
Date: 2026-06-06
Status: static planning only. This is a **plan** for the operator to run **manually** in a
**separate, throwaway Claude profile** - Ghoti does not run any of it and enables nothing.

ECC = **Everything Claude Code** (a bundle of commands/agents/skills/hooks), NOT elliptic
curve cryptography. Recorded source: `https://github.com/affaan-m/ecc` (verify license).

## Golden rule

**Never test swarm launching in the Ghoti environment or the operator's working Claude
profile.** Use an **isolated profile** (a distinct OS user profile or a disposable VM /
sandbox) that has:

- **no access** to the Ghoti repo,
- **no real accounts**, no secrets, no `.env`, no tokens/cookies,
- only a **scratch repo with junk data**, and git **worktrees** pre-created.

Bring back only **notes** (into `14_context/`), never the executable bundle.

## Safe test order (least risky -> most risky)

Run these one at a time, recording for each: automatic vs manual, token cost, whether it
needed worktrees, and exactly what it launched.

1. **subagents** - give the main session one read-only sub-task; watch it spawn a worker
   and report back. (Lowest risk.)
2. **skills** - add one `SKILL.md`; confirm the model loads it only when relevant.
3. **worktrees** - create a branch/worktree per agent on the scratch repo; confirm
   isolation.
4. **background agents** - `/bg` on a trivial task, then `claude --bg "<task>"`; watch them
   run async.
5. **agent view** - open the session list; steer a couple of background agents.
6. **agent teams** - enable the experimental env var, run a **small** team (2-3 agents) on
   the scratch repo with worktrees; record coordination behavior and **token cost**.
7. **dynamic workflows** - run a tiny `/workflows` task; **read the generated JavaScript
   before letting the runtime execute it**; watch phases/agent counts.
8. **hooks** - add one **no-op** validator hook; confirm it fires; confirm it can run code
   (this is why Ghoti keeps hooks off).
9. **community launchers (only after 1-8, license verified):**
   a. **ECC** (`affaan-m/ecc`) - install in the sandbox; inspect its commands/agents/hooks.
   b. **am-will/swarms** - exercise `swarm-planner` (Plan Mode) and `parallel-task`
      (bounded pool) on a scratch plan.
   c. **ClawTeam** (`HKUDS/ClawTeam`) - run the one-command flow on the junk repo; inspect
      `~/.clawteam/` JSON state.
   d. **affaan-m/claude-swarm** - try the terminal-UI orchestration (compare to Ghoti's
      Agent Arena).

## What to capture per item

- automatic vs manual; what required a human click/approval,
- token cost (rough); which items were expensive,
- whether it needed worktrees,
- whether it can commit / push / hit the network **without approval** (red flag),
- anything that surprised you (auto-commit, auto-push, outbound calls).

## What must stay disabled in Ghoti regardless

Live agent launching, agent teams, dynamic workflows, executable hooks, MCP,
browser/computer-use, auto-submit, and any community launcher. The sandbox findings inform
the **future Ghoti controlled launcher**; they do not enable anything here.

## Why a separate profile (not Ghoti)

ECC and the launchers wire **executable hooks** and **auto-launching** into whatever profile
they touch. Running them in the Ghoti environment would put live-action capability next to
the operator's real repo and accounts. Isolation keeps the blast radius at zero while the
ideas are evaluated honestly.
