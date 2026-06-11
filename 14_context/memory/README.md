# Ghoti Context Memory

This folder is Ghoti's source-linked, repo-local memory pointer layer.

It does not replace durable truth in existing context files. The generator
indexes a reviewed allowlist in place, records SHA-256 hashes, and emits small
startup maps so agents can load only the context needed for a task.

## Commands

```powershell
python 03_scripts/context_memory/ghoti_context_memory_map.py --check --json
python 03_scripts/context_memory/ghoti_context_memory_map.py --write --json
python 03_scripts/context_memory/ghoti_context_memory_map.py --verify --json
python 03_scripts/context_memory/ghoti_context_memory_map.py --index-json --json
```

## Outputs

- `generated/context_map.md`: bounded source directory with hashes.
- `generated/latest_state.md`: compact source-linked startup packet.
- `index/raw_index.json`: machine-readable source registry and hashes.
- `schemas/raw_index.schema.json`: raw index data contract.

## Safety Contract

- Source files are read-only and are never deleted or overwritten.
- All indexed paths are repo-relative.
- Unsafe source content is indexed as metadata only and never summarized.
- No secrets, private paths, browser data, account data, or credentials.
- No network, models, providers, command execution, or live actions.
- Generated memory is a pointer layer, not canonical truth.
- Vector search may be added later only as a disposable search aid.

## Existing Memory Compatibility

N+6.42A indexes selected durable files from:

- `14_context/00_main_memory/`
- `14_context/compact_memory/`
- `14_context/agent_handoff_vault/`
- `14_context/obsidian_vault/`

Those folders remain in place. No automatic migration occurs in this milestone.
