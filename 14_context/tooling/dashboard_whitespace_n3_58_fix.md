# Dashboard Stability + Card Whitespace Fix — N+3.58-FIX

## Dashboard Stability Fix

### Problem

`_probe_obsidian()` was called bare in `_collect_status()`. If the obsidian probe
subprocess raised an exception (e.g. non-zero exit, JSON parse error, or a
PermissionError from the inline fallback), the entire dashboard crashed before
returning any output.

### Fix

Wrapped in `try/except Exception`:

```python
obsidian_probe_error = None
try:
    obsidian = _probe_obsidian()
except Exception as _obe:
    obsidian_probe_error = str(_obe)
    obsidian = {
        "vault": {
            "path": "14_context/obsidian_vault",
            "exists": _safe_exists(OBSIDIAN_VAULT_DIR),
            "md_file_count": ...,
            "required_files": {f: False for f in OBSIDIAN_VAULT_REQUIRED},
            "required_files_pass": False,
        },
        "app": {
            "exe_found": False,
            "exe_path": None,
            "winget_found": False,
            "winget_detail": None,
            "probe_error": obsidian_probe_error,
            "inaccessible_candidates": [],
        },
    }
```

`obsidian_probe_error` is included in the returned status dict so it appears in
`--json` and `--status` output. The dashboard never silently hides the failure.

A `_safe_exists` helper was also added to `ghoti_dashboard.py` for use in the
fallback block.

## Card Whitespace Normalization

### Problem

Python's `pathlib.Path.write_text(content, encoding='utf-8')` on Windows translates
`\n` to `\r\n` (CRLF) by default. `git diff --cached --check` interprets the `\r`
character as trailing whitespace and fails the check.

### Fix

Two changes in `ghoti_dashboard.py`:

1. **`_clean_markdown` helper** — strips trailing whitespace from every line and
   ensures a single trailing newline:

   ```python
   def _clean_markdown(text: str) -> str:
       return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
   ```

   Applied in `_render_card()`:
   ```python
   return _clean_markdown("\n".join(lines))
   ```

2. **`newline="\n"` in `_safe_write_text`** — forces LF-only file output:

   ```python
   dest.write_text(content, encoding="utf-8", newline="\n")
   ```

### Commands Used

```powershell
python 03_scripts/ghoti_dashboard.py --card --apply
git diff --check -- 14_context/ghoti_dashboard_card.md
git diff --cached --check
```

### Diff-Check Proof

After applying and staging:

```
git diff --check -- 14_context/ghoti_dashboard_card.md
# (no output — exit 0)

git diff --cached --check
# (no output — exit 0)
```

Both pass with exit code 0. No trailing whitespace warnings.
