# Screenpipe Local Screen/Memory Capture Plan

**Status label:** `retention_plan / local_only / not_runtime_wired`

---

## Purpose

Screenpipe is a local screen and audio memory capture tool. For Ghoti, it provides:
- **Operator observation:** the operator can replay what Ghoti (or any visible desktop session) did recently.
- **Debugging:** screen frames and transcripts help reconstruct task context after failures.
- **Future integration path:** compact screen-state summaries could feed into ActionIntent payloads as evidence that an action was completed.

Screenpipe is **not wired into Ghoti runtime in this milestone**. No capture is started automatically. The operator must explicitly enable it.

---

## Default Configuration

| Setting | Default |
|---------|---------|
| `enabled` | `false` |
| `retention_days` | `3` |
| `dry_run_default` | `true` |
| `capture_mode` | operator-started only |
| `storage` | local paths only (see `screenpipe_retention_policy.example.json`) |

---

## Sensitive App Rules

The following must never be captured under any configuration:

- Banking or financial account screens
- Password entry fields or password manager windows
- 2FA prompts or authenticator apps
- Private documents (legal, medical, personal finance)
- Any screen containing credentials or session tokens

These exclusions apply even if the operator enables capture. The retention cleanup script (`03_scripts/screenpipe_retention_cleanup.ps1`) does not override these rules.

---

## Retention and Storage

- Default retention: **3 days**.
- All capture data stored under allowed roots only:
  - `C:/Users/ai_sandbox/Documents/AI_Managed_Only/output/screenpipe`
  - `C:/Users/ai_sandbox/Documents/AI_Managed_Only/05_logs/screenpipe`
- Cleanup script runs dry-run by default; requires `-Execute` flag to actually delete.
- Cleanup must not touch `14_context/`, `01_projects/`, or any repo root directory.

---

## Future Dashboard Integration

When wired, the dashboard should show:
- Capture status: `disabled / running / paused`
- Active retention policy summary
- Last cleanup run timestamp and file count
- Link to captured session artifacts

Not implemented in this milestone.

---

## Runtime Wiring Truth

| Fact | Value |
|------|-------|
| Screenpipe installed | unknown — not checked; evaluation only |
| Capture running | NO |
| Runtime wired | NO |
| Audit trail | NO |
| Operator can start | NO — requires future wiring milestone |

---

## Future Wiring Steps (not in this milestone)

1. Confirm Screenpipe repo and license.
2. Install Screenpipe to isolated local path with operator approval.
3. Define CapabilityAdapterDescriptor for screen-capture actions.
4. Wire `screenpipe_start` and `screenpipe_stop` as ActionIntent-gated commands.
5. Add dashboard status route for capture state.
6. Validate retention cleanup script against real capture output before enabling.
7. Ensure sensitive window exclusion rules are enforced at the adapter level.
