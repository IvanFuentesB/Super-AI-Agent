# Ghoti N+6.23A - Agent Arena Real Trace Ingestion + Memory Vault Status View

## Summary

N+6.23A upgrades the visual **Agent Arena** so it can show a **real local project trace**
built from existing report files, not only the sample simulation. It adds a read-only
trace loader, two new read-only GET endpoints, a sample/trace **view toggle**, and a row
of **status cards** for the current project state.

The arena stays simulation-first and safe by construction. Nothing here controls an
agent or executes a command:

- **Read-only and file-only.** The loader reads existing committed report files only. It
  runs no command (no `subprocess`), opens no network connection, and writes nothing.
- **Loopback-only.** The server still binds `127.0.0.1` only; there is no option to bind
  an external address.
- **GET-only.** No `do_POST` handler exists, so every non-GET method is rejected.
- **`simulation` and `live_execution` are always `false`** in the trace payload.
- No secret value and no absolute local path is surfaced - report paths are made
  repo-relative.

## What was added

| Piece | Path | Role |
|-------|------|------|
| Trace loader | `03_scripts/agent_arena/ghoti_agent_arena_trace_loader.py` | Read-only, file-only loader: parses recent reports into Agent Arena trace format and builds the status cards. |
| Trace schema | `14_context/agent_arena/trace_schema.json` | Shape + safety posture of the `/api/trace` payload. |
| Sample trace | `14_context/agent_arena/sample_trace.json` | Illustrative fallback used only when no local reports are found. |
| Server endpoints | `03_scripts/agent_arena/ghoti_agent_arena.py` | New `GET /api/trace` and `GET /api/trace-status`, plus trace keys in `--check`. |
| Static UI | `03_scripts/agent_arena/static/{index.html,app.js,styles.css}` | Buttons-only view toggle + status-cards section. |

## Trace loader

The loader reads recent committed reports under `14_context`
(`claude_n6_*.md`, `codex_n6_*.md`) and the agent handoff vault. For each report it
extracts, **without reading any secret and without running git**:

- milestone (from the filename),
- title (first heading),
- verdict (`IMPLEMENTED_AND_PUSHED` / `CLEAN_PASS` / `BLOCKED` / `recorded`),
- feature branch (`feat/ghoti-agent-...`) and Codex audit target (`audit/ghoti-agent-codex-...`),
- the `origin/main` short commit **as recorded in the newest report text** (this is a
  file read, not a live git read),
- the agent (from the filename prefix), and the repo-relative report path.

It is bounded: candidates are sorted by milestone from the filename (no read) and only the
newest ~25 are parsed.

CLI:

```
python 03_scripts/agent_arena/ghoti_agent_arena_trace_loader.py --check        # safety self-check
python 03_scripts/agent_arena/ghoti_agent_arena_trace_loader.py --trace-json   # the local trace
python 03_scripts/agent_arena/ghoti_agent_arena_trace_loader.py --status-json  # just the status cards
```

## Endpoints

| Route | Returns |
|-------|---------|
| `GET /api/simulation` | The sample simulation (unchanged). |
| `GET /api/trace` | The real local trace built read-only from report files. |
| `GET /api/trace-status` | Just the status cards. |

`GET /api/trace` and `GET /api/trace-status` are read-only. The server exposes no POST
route; a POST to any path is rejected by the standard library.

## Status cards

The **Local trace** view shows status cards derived read-only from the most recent
reports and from simple file-presence checks:

1. **Latest main commit (recorded)** - the `origin/main` short commit recorded in the
   newest local report (file-only, not a live git read).
2. **Latest Claude branch** - the newest `feat/ghoti-agent-claude-...` branch, with its milestone.
3. **Latest Codex audit** - the newest `audit/ghoti-agent-codex-...` target.
4. **Memory vault** - `present` / `missing` from a read-only check for
   `14_context/memory_vault/README.md`.
5. **Tool intake** - `present` / `missing` from a read-only check for the tool intake
   inventory JSON.

The memory-vault and tool-intake cards are **presence checks only**. Those areas are
owned by a separate lane; this milestone never edits them. When that lane has not yet
merged, both cards read `missing`, which is correct.

## View toggle

The page header has a buttons-only toggle: **Sample simulation** and **Local trace**.
The control only switches which read-only endpoint is read and re-renders; it launches
nothing, submits nothing, and posts nothing. There is no `<form>` on the page.

## Run it

```
# Safety self-check (no server):
python 03_scripts/agent_arena/ghoti_agent_arena.py --check

# Start the local-only server, then open the printed 127.0.0.1 URL:
python 03_scripts/agent_arena/ghoti_agent_arena.py --serve
```

Paths in this document are placeholders (`<repo>`, `<worktree>`); no real local path,
username, secret, or token is recorded here.

## Safety summary

- No command execution, no `subprocess`, no shell, no `os.system`.
- No file writes from the loader or the dashboard; no runtime-config mutation.
- Loopback-only server; GET-only; no POST routes; no external CDN/assets; no live socket.
- `simulation` and `live_execution` forced `false`; no agent is launched or controlled.
- No secrets and no absolute local paths surfaced.

## Relationship to N+6.21A

N+6.21A delivered the simulation-only arena and named "real trace ingestion" as a later
milestone. N+6.23A is that later milestone, added as a read-only extension that leaves
the simulation view and the loopback-only safety posture intact.
