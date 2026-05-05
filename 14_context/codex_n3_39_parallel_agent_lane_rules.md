# N+3.39 Parallel Agent Lane Rules

Status: Codex planning/spec only.
Date: 2026-05-05

Ghoti should eventually support multiple agents and multiple computers, but only after there is a clear lane, lock, sync, and merge protocol. The N+3.38/N+3.29 overlap proved the need for this layer before serious parallel work.

## Why Parallel Agents Are Desired

- Claude Code can implement hard multi-file changes.
- Codex can audit, source-check, and prepare specs without blocking implementation.
- ChatGPT can hold strategy, prompts, and architecture direction.
- Gemma/Ollama can do cheap local text compression, summaries, and checklist drafting.
- Future workers such as OpenClaw, Paperclip, n8n, Paseo, Bulwark, cto.new, CUA, Camofox, Chrome DevTools MCP, Firecrawl MCP, and Glif MCP may become useful after safety rails.
- A new computer or new agent should be able to join without corrupting state.

## Branch-Per-Agent Rule

Every non-trivial agent should work on its own branch unless the operator explicitly assigns it to the shared feature branch.

Recommended pattern:

```text
agent/<agent_id>/<milestone_slug>
```

For the current private feature lane, if an agent must work directly on `feat/ghoti-visible-operator-stack`, it must follow the pull/context protocol and use lock/status artifacts.

## One Writer Per Shared File Rule

Only one active agent may write a shared state file at a time.

Shared files requiring locks:

- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/ghoti_finish_line_log.md`
- `14_context/compact_memory/*`
- `14_context/obsidian_vault/00_Index.md`
- `14_context/obsidian_vault/01_Current_State.md`
- `14_context/obsidian_vault/02_Next_Actions.md`
- `14_context/obsidian_vault/03_Decisions.md`
- `14_context/obsidian_vault/08_Dirty_State.md`

If two agents need to update one of these files, one writes the canonical update and the other writes a separate audit/handoff doc.

## Agent Lanes

| Lane | Primary agent | Allowed work | Must not do |
| --- | --- | --- | --- |
| Implementation lane | Claude Code | Runtime code, scripts, dashboard, validation, commits | Skip validation, stage unrelated dirt, install external tools without approval |
| Audit/source/spec lane | Codex | Repo audits, source checks, planning docs, review packs | Runtime edits unless explicitly requested |
| Strategy/prompt lane | ChatGPT | High-level direction, prompts, architecture, user strategy | Claim repo truth without source/check |
| Cheap local worker lane | Gemma/Ollama | Summaries, compression, checklists, local draft artifacts | Execute output, edit repo automatically, use live accounts |
| Future app/business builder lane | cto.new/OpenClaw/Paperclip/n8n/Paseo/Bulwark | Isolated experiments after approval | Live automation, payments, account actions, shared state writes without locks |
| Browser/operator lane | CUA/Camofox/Chrome DevTools MCP/Firecrawl MCP/Glif MCP | Read-only tests or local sandbox tasks after review | Scraping, posting, login, account actions, bypass, stealth |

## Future Multi-Computer Requirements

Each computer/agent needs:

- stable `agent_id`
- branch name
- lock file
- status beacon
- heartbeat timestamp
- write scope
- current milestone
- last fetched origin commit
- last pushed commit
- human approval gates

Recommended folder:

```text
14_context/agent_lanes/
```

Recommended lock artifact:

```text
14_context/agent_lanes/<agent_id>_active_lock.md
```

Recommended status artifact:

```text
14_context/agent_lanes/<agent_id>_status.md
```

## Lock File Contract

Each active lock should include:

- `agent_id`
- `agent_type`
- `machine_id`
- `branch`
- `milestone`
- `started_at`
- `heartbeat_at`
- `write_scope`
- `shared_files_locked`
- `intended_commit_message`
- `operator_approval_scope`
- `do_not_touch`

Locks are advisory until a future helper enforces them, but agents must treat them as real.

## Git Pull/Context Protocol

Every agent must:

1. Run `git fetch origin`.
2. Record `git branch --show-current`.
3. Compare `git rev-parse HEAD` to `git rev-parse origin/<branch>`.
4. If clean and behind, use fast-forward only.
5. If dirty and behind, stop and report.
6. If ahead, record unpushed commits and ask/push only if assigned.
7. If diverged, stop and report.
8. Never use `git reset --hard` without explicit human approval.
9. Never stage unrelated local dirt.
10. Never edit shared files without checking active locks.

PowerShell-safe comparison:

```powershell
git fetch origin
$branch = git branch --show-current
$local = git rev-parse HEAD
$remote = git rev-parse "origin/$branch"
git status --short
Write-Output "branch=$branch local=$local remote=$remote"
```

## No Simultaneous Edits Rule

Do not simultaneously edit the same file unless explicitly planned with disjoint sections and a designated integrator.

Default policy:

- Claude owns implementation files during implementation milestones.
- Codex owns `codex_n*_*.md` docs during audit milestones.
- Only one agent appends/prepends to state docs per milestone.
- Gemma outputs artifacts only, not direct file edits.

## Merge Checklist

Before merge/push:

- `git fetch origin`
- confirm branch and origin
- confirm no divergence
- inspect `git status --short`
- inspect `git diff --cached --name-status`
- verify staged whitelist
- run milestone validation
- commit only intentional files
- push
- record commit hash
- update status artifact

## Parallel Agent Safety Rule

Parallel does not mean autonomous live action. No agent may post, send, sell, pay, scrape, create accounts, use live accounts, bypass subscriptions/caps/auth/captchas, or execute model output without explicit operator approval and a future safety milestone.
