# Ghoti Memory and Handoffs -- How They Connect

**Status:** Working local MVP (supervised; all relays are copy-paste only)

---

## Summary

Ghoti's memory is a set of repo-local markdown and JSON files with one
canonical core (compact memory), one rebuildable snapshot (the context pack),
and one human-curated layer (the Obsidian vault). The Agent OS reads all of
them through a single search interface that returns compact `path:line`
pointers, never file bodies. Handoffs between agents travel over copy-paste
buses: the prompt bus, relay pairs, the Hermes vault, and the new agent OS
packets. No bus delivers anything automatically - every packet says
`Human copy-paste required: YES` and `relay_mode: copy_paste_only`.

## Memory layers

| Layer | Location | Owner | Notes |
|-------|----------|-------|-------|
| Canonical compact memory | `14_context/compact_memory/*.md` | Human + agents (curated) | The durable core: working summary, next step, decisions, blockers |
| Generated memory | `14_context/compact_memory/generated/` | Machine-owned | Status shorts, migration summaries, the context pack; regenerated, not hand-edited |
| Context pack | built by `03_scripts/ghoti_context_pack_builder.py` -> `14_context/compact_memory/generated/ghoti_current_context_pack.{json,md}` | Machine-owned | One rebuildable snapshot with `generated_at` and `main_hash` |
| Obsidian vault | `14_context/obsidian_vault/` | Human-curated | Start note: `14_context/obsidian_vault/00_Index.md` |
| Repo knowledge | `14_context/repo_knowledge/generated/` | Machine-owned | Generated repo context summaries |

## Memory search (read-only, pointer-only)

```bash
python 03_scripts/agent_os/ghoti_agent_os.py --search-memory <term> --json
```

The search scans exactly these repo-local roots:

- `14_context/compact_memory`
- `14_context/obsidian_vault`
- `14_context/repo_knowledge/generated`
- `docs`

It returns compact pointers - repo-relative `path`, `line`, and a short
ASCII snippet, one hit per file - and never returns file bodies. That keeps
results safe to embed in handoff packets without leaking whole documents.
Search terms are restricted to 1-64 characters of letters, digits, space,
`_`, `.`, and `-`.

The suggestion-only worker uses the same sources: every plan and suggestion
it writes includes a "Memory pointers (verified local sources)" section
derived from the compact memory status files and the vault index.

## Handoff buses

| Bus | Location | Direction | Honesty label |
|-----|----------|-----------|---------------|
| Prompt bus (primary) | `14_context/prompt_bus/outbox/` | Ghoti -> human -> agent | copy-paste only |
| Relay pairs | `14_context/agent_relay/pairs/` | Paired agent lanes | copy-paste only |
| Hermes vault | `14_context/agent_handoff_vault/02_Agent_Handoffs/` | Coordinator notes | copy-paste only |
| Agent OS packets (new) | `14_context/agent_os/handoffs/` | Worker suggestions + per-target prompts | copy-paste only |

### Agent OS packets

`--worker-suggest <id>` writes a worker suggestion (`worker_suggestion_*.md`
plus `.json`): the rendered plan, the memory pointers it read, related memory
hits, and an explicit statement that no command was executed.

`--build-handoff --workflow <id>` writes three copy-paste packets:

- `handoff_claude_*.md` - implementation lane prompt
- `handoff_codex_*.md` - audit lane prompt (findings only, change nothing)
- `handoff_hermes_*.md` - coordinator status note for the handoff vault

Every packet ends with:

```
Human copy-paste required: YES
relay_mode: copy_paste_only
```

That is literal: Ghoti writes the file, you open it, you paste it into the
target tool yourself. There is no automatic delivery, no API call, and no
background watcher acting on these directories.

## How a typical loop runs

1. `--status --json` shows memory state: canonical file count, context pack
   freshness (`generated_at`, `main_hash`), vault note count, and the latest
   packets on each bus.
2. `--search-memory <term>` finds where something is recorded; you open the
   pointed-to file at the pointed-to line.
3. `--worker-suggest <workflow>` turns memory plus a template into a
   proposal you can read in one screen.
4. `--build-handoff --workflow <id>` produces the packets; you paste the
   right one into Claude, Codex, or the Hermes vault.
5. The receiving lane does its work; durable results get written back into
   canonical compact memory or the vault by whoever holds that lane's lock
   (`14_context/agent_lanes/active_locks.jsonl`).

## What this system does not do

It does not send messages between agents, does not sync to any cloud, does
not index file contents into an external database, and does not let the
worker edit canonical memory: the worker writes only under
`14_context/agent_os/` (plus any repo-local directory a human explicitly
lists in `14_context/agent_os/APPROVED_ACTIONS.json`).
