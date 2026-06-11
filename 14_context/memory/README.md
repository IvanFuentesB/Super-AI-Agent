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
python 03_scripts/context_memory/ghoti_handoff_packet.py --check --json
python 03_scripts/context_memory/ghoti_handoff_packet.py --validate 14_context/memory/examples/agent_handoff_packet.example.json --json
python 03_scripts/context_memory/ghoti_handoff_packet.py --write <repo-relative-packet.json> --json
python 03_scripts/context_memory/ghoti_handoff_packet.py --deliver <packet-id> --to-agent hermes --json
python 03_scripts/context_memory/ghoti_handoff_packet.py --reindex --json
python 03_scripts/context_memory/ghoti_handoff_packet.py --verify --json
```

## Outputs

- `generated/context_map.md`: bounded source directory with hashes.
- `generated/latest_state.md`: compact source-linked startup packet.
- `index/raw_index.json`: machine-readable source registry and hashes.
- `schemas/raw_index.schema.json`: raw index data contract.
- `index/handoff_index.json`: hash-linked packet and delivery registry.
- `schemas/agent_handoff_packet.schema.json`: shared packet contract.
- `agent_handoffs/<agent>/outbox/`: immutable packets written by that agent.
- `agent_handoffs/<agent>/inbox/`: read-only delivery pointers addressed to that agent.
- `obsidian/START_HERE.md`: generated Obsidian-compatible navigation entry point.
- `index/obsidian_view_index.json`: deterministic hashes for generated Obsidian views.

## Obsidian View

Open `14_context/memory/` as a local Obsidian vault, then start at
`obsidian/START_HERE.md`. The pages under `obsidian/` are generated pointers,
not canonical truth. They link back to the source indexes, durable files, and
handoff packets. Do not commit `.obsidian` workspace state, plugin caches, or
machine-specific settings.

```powershell
python 03_scripts/context_memory/ghoti_obsidian_memory_view.py --check --json
python 03_scripts/context_memory/ghoti_obsidian_memory_view.py --write --json
python 03_scripts/context_memory/ghoti_obsidian_memory_view.py --verify --json
```

## Safety Contract

- Source files are read-only and are never deleted or overwritten.
- All indexed paths are repo-relative.
- Unsafe source content is indexed as metadata only and never summarized.
- No secrets, private paths, browser data, account data, or credentials.
- No network, models, providers, command execution, or live actions.
- Generated memory is a pointer layer, not canonical truth.
- Vector search may be added later only as a disposable search aid.
- Commands inside handoff packets are audit evidence only and are never executed.
- A sender writes only to its own outbox; delivery creates an immutable hash-linked inbox pointer.
- Published packet IDs are append-only. Corrections require a new packet ID.
- Packet size and rendered Markdown are bounded to reduce repeated context and token use.

## Hash Contract

Indexes use `sha256_canonical_text_lf_binary_raw`. Text files are normalized to
LF line endings before hashing so the same committed content verifies across
Windows and Unix checkouts. Binary files are hashed as raw bytes.

## Existing Memory Compatibility

N+6.42A indexes selected durable files from:

- `14_context/00_main_memory/`
- `14_context/compact_memory/`
- `14_context/agent_handoff_vault/`
- `14_context/obsidian_vault/`

Those folders remain in place. No automatic migration occurs in this milestone.
