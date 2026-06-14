# Ghoti Agent OS - generated artifacts

This folder holds the integrated command center's repo-local outputs and the
Agent OS guard vertical slices. Everything remains local, supervised, and
deny-by-default. One of two fixed worker processes can now run after explicit
approval; all other worker/process identities remain denied.

The Rust guard validates every approved artifact or local-worker request.
Browser, computer-use, account, posting, purchase, and
model-output-as-command actions remain denied.

| Folder | Content |
|--------|---------|
| `workflows/` | Workflow plans written by `--plan-workflow` |
| `handoffs/` | Worker suggestions and copy-paste handoff packets |
| `runs/` | Self-check probes, ownership-check inputs, and local run records |
| `evidence/` | Full local, approved-local, and worker-run evidence reports |
| `approval_queue/` | Inspectable approval state in `pending/`, `approved/`, `rejected/`, `executed/`, `failed/` (runtime state is gitignored) |
| `contracts/` | Tracked public-safe action-request examples |
| `requests/` | Tracked example worker request (`example_worker_request.json`) |
| `trials/` | Tracked trial inputs and notes for the approval substrate |
| `runner_control/` | Generated active/cancel/state records for one local worker |

Generated files are gitignored; only the READMEs and the tracked example
files under `contracts/`, `requests/`, and `trials/` are committed.

The approval substrate is suggestion-only until an explicit human approval:
a proposed request waits in `approval_queue/pending/` and does nothing on its
own. After approval, the bounded executor
(`03_scripts/agent_os/approved_executor.py`) writes only text/JSON, only the
four allowlisted actions, and only under repo-local roots `14_context/agent_os/`
and `14_context/operator_reports/generated/`. It launches no process, runs no
shell command, and makes no network call. See
`docs/GHOTI_APPROVED_EXECUTION_SUBSTRATE.md`.

`APPROVED_ACTIONS.json` (not present by default) is the human-edited
approval file. If it exists and lists `allow_output_dirs` (repo-local
only), the suggestion-only worker may also write into those folders.
Without it, the worker can write nowhere outside this tree, and it can
never execute commands either way.

The approved-execution substrate adds one deliberately small real action:
after explicit approval, the executor may write a declared repo-local
text/JSON artifact plus its run record, evidence note, and handoff. The Rust
guard validates the request before queueing, approval, and execution. This is
not external or live automation: browser, computer-use, accounts, payments,
posting, sending, command execution, and writes outside the approved roots
remain denied.

The sandboxed local agent runner recognizes `repo-summary-worker` and
`local-model-summary-classification-worker`, with exactly one active at a
time. Each receives a fixed JSON invocation over stdin and returns JSON over
stdout. The existing approval queue and Rust guard must approve the request
and worker-registry fingerprint before the runner starts it. Timeout,
cancellation, and capped logs are supervised and recorded; arbitrary commands
and model-output-to-command remain impossible by contract.
