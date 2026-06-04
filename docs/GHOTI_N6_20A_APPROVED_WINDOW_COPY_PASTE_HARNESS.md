# Ghoti Approved-Window Copy/Paste Harness (N+6.20A)

The next safe step of the overnight operator loop. N+6.19A generates prompt packets
into `14_context/overnight_operator/outbox/`. N+6.20A adds the **approved-window**
layer: it can list visible windows, copy a packet to the clipboard on explicit
command, validate a paste target against an allowlist, and collect manually dropped
agent outputs - all without ever submitting.

## Important: this does not control apps yet

There is **no live app control** in this milestone. The harness does **not** paste
into apps, press Enter, submit, or click coordinates, and it never controls chat,
browser, or agent windows. The actual paste is the operator's **manual Ctrl+V** into a
window they chose. Live keystroke paste stays deferred behind
`approved_window_paste_enabled`.

## Tools

- `03_scripts/approved_window_paste/ghoti_approved_window_detector.ps1` - list visible
  windows (process name + title + pid) and mark approved-allowlist matches. Read-only.
- `03_scripts/approved_window_paste/ghoti_approved_clipboard_paste.ps1` - the paste
  wrapper. Defaults to a dry run; `-CopyOnly` copies the packet to the clipboard;
  `-PasteApproved -TargetWindow <name>` validates the allowlist match and then defers.
- `03_scripts/approved_window_paste/ghoti_paste_status.py --json` - read-only status.
- `03_scripts/approved_window_paste/check_approved_window_paste.ps1` - one-command check.
- `03_scripts/approved_window_paste/write_manual_output_summary.py` - summarize agent
  replies dropped into `14_context/approved_window_paste/manual_output_drop/`.

## Safety rules

- The paste input file must live under `14_context/overnight_operator/outbox/`; any
  other path is refused.
- The harness rejects secret-shaped patterns in the input and never reads secret
  values.
- `-PasteApproved` refuses any window not on the conservative allowlist
  (`14_context/approved_window_paste/approved_windows.example.json`). Chat, browser,
  and agent windows are never approved.
- Every subprocess is an argument list - no shell string, no interpolated PowerShell
  expression invocation. No Docker, no account login, no auto-send.

## Useful commands

```
powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/ghoti_approved_window_detector.ps1
powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/ghoti_approved_clipboard_paste.ps1 -InputFile 14_context/overnight_operator/outbox/latest_prompt_packet.md -DryRun
python 03_scripts/approved_window_paste/ghoti_paste_status.py --json
powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/check_approved_window_paste.ps1
```

## What stays disabled

Live keystroke paste, Enter/submit, mouse clicks, app/window control, auto-submit,
account login, email/WhatsApp, Docker, and any unattended live agent loop are all
disabled. Fully unattended overnight operation remains blocked until approved-window
detection, a clipboard guard, a kill switch, no overlapping worktrees, auto-stop on
errors, logs, and no auto merge/push are all in place.

## Next milestone

A future milestone may enable a single, guarded, operator-confirmed keystroke paste
into one approved, visible window (still no Enter, still no submit) behind
`approved_window_paste_enabled`. The Agent Arena swarm **simulator** (N+6.21A,
simulation-first) is planned separately in
`docs/GHOTI_AGENT_ARENA_SWARM_SIMULATOR_PLAN.md`.
