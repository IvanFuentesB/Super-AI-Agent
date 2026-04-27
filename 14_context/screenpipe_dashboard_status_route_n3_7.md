# Screenpipe Dashboard Status Route — N+3.7

**Date:** 2026-04-27
**Milestone:** N+3.7 PATH B
**Branch:** `feat/ghoti-visible-operator-stack`

---

## Route Added

```
GET /api/ghoti/screenpipe/status
```

Implemented in: `01_projects/dashboard_mvp/server.js`

---

## What the Route Does

- Reads `23_configs/screenpipe_retention_policy.example.json` if it exists
- Checks file-system existence of `output/screenpipe` and `05_logs/screenpipe` paths
- Returns a JSON status document with `capture_started: false` and `deletion_performed: false` always set

## What the Route Does NOT Do

- Does NOT start Screenpipe
- Does NOT capture screenshots or audio
- Does NOT read or serve screenshot/audio files
- Does NOT delete anything
- Does NOT call any external service

---

## Response Fields

| Field | Value / Source |
|-------|----------------|
| `ok` | true |
| `capture_started` | false (always) |
| `runtime_wired` | false (always) |
| `retention_days` | from policy JSON or null |
| `dry_run_default` | from policy JSON or null |
| `policy_file_exists` | bool — `23_configs/screenpipe_retention_policy.example.json` |
| `cleanup_script_exists` | bool — `03_scripts/screenpipe_retention_cleanup.ps1` |
| `allowed_roots` | array from policy JSON or [] |
| `output_screenpipe_exists` | bool — `output/screenpipe` dir existence |
| `output_screenpipe_file_count` | int — count of entries in that dir, not file contents |
| `logs_screenpipe_exists` | bool — `05_logs/screenpipe` dir existence |
| `logs_screenpipe_file_count` | int — count of entries in that dir, not file contents |
| `deletion_performed` | false (always) |
| `updated_at_utc` | ISO timestamp of response |

---

## Expected Response (current environment)

```json
{
  "ok": true,
  "capture_started": false,
  "runtime_wired": false,
  "retention_days": 3,
  "dry_run_default": true,
  "policy_file_exists": true,
  "cleanup_script_exists": true,
  "allowed_roots": [
    "C:/Users/ai_sandbox/Documents/AI_Managed_Only/output/screenpipe",
    "C:/Users/ai_sandbox/Documents/AI_Managed_Only/05_logs/screenpipe"
  ],
  "output_screenpipe_exists": false,
  "output_screenpipe_file_count": 0,
  "logs_screenpipe_exists": false,
  "logs_screenpipe_file_count": 0,
  "deletion_performed": false,
  "updated_at_utc": "..."
}
```

---

## UI Card

No UI card added to `public/app.js` in this milestone. The route is documented here and verified via `node --check` and direct curl/fetch. A dashboard card can be added in a later milestone when the operator confirms the route is useful.

---

## Related Files

- `23_configs/screenpipe_retention_policy.example.json` — policy source
- `03_scripts/screenpipe_retention_cleanup.ps1` — cleanup script (read-only check only)
- `14_context/screenpipe_local_capture_plan.md` — full retention plan
- `14_context/obsidian_vault/04_Tools.md` — tool status
