# N+3.7 Codex Screenpipe Route Review

Status: route_review / read_only / no_capture / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack

## Reviewed Route Proposal

```text
GET /api/ghoti/screenpipe/status
```

This route should be implemented as a read-only status surface. It should not start Screenpipe, read screenshot/audio contents, serve media, upload data, or delete files.

## Required Route Behavior

The route should report policy and file-count truth only:

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
  "warning": null
}
```

Exact field values should come from the existing retention config and safe local file checks.

## Must Not Do

- Must not start screen capture.
- Must not start audio capture.
- Must not read or serve screenshots.
- Must not read or serve audio.
- Must not run OCR.
- Must not upload data.
- Must not delete files.
- Must not expose arbitrary paths.
- Must not claim Screenpipe is running unless positively detected.
- Must not weaken any ActionIntent or approval gate.

## Retention Policy Truth

The current Screenpipe direction should preserve a 3-day retention default. Cleanup should remain dry-run by default, and destructive cleanup must require a separate explicit operator action in a later milestone.

Deletion boundaries should remain limited to approved capture roots. The route should report missing folders as warnings rather than creating, scanning outside, or deleting anything.

## Why This Is The Safest Next Implementation

If Docker is not approved, this route gives immediate operator value without installs. It helps the dashboard show local capture readiness, retention policy, and cleanup risk while keeping capture disabled and operator-controlled.

## Recommended Next Implementation

N+3.8 should implement Screenpipe status route + dashboard read model if Docker is not approved. It should validate:

- `node --check` for dashboard server/app/overlay files.
- Route returns 200 JSON.
- Missing capture folder produces a warning, not a crash.
- No screenshot/audio contents are exposed.
- No cleanup executes.
