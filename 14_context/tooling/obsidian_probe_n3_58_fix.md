# Obsidian Probe — N+3.58-FIX Hardening

## Problem

`obsidian_probe.py --status` and `--json` crashed with `PermissionError` on Windows.

When the script runs as `ai_sandbox`, accessing `C:\Users\Navif\AppData\Local\...`
raises `PermissionError` because the process does not have read permission to the
Navif user's AppData directory. The original code called `path.exists()` directly,
which propagated the exception.

## PermissionError Handling

Five safe helper functions added at module level:

```python
def safe_exists(path) -> bool
def safe_is_file(path) -> bool
def safe_glob_md(path) -> list
def safe_stat(path)
def safe_check_candidate(path) -> dict
```

Each wraps its operation in `except (PermissionError, OSError, FileNotFoundError)`
and returns a safe fallback (`False`, `[]`, `None`, or an error dict).

`safe_check_candidate` additionally catches `Exception` and returns:
```json
{"path": "...", "exists": false, "accessible": false, "error": "PermissionError: ..."}
```

## Status / JSON Behavior

### `--status`

- Prints vault and required-file state (using `safe_exists`).
- Prints each exe candidate with label `FOUND`, `not found`, or `INACCESSIBLE`.
- If any candidates were inaccessible, prints a `WARNING:` block.
- Does NOT crash.

### `--json`

Returns full probe result including:

```json
{
  "app": {
    "exe_candidates_checked": [...],
    "inaccessible_candidates": [...],
    ...
  },
  "probe_errors": [...]
}
```

`inaccessible_candidates` is a list of `safe_check_candidate` dicts where
`"accessible": false`. `probe_errors` is a list of human-readable warning strings.

## Inaccessible Candidate Handling

- Inaccessible candidates are never used as a positive exe match.
- They are recorded, not silently dropped.
- They appear in both `--status` output (warning block) and `--json` output.
- The probe continues to check remaining candidates even after an inaccessible one.

## Read-Only Proof

- No files are written by the probe.
- No subprocesses are launched except `winget --version` and `winget list` (read-only queries).
- No network calls.
- No Obsidian launch.
- `probe()` and both command handlers only call `subprocess.run` with `capture_output=True`.
