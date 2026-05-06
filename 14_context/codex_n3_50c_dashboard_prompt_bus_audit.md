# Codex N+3.50C - Dashboard And Prompt Bus Audit

Milestone: N+3.50C - Dashboard/Ruflo/Gemma parallel audit lane

Date: 2026-05-06

## Scope

This doc prepares the audit checklist for Claude's expected dashboard/local orchestrator card and prompt bus context-pack implementation. Codex does not edit dashboard/runtime files in this lane.

## Source-Check Summary

Primary sources checked:

- Express routing docs: `https://expressjs.com/en/guide/routing.html`
- Node.js filesystem docs: `https://nodejs.org/api/fs.html`
- Obsidian URI docs: `https://help.obsidian.md/uri`
- Python subprocess docs: `https://docs.python.org/3/library/subprocess.html`

Findings:

- Express `app.get()` routes are appropriate for read-only summary endpoints; `res.json()` sends JSON responses.
- Node filesystem read methods can support local status cards, but route handlers must avoid writes, deletes, path traversal, and secret paths.
- Obsidian URIs can open vault/file targets, but path behavior depends on the vault being known/registered in Obsidian. Opening the app is a local side effect and should remain operator-triggered, never automatic from a dashboard refresh.
- Python subprocess should avoid `shell=True`; subprocess calls should use list arguments and bounded allowlists.

## Expected Claude-Owned Dashboard/Prompt Files To Audit

Claude N+3.50 may add or modify:

- `03_scripts/ghoti_dashboard.py`
- `03_scripts/ghoti_local_orchestrator.py`
- `03_scripts/prompt_bus.py`
- `03_scripts/open_obsidian_vault.ps1`
- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/index.html`
- `14_context/ghoti_dashboard_card.md`
- `14_context/ghoti_dashboard_n3_50a.md`
- `14_context/prompt_bus_n3_50a_context_packs.md`
- `14_context/claude_n3_50a_dashboard_ruflo_gemma.md`

## Dashboard Route Audit Checklist

Expected route shape may be:

```text
GET /api/ghoti/local-orchestrator/summary
GET /api/ghoti/prompt-bus/summary
```

Audit requirements:

- GET only.
- No POST/PUT/PATCH/DELETE mutation routes.
- Reads local files only.
- Tolerates missing files.
- Tolerates malformed JSONL lines.
- Does not read `.env`, OS env, credential files, browser profiles, cookies, tokens, SSH keys, or payment/email/social configs.
- Does not run shell commands.
- Does not call external APIs.
- Does not call Ruflo.
- Does not call Ollama generation.
- Does not open Obsidian automatically.
- Does not write lane status automatically from dashboard refresh.
- Returns `warnings` for stale/missing data.
- Includes `source_files` in response.
- Avoids leaking absolute secret paths.
- Frontend has no mutation buttons.

Allowed UI actions:

- refresh
- copy file path
- copy prompt text if already in local file
- open local docs by existing project pattern, if safe

Forbidden UI actions:

- execute
- approve
- publish
- send
- pay
- scrape
- apply
- launch browser/operator
- run Ruflo
- pull/run Gemma model
- edit live state

## Prompt Bus Context Pack Audit Checklist

Expected behavior:

- Generate context packs under `05_logs/prompt_context_packs/<run_id>/`.
- Dry-run default.
- `--apply` required for writes.
- Inputs must be local repo files.
- Output artifacts should include:
  - `context_pack.md`
  - `context_pack.json`
  - `claude_prompt.md`
  - `codex_prompt.md`
  - `chatgpt_handoff.md`
  - `run_summary.json`
- No auto-send.
- No clipboard by default.
- No account connectors.
- No hidden mutation of `active_locks.jsonl` or `lane_status.jsonl`.
- Generated prompts must preserve allowed paths, forbidden paths, validation commands, branch, lane id, and hard safety rules.

## Obsidian Launch Helper Audit Checklist

Expected behavior:

- `-Check` should only verify files.
- `-Open` may call the local Obsidian URI, but only when explicitly invoked.
- No automatic launch from dashboard refresh.
- No plugin install.
- No Obsidian Sync/account login.
- No note writes unless a separate explicit local note-writing milestone approves it.
- Docs must warn that URI open may require the vault to have been opened/registered in Obsidian first.

## Local Orchestrator Card Checklist

Card should show:

- base branch and HEAD
- prompt bus outbox count
- canonical prompt path
- active lane count
- latest lane status
- Obsidian vault status
- compact memory status
- Ruflo readiness: missing / present / deps installed / gated
- Gemma readiness: Ollama missing / model missing / model available
- warnings
- next manual action

Card should not:

- run installs
- run model generation
- mutate files
- connect tools
- open apps automatically

## Safety Verdict

Verdict: SAFE TO IMPLEMENT IF READ-ONLY AND DRY-RUN-FIRST.

The dashboard/prompt-bus direction is exactly the right move toward 80%+ because it makes the local rails visible. It becomes unsafe only if dashboard refreshes start executing commands, opening apps, mutating state, or launching external tools.
