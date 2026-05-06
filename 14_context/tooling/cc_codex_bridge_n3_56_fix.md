# CC/Codex Bridge — N+3.56-FIX

**Script**: `03_scripts/cc_codex_bridge.py`

## What changed in N+3.56-FIX

- Added `--init` mode (explicit bridge directory creation).
- Added `_print_truth_labels()` called in all command outputs.
- `--status` remains strictly read-only (no dir creation).

## Truth Labels (printed in every command)
```
CC/Codex automatic     : NO
Bridge type            : local manual file handoff
Clipboard              : NO
API calls              : NO
Auto-send              : NO
Human copy-paste required: YES
```

## Commands
```bash
python 03_scripts/cc_codex_bridge.py --help
python 03_scripts/cc_codex_bridge.py --status
python 03_scripts/cc_codex_bridge.py --init --dry-run
python 03_scripts/cc_codex_bridge.py --init --apply
python 03_scripts/cc_codex_bridge.py --write-pair --title smoke --body "test" --dry-run
python 03_scripts/cc_codex_bridge.py --write-pair --title smoke --body "test" --apply
python 03_scripts/cc_codex_bridge.py --verify
python 03_scripts/cc_codex_bridge.py --archive-done --dry-run
```

## What passes
- `--init --dry-run`: prints dirs, writes nothing. ✓
- `--init --apply`: creates all 5 bridge dirs. ✓
- `--status`: read-only, reports missing dirs. ✓
- `--write-pair --dry-run`: writes nothing, shows preview. ✓
- `--write-pair --apply`: writes handoff files to outbox. ✓
- Truth labels printed in every command. ✓

## What is NOT automatic
- CC/Codex control: NO
- Clipboard: NO
- API: NO
- Auto-send: NO
