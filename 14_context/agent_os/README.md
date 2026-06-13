# Ghoti Agent OS - command center and guard artifacts

This folder holds the integrated command center's repo-local outputs and the
first Agent OS guard vertical slice. Everything remains local, supervised,
suggestion-only, and deny-by-default.

The Rust guard validates proposed local worker actions before the guarded
Python harness may render a simulation or suggestion-only plan. The command
center and guarded harness never execute `approved_local`, browser,
computer-use, account, posting, purchase, or model-output-as-command actions.

| Folder | Content |
|--------|---------|
| `workflows/` | Generated workflow plans written by `--plan-workflow` |
| `requests/` | Public-safe example guard policy requests |
| `trials/` | Harmless suggestion-only trial artifacts |
| `handoffs/` | Worker suggestions and copy-paste handoff packets |
| `runs/` | Guard decisions, self-check probes, and local run records |
| `evidence/` | Full local and approved-local demo evidence reports |
| `contracts/` | Public-safe action request examples |
| `approval_queue/` | Inspectible pending/approved/rejected/executed/failed state |

Generated command-center artifacts are gitignored and safe to regenerate.
Small deterministic guard examples may be tracked as public-safe evidence.
On Windows, generated text may use the repo's fixed data-only Node writer
fallback. Its destination is already allowlisted and its content is encoded
data; it cannot accept or execute user/model-supplied commands.

`APPROVED_ACTIONS.json` is not present by default. If a human creates it and
lists repo-local `allow_output_dirs`, the suggestion-only command-center
worker may write suggestions into those folders. It still cannot execute
commands. Raw approval values are never copied into guard decisions, run
records, or handoffs.

The approved-execution substrate adds one deliberately small real action:
after explicit approval, the executor may write a declared repo-local
text/JSON artifact plus its run record, evidence note, and handoff. The Rust
guard validates the request before queueing, approval, and execution. This is
not external or live automation: browser, computer-use, accounts, payments,
posting, sending, command execution, and writes outside the approved roots
remain denied.
