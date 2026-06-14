# Ghoti Approved-Worker Swarm Coordinator

## Purpose

This is the planner/coordinator control plane that sits on top of the existing
approval queue. Ghoti can now lay out a multi-worker plan for a workflow, but it
executes at most ONE worker at a time, and only through the existing approval
queue plus the Rust `agent_os_guard`. The coordinator launches no process, runs
nothing in parallel, and adds no new queue and no new executor: it reuses
`03_scripts/agent_os/approval_queue.py`.

It is intentionally not live swarm execution. It cannot run agents in parallel,
launch a process, open a browser, click/type, touch an account, send/post
anything, or make an external write.

## What this is NOT

- Not parallel execution. At most one worker is ever in flight per plan.
- Not live actions. Queueing a step creates a pending approval request; it does
  not execute anything.
- No browser, computer-use, mouse/keyboard, account, money, posting, email,
  Telegram, n8n, MCP, or provider-API capability is reachable from a plan.
- No new execution path: the coordinator only reuses the existing approval
  queue and bounded executor.

## How it fits

```
coordinator (build plan)
  -> approval queue (queue ONE step as one request)
    -> agent_os_guard (validate the request)
      -> human approve
        -> bounded executor (one repo-local text/JSON write)
```

The coordinator stops at "queue ONE step". A human still approves and executes
each step through the existing approval queue, and the bounded executor
(`03_scripts/agent_os/approved_executor.py`) performs the single repo-local
write. When the local-agent runner lands, it executes those approved single
steps; until then, the executed write is the same bounded text/JSON artifact the
approved execution substrate already produces.

## Control plane

The control plane is `03_scripts/agent_os/swarm_coordinator.py`. It plans
multiple workers, but schedules them one at a time:

1. Build a deterministic plan for an allowlisted swarm workflow.
2. Reconcile each step's status against the real approval queue.
3. Queue the next runnable step as exactly ONE approval request (no execution).
4. Refuse a second queue while any step is in flight (one-worker lock).

Per-step lifecycle: `planned -> queued -> approved -> executed` (or `blocked`).
A step is runnable only when all of its dependency steps are `executed`.

## Plan format

Plans are written under `14_context/agent_os/swarm_plans/` as JSON plus a
Markdown render (runtime, gitignored). Each plan has:

- `schema` (`ghoti_swarm_plan/1`)
- `plan_id` (deterministic, `swarm-` + the first 20 hex chars of the plan
  fingerprint)
- `workflow` and `base_workflow`
- `title`
- `created_at`
- `fingerprint` (deterministic sha256 over the workflow, base, and the
  worker/purpose/owned-files/dependencies/capabilities of every step)
- `single_worker_lock` (`true`)
- `mode` (`planning_only`)
- `steps`
- `safety` (`parallel_execution=false`, `max_workers_in_flight=1`,
  `live_execution=false`, `queue_through_approval_queue=true`)

Each step carries: `step` (1-based id), `worker_id`, `purpose`,
`required_inputs`, `output_target`, `status` (`planned`, `queued`, `approved`,
`executed`, or `blocked`), `owned_files`, `dependencies` (earlier step ids),
`risk_note`, and `capabilities`.

## The three swarm workflows

Each swarm workflow maps onto one base Agent OS workflow so queued steps reuse
the existing bounded write action.

| Swarm workflow | Base workflow | Steps |
|----------------|---------------|-------|
| `coding-task-swarm-plan` | `coding-task` | planner brief -> coder outline -> auditor findings |
| `content-pipeline-swarm-plan` | `content-video` | researcher ideas -> content drafts -> planner publish checklist |
| `business-research-swarm-plan` | `business-research` | planner hypothesis -> researcher checklist |

Every step is read/plan/draft/checklist only. Nothing is published, scraped
live, or purchased.

## Worker allowlist

Only these worker ids may appear in a plan; any other id is refused at plan
build:

- `planner`
- `coder`
- `auditor`
- `researcher`
- `content`
- `operator`
- `repo-summary-worker`
- `local-model-summary-classification-worker`

## Capability allowlist and deny list

A step may only request these capabilities:

- `repo_read`
- `status_read`
- `plan_render`
- `report_write_repo_local`
- `local_model_status_read`

Any other capability is refused at plan build. The explicit block list includes:
`account`, `browser`, `computer_use`, `money`, `mass_message`, `mcp`,
`secrets`, `telegram`, `posting`, `email_send`, `purchase`, `payment`,
`external_write`, `file_delete`, `file_move`, `agent_launch`, `auto_submit`, and
`provider_api`.

## Safety guarantees

- One-worker lock: only one step per plan may be in flight (queued or
  approved-not-executed). A second queue while a step is in flight is refused
  with `reason: one_worker_lock`.
- Queue-next is approval, not execution: `queue_next_step` creates exactly one
  pending approval request and returns `approval_state: pending`,
  `executed: false`. It runs nothing.
- Dependency order enforced: a step is runnable only when every dependency step
  is `executed`.
- Ownership-overlap block: independent steps (no dependency path between them)
  that share an owned-file prefix are auto-marked `blocked` at build, keeping
  one-at-a-time scheduling safe.
- Capability deny: unknown workers, blocked capabilities, and forward
  dependencies are rejected at plan build.
- Deterministic identity: the same workflow yields the same `plan_id` and
  `fingerprint`.

## CLI commands

```powershell
python 03_scripts/agent_os/ghoti_agent_os.py --plan-swarm coding-task-swarm-plan --json
python 03_scripts/agent_os/ghoti_agent_os.py --list-swarm-plans --json
python 03_scripts/agent_os/ghoti_agent_os.py --queue-next-swarm-step <plan_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --swarm-status --json
python 03_scripts/agent_os/ghoti_agent_os.py --full-swarm-planning-demo --json
```

## Dashboard card

The dashboard adds a "Swarm Coordinator" card (badge: planning-only) to the
existing Agent OS panel in `01_projects/dashboard_mvp`. It exposes the bounded
flow only - pick an allowlisted swarm workflow, build a plan, queue one step, or
run the planning demo. Endpoints, all under `/api/product-control/`:

- `GET agent-os-swarm-status`
- `GET agent-os-swarm-plans`
- `POST agent-os-plan-swarm`
- `POST agent-os-queue-next-swarm-step`
- `POST agent-os-full-swarm-planning-demo`

The routes accept only an allowlisted swarm workflow id or a validated plan id.
They do not accept commands, paths, capabilities, or payloads.

## Full swarm planning demo

`--full-swarm-planning-demo` builds all three plans and queues exactly one step
on the first plan to prove the approval path, then writes evidence:

- `14_context/agent_os/evidence/full_swarm_planning_demo_<timestamp>.md`
- `14_context/agent_os/evidence/full_swarm_planning_demo_<timestamp>.json`

The evidence records the plans built, the one queued step (an approval request,
not an execution), and asserts the single-worker lock and `live_execution=false`.

## What is real now

- A deterministic multi-worker plan per allowlisted swarm workflow.
- Queueing exactly one step at a time as a normal approval request, validated by
  the Rust guard.
- One-worker lock, dependency-order scheduling, ownership-overlap blocking, and
  capability/worker deny at build.
- Planning evidence under `14_context/agent_os/evidence/`.

## What remains blocked

- Real swarm / parallel execution
- Live local agent process launching
- Browser and computer-use
- Mouse/keyboard input
- Accounts, email sending, Telegram live actions, and n8n wiring
- Posting, purchases, payments, trading, and money movement
- External (out-of-repo) writes and arbitrary command execution
- Model-output-as-command loops

## Validation

- Focused tests: `01_projects/runtime_mvp/tests/test_agent_os_swarm_coordinator.py`
  (17/17 ok).
- Rust guard suite: cargo 31/31 ok.
- Full approved demo ok; full swarm planning demo ok.
- Live dashboard HTTP plan/status/queue-next verified; a bad plan id returns 400.

## Related docs

- Approved execution substrate: `docs/GHOTI_APPROVED_EXECUTION_SUBSTRATE.md`
- Current status: `docs/GHOTI_CURRENT_PRODUCT_STATUS.md`
- Roadmap: `docs/GHOTI_ROADMAP_TO_FULL_COMPUTER_USE.md`
