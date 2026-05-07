# Prompt Bus Hardening — N+3.56-FIX

**Script**: `03_scripts/prompt_bus.py`

## What was verified in N+3.56-FIX

The `--allow-canonical-overwrite` protection is confirmed in place from N+3.51A. No changes needed.

## Overwrite protection behavior
- `--write-context-pack --target claude --apply` without `--allow-canonical-overwrite` → REFUSED if canonical prompt exists.
- `--write-context-pack --target claude --apply --allow-canonical-overwrite` → writes.
- `--dry-run` mode always safe (no writes).

## Context pack contents
Context packs include:
- git branch, HEAD, dirty state summary
- memory pointers (compact_memory/ files)
- next recommended actions
- bridge status
- Ruflo/Gemma status
- exact copy-paste commands

## Validation commands
```bash
python 03_scripts/prompt_bus.py --help
python 03_scripts/prompt_bus.py --status-json
python 03_scripts/prompt_bus.py --write-context-pack --target all --title n3-56-fix-smoke --include-status --include-memory --include-next-actions --dry-run
python 03_scripts/prompt_bus.py --write-context-pack --target claude --title should-refuse --include-status --apply
```

The last command must REFUSE (canonical prompt already exists).

## Safety
- No clipboard access.
- No automatic send.
- Overwrite of canonical prompt requires explicit flag.
- Outbox files unstaged by default.
