# Ghoti runtime paths

Generated state does not belong in the repository. `paths.py` picks a writable
runtime root outside the repo, creates the directories that generated state needs,
and writes files atomically.

The repository stays the source of truth for checked-in inputs (for dispatch:
`14_context/dispatch/schedules.json` and the report templates). Reports, artifacts,
evidence and logs are generated state and live under the runtime root.

## Root selection

Candidates are tried in order. The first one that accepts a real probe file wins;
the probe file is created and then deleted, so writability is proven, never assumed.

| Order | Source | Location |
|-------|--------|----------|
| 1 | `env` | the `GHOTI_RUNTIME_ROOT` environment variable |
| 2 | `localappdata` | the per-user local application data folder, `Ghoti/AI_Managed_Only` |
| 3 | `temp` | the per-user temporary folder, `Ghoti/AI_Managed_Only` |

No candidate needs administrator rights. `select_runtime_root()` always reports the
selected source and one `{source, path, reason}` entry for every rejected candidate,
so a fallback is never silent.

`GHOTI_RUNTIME_ROOT` is the only environment variable this module reads, and the
runtime root is the only environment-derived value it reports.

## Layout under the runtime root

The runtime root mirrors the repository layout, so a path reported inside a
generated file can stay repo-relative and never leaks an absolute user path.

```
<runtime_root>/14_context/dispatch/outbox/<schedule_id>/<YYYY-MM-DD>.md
<runtime_root>/14_context/dispatch/artifacts/<artifact_id>.latest.json
<runtime_root>/14_context/dispatch/evidence/<schedule_id>/<YYYY-MM-DD>.json
<runtime_root>/05_logs/
```

## API

| Function | Returns |
|----------|---------|
| `get_runtime_root(root=None)` | `Path` to the runtime root |
| `get_dispatch_runtime_root(runtime_root=None)` | `Path` to `14_context/dispatch` under the root |
| `get_dispatch_outbox_dir(runtime_root=None)` | `Path` to the generated reports |
| `get_dispatch_artifacts_dir(runtime_root=None)` | `Path` to the generated artifacts |
| `get_dispatch_evidence_dir(runtime_root=None)` | `Path` to the generated evidence |
| `get_logs_dir(runtime_root=None)` | `Path` to the runtime logs |
| `ensure_runtime_dirs(runtime_root=None)` | `ghoti_runtime_dirs/1`, idempotent |
| `write_text_atomic(path, content)` | `ghoti_runtime_write/1` |
| `write_json_atomic(path, payload)` | `ghoti_runtime_write/1` |
| `select_runtime_root()` | `ghoti_runtime_root/1` |
| `diagnose_write_access(repo_root=None, runtime_root=None)` | `ghoti_runtime_write_access/1` |

Every getter takes an optional root override, so a caller or a test can redirect
all runtime state to one directory.

## Atomic writes

`write_text_atomic` and `write_json_atomic` create the parent directory, write a
temporary file in that same directory, then `os.replace` it onto the target. A
partial file is never left behind: `write_json_atomic` serializes before it opens
anything, and a failed write removes its temporary file and returns `ok: false`
with the failure class instead of raising.

## Diagnosing a blocked repository

`diagnose_write_access()` reports `repo_writable`, `runtime_writable`, the selected
source, the rejected candidates, `cfa_suspected` and a remediation list.

`cfa_suspected` is true when the repository refuses a probe file while the runtime
root accepts one. That asymmetry is the signature of an operating-system folder
protection policy (on Windows, Defender Controlled Folder Access), which surfaces
as a misleading `FileNotFoundError` inside the protected tree. Dispatch keeps
working in that state because generated state is already outside the repository.

## Safety

- Local only. No network, no browser, no credentials, no outbound action.
- Reads exactly one environment variable and logs no other environment value.
- Python 3.11 standard library only.
