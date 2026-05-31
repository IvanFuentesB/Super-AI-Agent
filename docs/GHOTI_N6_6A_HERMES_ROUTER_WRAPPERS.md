# N+6.6A — Hermes Soul + Router Wrapper Foundation

Status: IMPLEMENTED (safe foundation). This milestone builds the first real, bounded
way for Hermes (the local coordinator) to act. It does **not** enable autonomy.

Author lane: implementation specialist (Claude Code). Codex audits next; a human merges.
Date: 2026-05-31

## 1. What this milestone is

Hermes is the **local coordinator and memory writer**, not the main brain. ChatGPT is
the main architect and planner. This milestone gives Hermes:

- a **soul / identity contract** (`HERMES_SOUL.md`) that fixes who Hermes is and is not,
- **status + routing memory** (`HERMES_CURRENT_STATUS.md`, `HERMES_ROUTER_POLICY.md`),
- a **coordinator summary** note (`04_Logs/HERMES_COORDINATOR_SUMMARY.md`),
- seven **approved PowerShell wrappers** in `03_scripts/hermes_router/` that are the
  *only* ways Hermes may act, and
- **tests** that lock the safety behavior so it cannot silently regress.

## 2. Wrappers-only rule

Hermes runs **approved wrappers only** and **never runs arbitrary commands**. There is
no general shell, no `Invoke-Expression` of caller input, no pass-through execution.
Every wrapper:

- is **dry-run / read-only by default** (writes require an explicit `-AllowWrite`),
- is bounded to the **repo root and the vault**,
- makes **no network calls**,
- **launches nothing** (no Claude, Codex, browser, or other process),
- reads/writes **no secrets**, and
- prints a single **JSON** object including `live_action: false` and `local_only: true`.

## 3. Wrapper contracts

| Wrapper | Mode | Inputs | Output (JSON) | Forbidden |
|---------|------|--------|---------------|-----------|
| `read_current_task.ps1` | read-only | — | task path, exists, preview, `allowed_actions_now` | writes, network, launch |
| `write_handoff_note.ps1` | dry-run (`-AllowWrite`) | `-Title`, `-Body`, `-Overwrite` | sanitized filename, `target_path`, `under_logs`, `wrote` | writing outside `04_Logs`, traversal, network |
| `prepare_claude_prompt.ps1` | dry-run (`-AllowWrite`) | — | `sources`, `output_path`, `preview`, `launches_claude:false` | launching Claude, network |
| `prepare_codex_audit.ps1` | dry-run (`-AllowWrite`) | — | `sources`, `output_path`, `preview`, `launches_codex:false` | launching Codex, network |
| `collect_agent_outputs.ps1` | read-only | — | per-log exists/line_count/size/preview, next action | LLM call, network, launch |
| `run_gemma_summary.ps1` | dry-run only | `-InputPath`, `-AllowLocalModel` | model, loopback endpoint (not contacted), `local_model_call_implemented:false` | network, model download, install |
| `hermes_router_status.ps1` | read-only | — | foundation file/wrapper presence + standing safety flags | writes, network, launch |

### Path-containment contract (`write_handoff_note.ps1`)

The title is sanitized to `[a-z0-9_-]` only, so `..`, `/`, `\`, and `:` collapse to
`_` and cannot escape the folder. A second check resolves the absolute target and
**refuses** any path that does not live strictly inside `04_Logs/`. In dry-run it
computes and reports the safe path and writes nothing.

## 4. How Hermes will route work (future)

`HERMES_ROUTER_POLICY.md` holds the routing table (planning → ChatGPT; memory/handoff
→ Hermes/Llama; summary → Gemma; implementation → Claude; audit → Codex; merge → human),
the risk levels (`low`/`medium`/`high`/`blocked`), and the status lifecycle
(`idle → planned → assigned → running → output_ready → audit_ready → blocked|pass →
human_decision`). A `high`/`blocked` task stops for a human; no gate is weakened.

## 5. What is explicitly NOT enabled

- **No Telegram.** **No browser/computer-use.** **No MCP installed.**
- **No arbitrary command execution** by Hermes.
- No autonomous agent launch — prompt preparation never starts Claude or Codex; any
  future launch is a separately-approved, dry-run-first milestone.
- No external repo clone/install/run. No live account/API/posting/money action.
- `main` is not touched by this milestone.

## 6. What Codex should audit next

1. Each wrapper matches its contract above and contains no `Invoke-Expression`,
   `Start-Process`, or outbound web call.
2. `write_handoff_note.ps1` cannot escape `04_Logs/` (traversal + containment).
3. `prepare_*` wrappers never launch an agent (`launches_claude/codex:false`).
4. `run_gemma_summary.ps1` makes no network call and downloads/installs nothing.
5. No doc/wrapper claims Telegram, browser/computer-use, MCP, or autonomy is enabled.
6. The change is scripts + memory notes + docs + tests only, and is trivially revertable.
