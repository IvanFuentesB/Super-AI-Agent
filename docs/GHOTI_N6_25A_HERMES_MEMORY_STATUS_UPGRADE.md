# Ghoti N+6.25A - Hermes Memory/Status Upgrade + Automatic Coordinator Grounding

## Summary

N+6.25A gives Hermes a **reliable, read-only status/memory packet** it reads before
answering, so it stops giving shallow or incorrect summaries. It is the next step toward
automatic coordination - but there is **still no live agent launching**. The generator
reads existing committed status sources and read-only git metadata only; it launches
nothing and writes nothing unless explicitly told to.

## What it builds

| Piece | Path |
|-------|------|
| Generator | `03_scripts/hermes_status/ghoti_hermes_status_packet.py` |
| PowerShell check | `03_scripts/hermes_status/check_hermes_status_packet.ps1` |
| Packet schema | `14_context/hermes_status/hermes_status_packet_schema.json` |
| Example packet | `14_context/hermes_status/HERMES_STATUS_PACKET.example.md` |
| Folder README | `14_context/hermes_status/README.md` |

## Sources it reads (committed, read-only)

- latest main commit (read-only git metadata; `origin/main` preferred over a possibly
  stale local `main`)
- Agent Arena trace status (if present)
- Memory Vault index (if present)
- Tool Intake summary (if present)
- latest Claude report and latest Codex report (sorted by milestone, not alphabetically)
- feature-flags summary (the `*.example` flags file only - **no secrets**)

## What the packet contains

- **Plain-English status with percentages** (overall progression and a hard
  `live automation enabled: 0%`).
- The **N+ label plus its human meaning**.
- **What is done**, **what is blocked**, and **what can run in parallel**.
- **What Hermes should NOT claim** (no live launch, no MCP/browser/computer-use, no
  auto-submit, no overnight autonomy, and do not confuse ECC).
- **ECC = Everything Claude Code** (explicitly NOT elliptic curve cryptography).
- **Hermes role:** current = coordinator/status/memory only; future = automatic
  coordinator only after the controlled launcher and approval gates are built and audited.

## CLI

```
python 03_scripts/hermes_status/ghoti_hermes_status_packet.py --check --json   # safety self-check
python 03_scripts/hermes_status/ghoti_hermes_status_packet.py --json           # JSON packet
python 03_scripts/hermes_status/ghoti_hermes_status_packet.py --md             # Markdown packet
python 03_scripts/hermes_status/ghoti_hermes_status_packet.py --write \
  --output 14_context/hermes_status/HERMES_STATUS_PACKET_LAST_RUN.md --json     # write packet
powershell -ExecutionPolicy Bypass -File 03_scripts/hermes_status/check_hermes_status_packet.ps1
```

`--write` refuses any output path outside the repo root. The `HERMES_STATUS_PACKET_LAST_RUN.md`
output is a run artifact and is **not committed**.

## How to paste the packet into Hermes

1. Generate the latest packet:
   `python 03_scripts/hermes_status/ghoti_hermes_status_packet.py --write --output 14_context/hermes_status/HERMES_STATUS_PACKET_LAST_RUN.md`
2. Open `14_context/hermes_status/HERMES_STATUS_PACKET_LAST_RUN.md` and copy its contents.
3. At the **start** of a Hermes coordination session, paste the Markdown packet in as
   context and tell Hermes: "This is the current ground-truth status. Do not claim
   anything it marks blocked."
4. Hermes answers using the packet. It must not invent status, must not claim live agent
   launching, and must not confuse ECC (Everything Claude Code) with elliptic curve
   cryptography.

No auto-submit and no automatic pasting are involved - a human pastes the packet. This is
a status/memory grounding step, not a launcher.

## ECC

`ECC = Everything Claude Code` - a curated bundle of Claude Code commands/agents/skills/
hooks. It is **not** elliptic curve cryptography. Ghoti adapts the ideas as guidance only;
it does not install ECC or wire its hooks. The packet repeats this so Hermes never
confuses the two.

## Dependency note

- N+6.23B (Agent Arena trace ingestion) is on main; the packet reads that trace status.
- This lane does **not** edit `14_context/skills` or the N+6.24A swarm-intake files. (At
  the start of this milestone N+6.24B was not merged; per the rule those files were left
  untouched. They are read for status only, never edited.)

## Safety posture

Read-only. The only command run is read-only git (commit metadata). No installs, no
external repo execution, no MCP, no browser/computer-use, no live agent launching, no
auto-submit, no Docker, no secrets/tokens/cookies/auth files, no real local
paths/usernames/private images (the packet emits repo-relative paths and short commit
hashes only). It writes only when `--write` is passed, and then only inside the repo.

## Future role (automatic coordinator)

After the controlled launcher and approval gates are built and audited (dry-run first,
worktree-per-agent, human approval), Hermes can become an automatic coordinator that uses
this packet as its grounding. Until then it stays coordinator/status/memory only.
