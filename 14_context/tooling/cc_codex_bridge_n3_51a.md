# CC/Codex Bridge — N+3.51A

Generated: 2026-05-06

## Summary

Local file-based handoff bridge for Claude/Codex/ChatGPT coordination.

**CC/Codex automatic = NO.** This is a copy-paste friction reducer, not automation.

## Commands Run

```powershell
python 03_scripts/cc_codex_bridge.py --help
python 03_scripts/cc_codex_bridge.py --status
python 03_scripts/cc_codex_bridge.py --write-pair --title n3-51-smoke --body "..." --dry-run
python 03_scripts/cc_codex_bridge.py --write-pair --title n3-51-smoke --body "..." --apply
python 03_scripts/cc_codex_bridge.py --next --dry-run
python 03_scripts/cc_codex_bridge.py --verify
```

## Status

| Item | Value |
|------|-------|
| Bridge dirs | ALL CREATED (`14_context/bridge/{inbox,outbox,archive,status}`) |
| Outbox files (smoke) | 3 (claude, codex, chatgpt handoffs) |
| CC/Codex automatic | NO |
| Clipboard | NO |
| API calls | NO |
| Human paste required | YES |

## Automation State

- `--status`: PASS
- `--write-pair --dry-run`: PASS (previews files, no write)
- `--write-pair --apply`: PASS (writes to bridge outbox)
- `--next --dry-run`: PASS (shows next paste action)
- `--verify`: PASS (all dirs exist, files readable)
- `--archive-done --dry-run`: available

## What Is Automated

- Writing handoff prompt files to `14_context/bridge/outbox/`
- Verifying bridge directory structure
- Listing pending outbox files
- Archiving done files (manual trigger)

## What Remains Manual

- Opening outbox files and pasting content into Claude/Codex/ChatGPT
- Deciding which AI tool receives which handoff
- Any response from the target AI

## Bridge Dirs

```
14_context/bridge/
14_context/bridge/inbox/
14_context/bridge/outbox/
14_context/bridge/archive/
14_context/bridge/status/
```

## Next Step

Run `--write-pair --apply` to generate handoff files, then open each file and paste into the target AI manually.
