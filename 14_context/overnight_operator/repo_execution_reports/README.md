# Repo execution reports (N+6.19A)

This folder holds reports from `ghoti_repo_execution_sandbox.py` about what it did
with each allowlisted external repo: clone, static scan, and allowlisted read-only
metadata commands.

## What is committed vs generated

- **Committed:** this `README.md` and any intentionally curated summary report (for
  example, the N+6.19A MarkItDown execution summary).
- **Generated (never committed):** per-run reports the sandbox writes under
  `generated/`. That subfolder is git-ignored, and the cloned repo contents under
  `21_repos/third_party_runtime_sandbox/` are git-ignored too.

## Report fields

Every sandbox action records:

- `repo` - the allowlisted repo name
- `action` - `list`, `static_scan`, `clone`, or `run_allowlisted`
- `command_preview` - the exact argument-list command (never a shell string)
- `executed` - whether the command actually ran
- `exit_code` - the process exit code (or null)
- `timeout` - the timeout applied
- `cwd` - the working directory (always inside the sandbox)
- `files_touched` - paths created/read (clones stay inside the sandbox)
- `safety_verdict` - `safe`, `needs_review`, or `blocked`
- `next_action` - the prepared next safe step

## Safety

Clones go only under `21_repos/third_party_runtime_sandbox/` and are never committed.
No shell-string subprocess, no PowerShell expression invocation, no containers, no package install, no remote script piping,
no secrets. Runtime execution (editable install / CLI help / tests) stays disabled
unless the static scan passes and the matching feature flag is enabled.
