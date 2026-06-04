# Next task: Approved-window paste

Status-only handoff for the N+6.20A approved-window paste harness. It authorizes no
live app control, no submit, no Enter keystroke, and no secrets in the repo.

## Where things stand

- The harness can list visible windows (read-only), copy an outbox packet to the
  clipboard on explicit command, validate a paste target against a conservative
  allowlist, and summarize manually dropped agent outputs.
- It does **not** paste into apps, press Enter, submit, or click. Live keystroke paste
  is deferred behind `approved_window_paste_enabled`. The operator pastes manually with
  Ctrl+V.

## Useful commands

```
powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/ghoti_approved_window_detector.ps1
powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/ghoti_approved_clipboard_paste.ps1 -InputFile 14_context/overnight_operator/outbox/latest_prompt_packet.md -DryRun
python 03_scripts/approved_window_paste/ghoti_paste_status.py --json
powershell -ExecutionPolicy Bypass -File 03_scripts/approved_window_paste/check_approved_window_paste.ps1
```

## Suggested next step (when approved)

- A single, guarded, operator-confirmed keystroke paste into one approved, visible
  window (still no Enter, still no submit), behind `approved_window_paste_enabled`.
- Or start the Agent Arena swarm **simulator** (N+6.21A, simulation-first) per
  `docs/GHOTI_AGENT_ARENA_SWARM_SIMULATOR_PLAN.md`.

## Out of scope / still disabled

Live keystroke paste, Enter/submit, mouse clicks, app/window control, auto-submit,
account login, email/WhatsApp, Docker, and any unattended live agent loop remain
disabled. No secrets are stored in the repo.
