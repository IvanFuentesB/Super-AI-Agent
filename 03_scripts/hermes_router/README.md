# Hermes Router Wrappers (`03_scripts/hermes_router/`)

These are the **only** approved ways for Hermes (the local coordinator) to act.
Hermes runs **approved wrappers only** and **never runs arbitrary commands**.

## Safety model

- **Dry-run / read-only by default.** Wrappers that can write require an explicit
  `-AllowWrite` switch; with no switch they preview and write nothing.
- **Bounded.** Wrappers operate only inside the repo root and the Obsidian vault
  (`14_context/agent_handoff_vault/`). `write_handoff_note.ps1` is confined to
  `04_Logs/`, sanitizes the filename, and refuses any path outside that folder.
- **No arbitrary command execution.** No `Invoke-Expression`, no pass-through shell.
- **No launches.** No wrapper starts Claude, Codex, a browser, or any process.
- **No network.** No wrapper makes outbound calls. `run_gemma_summary.ps1` names a
  loopback endpoint for documentation only and never contacts it.
- **No secrets.** Wrappers never read or write tokens, `.env`, cookies, or auth files.
- **JSON out.** Each wrapper prints a single JSON object describing what it did/would
  do, including `live_action: false` and `local_only: true`.

## Wrappers

| Wrapper | Mode | Purpose |
|---------|------|---------|
| `read_current_task.ps1` | read-only | Read the current classified task from the vault. |
| `write_handoff_note.ps1` | dry-run (`-AllowWrite` to write) | Prepare a handoff note under `04_Logs/`. |
| `prepare_claude_prompt.ps1` | dry-run (`-AllowWrite` to write) | Assemble a Claude implementation prompt. Never launches Claude. |
| `prepare_codex_audit.ps1` | dry-run (`-AllowWrite` to write) | Assemble a Codex audit prompt. Never launches Codex. |
| `collect_agent_outputs.ps1` | read-only | Summarize the agent output logs for a human. |
| `run_gemma_summary.ps1` | dry-run only | Describe the local Gemma summary that would be requested. No model call. |
| `hermes_router_status.ps1` | read-only | Report foundation state and standing safety flags. |

## What is NOT enabled here

- **No Telegram.** **No browser/computer-use.** **No MCP installed.**
- No autonomous agent launch (launch designs are a later, separately-approved
  milestone and remain dry-run).
- No external repo clone/install/run. No live account/API/posting/money action.

## Usage

```powershell
powershell -ExecutionPolicy Bypass -File 03_scripts/hermes_router/hermes_router_status.ps1
powershell -ExecutionPolicy Bypass -File 03_scripts/hermes_router/read_current_task.ps1
powershell -ExecutionPolicy Bypass -File 03_scripts/hermes_router/write_handoff_note.ps1 -Title "my_note" -Body "text"   # dry-run
```
