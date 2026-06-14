# Ghoti Sandboxed Local Agent Runner

## Purpose

This is the first real local agent process in Ghoti. It turns the approved
execution substrate into a supervised process lifecycle without enabling
arbitrary commands or risky live actions.

The allowlisted workers are `repo-summary-worker` and
`local-model-summary-classification-worker`, with only one active at a time.
They read declared repo-local context files and return source-linked results. They cannot
open a browser, use the network, touch accounts, click/type, send/post, buy,
pay, trade, write files, launch another process, or turn model output into a
command.

## Supervised Lifecycle

1. A workflow suggestion becomes a `run_local_worker` action request.
2. The Rust `agent_os_guard` validates the action, capability, worker identity,
   bounded runtime, paths, ownership, approval state, and fingerprint.
3. The request enters the existing approval queue.
4. A human explicitly approves the request.
5. The Rust guard validates the approved request again.
6. The runner starts exactly one fixed Python entrypoint with fixed registry
   arguments and a sanitized environment.
7. The worker receives data through stdin and returns data through stdout.
8. The runner terminates it on timeout or a repo-local cancellation marker.
9. Stdout and stderr are capped; oversized output fails closed.
10. The runner writes the artifact, run record, evidence note, handoff, and
   final runner state.

The runner uses the existing Agent OS queue, memory pointers, command-center
panel, evidence folders, and handoff folders. It does not add a second
dashboard or memory system.

## Rust Policy Rules

The guard allows `run_local_worker` only when:

- capability `agent_os.spawn_allowlisted_worker` is requested;
- `worker_id` is one of the two fixed workers;
- the worker registry fingerprint is exact;
- task is allowlisted;
- runtime is between 1 and 30 seconds;
- all reads and writes are normalized repo-relative paths;
- all outputs are declared and owned;
- no ownership lock conflicts exist;
- no `command`, `args`, `executable`, `shell`, `env`, `script`, or code field
  exists;
- `approved_local` has a valid approval hash.

## Commands

```powershell
python 03_scripts/agent_os/ghoti_agent_os.py --propose-worker-run coding-task --json
python 03_scripts/agent_os/ghoti_agent_os.py --list-approvals --json
python 03_scripts/agent_os/ghoti_agent_os.py --approve-action <request_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --execute-approved <request_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --runner-status --json
python 03_scripts/agent_os/ghoti_agent_os.py --cancel-worker <request_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --full-worker-demo --json
python 03_scripts/agent_os/ghoti_agent_os.py --full-local-model-worker-demo --json
```

The full demo is an explicit operator command that proposes, approves, and
executes one bounded worker run. Normal operation keeps proposal, approval,
and execution as separate commands.

## Evidence and Kill Path

Generated runtime files:

- `14_context/agent_os/workflows/worker_result_<request_id>.md`
- `14_context/agent_os/runs/worker_run_<request_id>.json`
- `14_context/agent_os/evidence/worker_run_<request_id>.md`
- `14_context/agent_os/handoffs/worker_run_<request_id>.md`
- `14_context/agent_os/runner_control/state_<request_id>.json`
- `14_context/agent_os/runner_control/cancel_<request_id>.json`

Only one worker can hold `runner_control/active_worker.json`. Cancellation
writes the fixed request-specific marker; the supervising runner terminates
the matching process and records `cancelled`. Timeout records `timed_out`.

## Still Blocked

- Arbitrary executables, arguments, shell commands, and model-output commands
- More than one local agent process at a time
- Swarms and live Claude/Codex/Hermes process launch
- Browser and computer-use
- Mouse/keyboard input
- Accounts, login, email sending, Telegram actions, and n8n execution
- Posting, purchases, payments, trading, and money movement
- Network access and external writes

Future workers must be added one at a time to both the Rust and Python
allowlists, receive a separate audit, and preserve this approval lifecycle.
