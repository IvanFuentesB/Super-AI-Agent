# Next Hermes Status Task

Milestone source: N+6.25A Hermes memory/status upgrade (read-only coordinator packet).

## What N+6.25A produced

- `03_scripts/hermes_status/ghoti_hermes_status_packet.py` - a read-only generator that
  reads committed status sources + read-only git metadata and emits a Markdown/JSON packet
  Hermes reads before answering.
- A PowerShell check, a JSON schema, a static example packet, and a folder README.
- The packet states plain-English status with percentages, what is done/blocked/parallel,
  what Hermes must not claim, ECC = Everything Claude Code, and Hermes's current vs future
  role.

## The next step (gated, human-approved)

The next step toward automatic coordination is the **controlled launcher** - the first
time Ghoti actually launches/coordinates agents:

`simulation -> trace ingestion -> static repo intake -> hermes status/memory (done) -> controlled launcher (NEXT) -> approved-window bridge -> supervised overnight loop`

A controlled-launcher milestone must:

- Be **dry-run-first**: print the exact command(s) it would run, then stop. No real launch
  until a separate human approval.
- Reuse this packet as Hermes's grounding before it coordinates anything.
- Use one agent per task on its own branch/worktree; no overlapping edits.
- Keep every hard limit: no installs, no MCP, no browser/computer-use, no auto-submit, no
  secrets, no live account/API/money actions.

## Improvements to consider for the packet (still read-only)

- Read the Agent Arena trace status live via the trace loader (read-only) instead of the
  sample only, once stable.
- Add a "lane locks" summary from `14_context/agent_lanes/` (read-only).
- Keep paths repo-relative and never embed absolute local paths or usernames.

## Do not

- Do not enable live launching, MCP, browser/computer-use, or auto-submit in this packet.
- Do not write outside the repo root; keep `--write` repo-bounded.
- Do not record secrets, tokens, or real local paths in the committed example/schema/docs.
