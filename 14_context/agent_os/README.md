# Ghoti Agent OS - generated artifacts

This folder holds the command center's repo-local outputs. Everything in
the subfolders is generated, suggestion-only, and safe to regenerate:

| Folder | Content |
|--------|---------|
| `workflows/` | Workflow plans written by `--plan-workflow` |
| `handoffs/` | Worker suggestions and copy-paste handoff packets |
| `runs/` | Self-check probes and ownership-check inputs (role-namespaced) |
| `evidence/` | Full local demo evidence reports (`full_local_demo_*.md/.json`) |

Generated files are gitignored; only the READMEs are tracked.

`APPROVED_ACTIONS.json` (not present by default) is the human-edited
approval file. If it exists and lists `allow_output_dirs` (repo-local
only), the suggestion-only worker may also write into those folders.
Without it, the worker can write nowhere outside this tree, and it can
never execute commands either way.
