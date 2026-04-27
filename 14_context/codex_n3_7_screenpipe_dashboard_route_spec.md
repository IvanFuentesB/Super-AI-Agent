# Codex N+3.7 Screenpipe Dashboard Route Spec

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Status label: route_spec_only / read_only_dashboard / no_capture / not_runtime_wired

## Goal

Specify a safe next implementation milestone for Screenpipe visibility without starting capture, OCR, audio processing, uploads, or deletion.

Recommended route:

`GET /api/ghoti/screenpipe/status`

## Route Requirements

The route should be local-only and read-only. It should never start Screenpipe, never capture frames/audio, never delete files, and never expose image contents.

Suggested response shape:

```json
{
  "ok": true,
  "capture_enabled": false,
  "capture_running": false,
  "retention_days": 3,
  "dry_run_default": true,
  "allowed_roots": [],
  "latest_cleanup_check_utc": null,
  "total_capture_files": 0,
  "oldest_capture_age_hours": null,
  "files_over_retention_count": 0,
  "external_upload_enabled": false,
  "runtime_wiring_truth": "local_status_only",
  "warning": "capture folder missing"
}
```

## Field Semantics

| Field | Required behavior |
|---|---|
| `ok` | true if config/status can be read; false if parse/read fails |
| `capture_enabled` | false by default from config |
| `capture_running` | false unless positively detected |
| `retention_days` | read from `23_configs/screenpipe_retention_policy.example.json` or fallback to 3 |
| `dry_run_default` | read from config; should be true |
| `allowed_roots` | roots from config, normalized for display |
| `latest_cleanup_check_utc` | null unless a future cleanup status file exists |
| `total_capture_files` | count files if capture folder exists |
| `oldest_capture_age_hours` | null if no files/folder |
| `files_over_retention_count` | count files older than retention cutoff |
| `external_upload_enabled` | always false for this route |
| `runtime_wiring_truth` | `local_status_only` |
| `warning` | include if config/folder is missing or unreadable |

## Safety Constraints

Must not:

- start screen capture
- start audio capture
- run OCR
- read image contents
- serve screenshots
- upload anything
- delete anything
- run `screenpipe_retention_cleanup.ps1 -Execute`
- scan outside allowed roots
- expose private paths beyond configured roots and summary counts

## Cleanup Visibility

The dashboard may show:

- retention days
- dry-run default
- allowed roots
- files over retention count
- note that deletion requires explicit `-Execute`

It must not expose a "delete now" action in the first route milestone.

## Dashboard Copy

Recommended wording:

- "Screenpipe status is local-only and read-only."
- "Capture is disabled unless the operator explicitly starts it."
- "This panel does not start capture, OCR, audio, upload, or deletion."
- "Default retention: 3 days."

## Recommended Implementation Milestone

N+3.8 Screenpipe status route + dry-run cleanup visibility.

Acceptance criteria:

- `GET /api/ghoti/screenpipe/status` returns JSON.
- Route reads retention config.
- Route reports missing folders honestly.
- Route does not start capture or deletion.
- Dashboard displays status without screenshot contents.
- Node syntax checks pass.
- Runtime artifacts are not staged.
