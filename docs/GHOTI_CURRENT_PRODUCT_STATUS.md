# Ghoti Current Product Status

**Status:** Working local MVP (supervised, deny-by-default)
**Landed on main:** PR #17 (Agent OS MVP) and PR #18 (approved execution
substrate) are merged; `origin/main` is `f23a8f9`.
**Entry points:** `03_scripts/agent_os/ghoti_agent_os.py`,
`03_scripts/ghoti_product_launcher.py`

---

## Summary

This is the one-screen honest snapshot of what Ghoti can actually do on this
branch today. Everything real is local, repo-bound, and human-supervised:
suggestions and bounded text/JSON writes only, behind two Rust guards and an
explicit approval queue. Ghoti launches no agent and no process, and every
live step is performed by a human.

## What is real now

| Capability | Where it lives |
|------------|----------------|
| Local dashboard (localhost only) | `03_scripts/ghoti_product_launcher.py`, `01_projects/dashboard_mvp/` (`http://127.0.0.1:3210`) |
| Agent OS panel (dashboard left-nav) | `01_projects/dashboard_mvp/` Agent OS panel |
| Memory/search pointers (path:line) | `03_scripts/agent_os/local_worker.py` `search_memory` over `14_context/compact_memory`, `14_context/obsidian_vault`, `14_context/repo_knowledge/generated`, `docs` |
| Workflow templates (7 workflows) | `03_scripts/agent_os/workflow_templates.py` |
| Handoff generation (copy-paste only) | `14_context/agent_os/handoffs/` |
| Local worker suggestion outputs | `03_scripts/agent_os/local_worker.py` |
| Rust guard 1: ownership/recipe checks | `rust/ghoti_policy_checker` (`--check`, `--input`, `--ownership-input`) |
| Rust guard 2: approved-action validation | `rust/agent_os_guard` (`validate ... --json`, `guard_version agent_os_guard/0.2.0`) |
| Approval queue (inspectable JSON state) | `03_scripts/agent_os/approval_queue.py`, `14_context/agent_os/approval_queue/{pending,approved,rejected,executed,failed}/` |
| Approved bounded artifact writing | `03_scripts/agent_os/approved_executor.py` (text/JSON only, 4 allowlisted actions, 2 repo-local roots) |
| Swarm coordinator (planning-only, one-worker-lock) | `03_scripts/agent_os/swarm_coordinator.py` (plans multiple workers; queues at most ONE step at a time through the approval queue; no parallel launch) |
| Full local demo | `ghoti_agent_os.py --full-demo` |
| Full approved demo | `ghoti_agent_os.py --full-approved-demo` |
| Full swarm planning demo | `ghoti_agent_os.py --full-swarm-planning-demo` |
| Run records and evidence | `14_context/agent_os/runs/`, `14_context/agent_os/evidence/` |

The bounded executor writes only under `14_context/agent_os/` and
`14_context/operator_reports/generated/`, only the four allowlisted actions
(`write_handoff_file`, `write_workflow_plan`, `write_evidence_note`,
`update_latest_state_note`), refuses content with secret markers or absolute
Windows paths, and uses no subprocess or network of its own. Every run record
asserts `live_execution=false`, `network_used=false`, `browser_used=false`,
`account_action=false`, and `shell_command_executed=false`.

## What is still blocked

| Blocked capability | Why it is blocked |
|--------------------|-------------------|
| Browser control and computer-use | No control path is built or wired |
| Mouse and keyboard input | No input path is built or wired |
| Account access | No credentials path is approvable |
| Email sending | Draft-only; no send path |
| Posting to any channel | Draft-only; no publish path |
| Purchases, payments, trading, money movement | Never approvable |
| Telegram live actions | Status-doc only; no live action path |
| n8n live wiring | Not wired |
| Real multi-agent swarms | Simulation/planning only |
| External (out-of-repo) writes | Refused by the executor and guard |
| Model-output-as-command loops | No command surface accepts model output |

## Exact commands

Dashboard (localhost only):

```powershell
python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
python 03_scripts/ghoti_product_launcher.py --agent-os-status --json
```

Full local demo and full approved demo:

```powershell
python 03_scripts/agent_os/ghoti_agent_os.py --full-demo --json
python 03_scripts/agent_os/ghoti_agent_os.py --full-approved-demo --json
```

Swarm coordinator (planning-only, one-worker-lock):

```powershell
python 03_scripts/agent_os/ghoti_agent_os.py --plan-swarm coding-task-swarm-plan --json
python 03_scripts/agent_os/ghoti_agent_os.py --list-swarm-plans --json
python 03_scripts/agent_os/ghoti_agent_os.py --queue-next-swarm-step <plan_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --swarm-status --json
python 03_scripts/agent_os/ghoti_agent_os.py --full-swarm-planning-demo --json
```

Approval flow:

```powershell
python 03_scripts/agent_os/ghoti_agent_os.py --propose-action coding-task --json
python 03_scripts/agent_os/ghoti_agent_os.py --list-approvals --json
python 03_scripts/agent_os/ghoti_agent_os.py --approval-status --json
python 03_scripts/agent_os/ghoti_agent_os.py --approve-action <request_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --reject-action <request_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --execute-approved <request_id> --json
```

Rust guards:

```powershell
cargo run --release --bin agent_os_guard -- validate --request 14_context/agent_os/contracts/action_request.schema.example.json --repo-root . --json
cargo run --release --bin ghoti_policy_checker -- --check
cargo run --release --bin ghoti_policy_checker -- --ownership-input <wave.json>
```

## Next real step

The next big target is approved local model routing (cheap local drafts behind
the output guard), then a browser/computer-use observation harness (observation
only, zero control paths). Building on those, the first sandboxed local agent
process runner uses the Rust guard plus approval queue to run exactly ONE
allowlisted local worker process, with a timeout, a kill path, capped logs,
repo-local IO, and a full trace. It is the first time Ghoti launches a process,
it stays bounded to one approved allowlisted worker at a time, and it unlocks
nothing in the blocked table above. The swarm coordinator is the planning-only
control plane that will feed that runner one approved step at a time.

## Related docs

- Overview: `docs/GHOTI_AGENT_OS_OVERVIEW.md`
- Approved execution substrate: `docs/GHOTI_APPROVED_EXECUTION_SUBSTRATE.md`
- Swarm coordinator: `docs/GHOTI_APPROVED_WORKER_SWARM_COORDINATOR.md`
- Roadmap: `docs/GHOTI_ROADMAP_TO_FULL_COMPUTER_USE.md`

## Environment note

Windows Defender Controlled Folder Access blocks Python writes under
`Documents`; run write-heavy validation from a scratch worktree under
`%LOCALAPPDATA%/Temp`.
