# Ghoti Approved Execution Substrate

## Purpose

This is the bridge from suggestions to one real, supervised local action.
Ghoti can now create an action request, validate it with Rust, place it in an
inspectible approval queue, record explicit approval, and write one bounded
repo-local text/JSON artifact with evidence.

It is intentionally not live autonomy. The later sandboxed-runner extension
may launch one fixed repo-summary worker after approval; arbitrary commands,
other agents, browser actions, click/type, accounts, sending/posting, and
external writes remain blocked.

## Architecture

1. The local worker creates a suggestion and a `ghoti_action_request/1`.
2. `agent_os_guard` validates schema, capabilities, paths, ownership, runtime,
   approval state, and the deterministic request fingerprint.
3. A valid suggestion enters `14_context/agent_os/approval_queue/pending/`.
4. An explicit CLI or command-center approval creates a hashed approval marker
   and runs the Rust guard again.
5. Execution runs the Rust guard a third time.
6. The approved executor writes only the declared artifact, run record,
   evidence note, and handoff.
7. The queue records the final `executed` or `failed` state.

Queue transitions are append/copy based so the audit trail does not depend on
destructive deletes. Only the record whose embedded state matches its folder
is active.

## Rust Guard

The Rust guard is the deterministic policy kernel:

```powershell
cargo run --release --bin agent_os_guard -- validate --request 14_context/agent_os/contracts/action_request.schema.example.json --repo-root . --json
cargo run --release --bin agent_os_guard -- fingerprint --request 14_context/agent_os/contracts/action_request.schema.example.json --repo-root . --json
```

It denies unknown actions/capabilities, absolute or escaping paths, output
paths outside approved roots, ownership conflicts, unbounded runtime, and an
`approved_local` request without a valid approval hash. Raw approval values
are never emitted.

Approved output roots:

- `14_context/agent_os/`
- `14_context/memory/agent_handoffs/`
- `14_context/operator_reports/generated/`

## Allowlisted Actions

- `write_handoff_file`
- `write_workflow_plan`
- `write_evidence_note`
- `update_latest_state_note`

These actions write text/JSON artifacts only. The current worker-to-approval
bridge maps each existing workflow to one of these actions.

## Operator Commands

```powershell
python 03_scripts/agent_os/ghoti_agent_os.py --propose-action coding-task --json
python 03_scripts/agent_os/ghoti_agent_os.py --list-approvals --json
python 03_scripts/agent_os/ghoti_agent_os.py --approval-status --json
python 03_scripts/agent_os/ghoti_agent_os.py --approve-action <request_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --reject-action <request_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --execute-approved <request_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --full-approved-demo --json
```

The command-center Agent OS panel exposes the same bounded flow. Dashboard
routes accept only an allowlisted workflow ID or a validated deterministic
request ID. They do not accept commands, paths, capabilities, or payloads.

## Full Approved Demo

`--full-approved-demo` proves the complete supervised path:

1. create a coding-task suggestion;
2. propose a request;
3. validate and queue it;
4. record explicit local approval;
5. validate again and execute;
6. write a workflow artifact, run record, evidence, and handoff.

Generated evidence:

- `14_context/agent_os/evidence/full_approved_demo_<timestamp>.md`
- `14_context/agent_os/evidence/full_approved_demo_<timestamp>.json`

On restricted Windows worktrees, data bytes may be written through the
existing fixed data-only writer fallback. It has fixed code, encoded data,
and no user/model command surface.

## What Is Real Now

- A Rust policy decision is required for every request transition.
- An explicit approval queue persists inspectible JSON state.
- One approved local artifact write really occurs.
- Execution produces a run record, evidence note, and handoff.
- The command center displays pending/approved/executed counts and bounded
  approval actions.

## What Remains Blocked

- Any local agent process except the fixed approved `repo-summary-worker`
- Swarm execution
- Browser and computer-use
- Mouse/keyboard input
- Accounts, email sending, Telegram actions, and n8n wiring
- Posting, purchases, payments, trading, and money movement
- External writes and arbitrary command execution
- Model-output-to-command loops

## Future Integration

This branch is based on the integrated Agent OS command center, so Claude's
Agent OS CLI, workflows, memory pointers, and dashboard are extended directly.
Future swarms can propose separate requests with file ownership and capability
sets; each request still needs a Rust verdict and human approval. Future
computer-use, content, business, and email lanes should add new policy
contracts only after separate audited milestones. They must not bypass this
queue.
