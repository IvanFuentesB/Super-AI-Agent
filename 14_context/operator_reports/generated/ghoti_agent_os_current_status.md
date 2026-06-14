# Ghoti Agent OS - Current Status

One coherent local product path. This is the operator snapshot.

## Main

- `origin/main` = `e4d2b629adf7e1c9137eb004dafe0dc3af7135d1`.
- Merged PRs: #14/#15/#16 (working MVP recipes/operator console), #17 (integrated
  Agent OS MVP), #18 (approved execution substrate).
- One of each: dashboard, memory/search, workflow launchpad, handoff path,
  approval queue, bounded executor; two role-distinct Rust guards
  (`ghoti_policy_checker` = ownership/recipe, `agent_os_guard` = approved-action).
- No duplicate `context_memory/`, `agent_command_center/`, or `14_context/memory/`.

## Open branches / PRs

- `feat/ghoti-agent-os-approved-worker-swarm-coordinator` - swarm coordinator
  control plane (this work). Plans many workers, executes at most one at a time
  through the approval queue. Planning-only; not live swarm execution.
- Codex runner branch `feat/ghoti-agent-os-local-agent-runner-and-model-worker`:
  NOT yet pushed. The old `feat/ghoti-agent-codex-sandboxed-local-agent-runner`
  (`94749a2`, based on old substrate `96c8d627`) must be cleanly re-based, not
  merged as-is.

## What is real now

| Capability | State |
|---|---|
| Local dashboard + Agent OS panel | real (localhost 127.0.0.1:3210) |
| Memory/search (path:line pointers) | real |
| Workflow templates + launchpad | real |
| Handoff packet generation | real (copy-paste only) |
| Local worker suggestions | real (suggestion-only) |
| Two Rust guards (ownership + approved-action) | real |
| Approval queue (propose/approve/execute) | real |
| Bounded approved artifact writing | real (repo-local text/JSON only) |
| Full local demo | real |
| Full approved demo | real |
| Swarm coordinator (plan many, run one) | real (planning-only, single-worker lock) |
| Run records / evidence | real |

## What remains blocked

Real browser control, mouse/keyboard computer-use, account actions, email
sending, posting, purchases, payments, Telegram live commands, n8n live
execution, real/parallel swarm execution, external writes, model-output-as-command.

## Commands

```
# Dashboard
python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
# Full local demo
python 03_scripts/agent_os/ghoti_agent_os.py --full-demo --json
# Full approved demo (propose -> approve -> execute, one bounded write)
python 03_scripts/agent_os/ghoti_agent_os.py --full-approved-demo --json
# Full swarm planning demo (plans 3, queues one step as approval request)
python 03_scripts/agent_os/ghoti_agent_os.py --full-swarm-planning-demo --json
# Worker / local-model worker demos: available once the Codex runner branch lands
```

## Next big target

1. Approved local model routing (Ollama/Gemma) for cheap local drafts, behind
   the existing approval queue + guard.
2. Then the browser/computer-use OBSERVATION harness (observe-only, no control).

## Merge order

1. Merge the Codex local-agent-runner + model-worker branch first (once pushed,
   clean-based on main, full gate green) - it executes single approved steps.
2. Then merge the swarm coordinator branch - its queued steps are executed by
   that runner. Both meet at the approval queue contract, so order is flexible,
   but landing the runner first gives the coordinator something to execute.

## Coherence

Repo is coherent: one product path, no duplicate-system risk. The swarm
coordinator reuses the approval queue and guard; it adds no second queue,
executor, memory system, or command center.
