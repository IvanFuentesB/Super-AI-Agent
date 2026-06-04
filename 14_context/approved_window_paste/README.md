# Approved-window paste harness (N+6.20A)

The next step of the overnight operator loop. The N+6.19A overnight operator generates
prompt packets into `14_context/overnight_operator/outbox/`. This harness adds the
**approved-window** safety layer for getting a packet from the outbox onto the
clipboard - and, in a future guarded step, into an approved window - without ever
submitting.

## What it does today

1. **List visible windows** (read-only) with `ghoti_approved_window_detector.ps1`:
   process name + title + pid, plus which ones match the approved allowlist.
2. **Copy an outbox packet to the clipboard** on explicit command with
   `ghoti_approved_clipboard_paste.ps1 -CopyOnly`. The operator then pastes manually.
3. **Validate a paste target** against `approved_windows.example.json` with
   `-PasteApproved -TargetWindow <name>`. It refuses any window not on the allowlist.
4. **Status** with `ghoti_paste_status.py --json` and a one-command
   `check_approved_window_paste.ps1`.
5. **Collect manual outputs**: drop agent replies as files into
   `manual_output_drop/` and summarize them with `write_manual_output_summary.py`.

## What it does NOT do

- It does **not** paste into apps, press Enter, submit, or click coordinates.
- It does **not** control chat, browser, or agent windows (those are never approved).
- Live paste execution stays **disabled** behind `approved_window_paste_enabled`; the
  paste is the operator's manual Ctrl+V into a window they chose.

## Safety rules

- The paste input file must live under `14_context/overnight_operator/outbox/`.
- The harness rejects secret-shaped patterns in the input and never reads secret
  values.
- The paste wrapper defaults to a dry run. `-CopyOnly` copies only. `-PasteApproved`
  validates an allowlist match and then defers - it never performs a live keystroke
  paste in this milestone.

## Files

- `approved_windows.example.json` - the conservative allowlist template (no secrets).
- `paste_status_schema.json` - the status shape and safe posture.
- `manual_output_drop/README.md` - the drop folder for pasted agent outputs.
