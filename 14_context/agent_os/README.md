# Ghoti Agent OS - generated artifacts

This folder holds the command center's repo-local outputs. Everything in
the subfolders is generated, suggestion-only, and safe to regenerate:

| Folder | Content |
|--------|---------|
| `workflows/` | Workflow plans written by `--plan-workflow` |
| `handoffs/` | Worker suggestions and copy-paste handoff packets |
| `runs/` | Self-check probes and ownership-check inputs (role-namespaced) |
| `evidence/` | Full local demo evidence reports (`full_local_demo_*.md/.json`) |
| `approval_queue/` | Inspectable approval state in `pending/`, `approved/`, `rejected/`, `executed/`, `failed/` (runtime state is gitignored) |
| `contracts/` | Tracked action-request schema example (`action_request.schema.example.json`) |
| `requests/` | Tracked example worker request (`example_worker_request.json`) |
| `trials/` | Tracked trial inputs and notes for the approval substrate |

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
