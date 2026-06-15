# Ghoti Repo Intake Safety

The safe way to evaluate an unknown repo before adapting any of its code. The
intake never executes the repo. Dry-run never clones; `--apply` shallow-clones
into a gitignored sandbox, collects metadata only, and writes a report with a
conservative decision.

## Command

```
python 03_scripts/tool_stack/repo_intake.py <repo-url> [--apply]
```

- No `--apply` (default dry-run): nothing is cloned or executed. It validates the
  target and prints the `planned_sandbox` path so you can see where a clone would
  go.
- `--apply`: shallow-clones (`--depth 1`, hooks disabled) into the gitignored
  sandbox, runs the static scans, and writes a report. It still never runs
  install scripts, build steps, or any code from the repo.

Accepted targets: `https://...` / `git@...` git URLs, or `owner/name` shorthand
(mapped to GitHub). Local filesystem paths are rejected.

## What happens on --apply

1. Shallow-clone into the sandbox:
   `14_context/tool_intake/repo_sandbox/<slug>/`
   (the sandbox directory is gitignored; an alternative `.ghoti_tool_sandbox/`
   name may be used in other setups). If the path already exists, intake stops
   and asks you to inspect or remove it first.
2. Collect metadata only: license file, package manifests
   (`package.json`, `pyproject.toml`, `Cargo.toml`, `setup.py`,
   `requirements.txt`), declared npm script names, README snippet, file count.
3. Run the two static scans (below).
4. Write a report to `14_context/tool_intake/reports/<slug>_<timestamp>.json`
   and `.md` with a decision. Reports are committed; the cloned source is not.

Nothing from the repo is executed at any point: no `postinstall`, no build, no
script run. `executed_anything` is always `false`.

## Static scans

Two read-only pattern scans run over text-like files
(`.py .js .ts .json .sh .ps1 .toml .cfg .yml .yaml .md` and extensionless):

- Suspicious-pattern scan: install hooks and dangerous operations, e.g.
  `postinstall`, `preinstall`, `curl `, `wget `, `eval(`, `base64 -d`,
  `rm -rf`, `Invoke-Expression`, `powershell -enc`, `child_process`,
  `os.system`, `subprocess`, `/etc/`, `~/.ssh`, `AWS_SECRET`.
- Network / browser / account-indicator scan: surfaces that imply outbound
  calls, browser control, or credentials, e.g. `requests`, `httpx`, `fetch(`,
  `axios`, `playwright`, `puppeteer`, `selenium`, `oauth`, `api_key`, `token`,
  `stripe`, `smtp`, `imap`. These are informational flags, not failures.

## Decision values

- `inspect_more`: dry-run default, or needs a closer human read before adapting.
- `safe_to_adapt`: no suspicious hits; low-risk static reuse.
- `risky`: one or more suspicious hits; isolate, do not run.
- `reject`: five or more suspicious hits; do not adapt.

A decision is guidance, not approval. Adapting any code is a separate,
human-reviewed step. The repo is never run.

## Related

- Inspect-first queue: `14_context/tool_intake/repo_intake_queue.md`
- Intake safety rules: `14_context/tool_intake/intake_rules.md`
- Reject/blocked list: `14_context/tool_stack/rejected_or_blocked_tools.md`
