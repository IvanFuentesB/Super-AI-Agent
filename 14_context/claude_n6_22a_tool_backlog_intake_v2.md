# Ghoti N+6.22A - Tool Backlog Intake v2 + Repo Memory Vault v1 (Report)

## Summary

A **static, planning-only** milestone: it classifies a large new tool backlog into six
lanes, sets Tier 1 / Tier 2 / blocked priorities with a per-tool safety gate, and stands
up the **Repo Memory Vault v1**. Nothing is installed, cloned, or executed; no secrets
are touched; and **no `agent_arena` files are modified** (N+6.21B audits in parallel).

## Verdict

IMPLEMENTED_AND_PUSHED.

## Branch / worktree / base / dependency

- Branch: `feat/ghoti-agent-claude-n6-22a-tool-backlog-intake-v2`
- Commit message: `docs(ghoti): add tool backlog intake v2`
- Worktree: `<repo>/.claude/worktrees/n6_22a_tool_backlog_intake_v2`
- Base `origin/main`: `e126fb2` (N+6.20B merge gate). **N+6.20B is on main.**
- **Dependency:** N+6.21B (agent arena) is **not yet on main** (Codex auditing the
  loopback-only fix). This lane is independent and **touches no `agent_arena` files**,
  so it runs in parallel without conflict.

## Tier 1 (static-inspect first)

Paperclip\*, awesome-llm-apps (Shubhamsaboo), Understand-Anything\*, Ruflo, gstack\*,
Obsidian-skills\*, Stop skill\*, CodeGraph / Git Nexus / dynamic code graph\*, n8n,
Composio\*, Apify\*, Firecrawl, Browserbase\*, MarkItDown, Stirling PDF\*, Surya OCR\*,
Tesseract, Kimi+Claude swarms\*, DeepSeek / provider routing\*.

## Source-needed / needs-verification (never guessed)

Paperclip, Understand-Anything, gstack, Obsidian-skills, Stop skill, CodeGraph, Composio,
Apify, Browserbase, Stirling PDF, Surya OCR, Kimi+Claude swarms, DeepSeek routing repo,
OpenHuman, TradingAgents, OpenWA, Cloakbrowser, Docmost, DocuSeal, Clerk. (URLs are
recorded only when confidently known - e.g. n8n, Firecrawl, MarkItDown, Tesseract,
Whisper, Qdrant, AppFlowy, Penpot, Plausible, Fooocus, awesome-llm-apps, Ruflo.)

## Blocked / careful

- Live trading / money actions (TradingAgents) - research/paper-only at most.
- Health / medical advice or action - out of scope.
- Account automation / login - out of scope.
- Mass messaging / spam (OpenWA) - out of scope.
- Cloaking / anti-detection (Cloakbrowser) - out of scope.
- Browser automation against real sites (Browserbase, live Apify) - gated.
- Bulk media downloading (the `ytdlp` family) - ToS/scale; out of scope.
- Unknown binaries - never run.
- Anything needing secrets/API keys (Composio, Clerk, Browserbase, Bitwarden) - deferred
  to a secret-management milestone.

## Repo Memory Vault v1 summary

`14_context/memory_vault/` is a token-efficient, durable memory area: the main memory
keeps the short reminder; the details live as Markdown. Categories `lists/`,
`preferences/`, `tool_backlog/`, `project_notes/` (each with `.gitkeep`), plus
`templates/` (`checklist.md`, `tool_note.md`) and a top-level `INDEX.md`. Markdown for
humans, JSON only for script indexes. **No secrets, tokens, health details, addresses,
or sensitive personal data** may be committed. Design doc: `docs/GHOTI_REPO_MEMORY_VAULT.md`.

## Rust lane note

Rust is **not needed now** (the planning lanes are Python + Markdown). A future Rust lane
is reserved only for concrete high-performance / time-sensitive needs (agent runtime,
file watchers, tracing, local IPC, long-running background services). See
`14_context/tool_intake/rust_runtime_lane_n6_22a.md`. **Do not introduce Rust now.**

## Skills

- Used: `ghoti-status` (repo/lane-lock inspection before editing - no N6 lane-lock
  conflict) and `anthropic-skills:karpathy-guidelines` (surgical, minimal, planning-only;
  it kept the milestone strictly static and pushed honest `source_needed` flags instead
  of guessed URLs). No ECC/CCE plugin is installed in this session.

## Validation

- `python -m unittest discover -p "test_n6_22a_*.py"` -> **16 tests, 16 pass**.
- `public_repo_security_audit.py --run --json` -> **`failed_checks: 0`,
  `safe_to_make_public: true`, no blocking findings** (the inventory avoids the
  scanner-flagged video-downloader token and keeps the JSON free of bot-bypass phrases).
- `ghoti_product_launcher.py --status / --context-pack / --repo-map --json` -> **all
  `ok: true`**.
- `git diff --check` -> **clean**.
- Generated residue restored (the context-pack / repo-map generated files); only the 23
  new files remain.

## What remains disabled

No installs, no clones, no execution, no secrets/API keys, no Docker, no live
money/trading, no messaging/send, no account login, no browser automation against real
sites, no cloaking/anti-detection. Source-needed items are never guessed. Nothing here
touches `agent_arena`.

## Security note (repo docs are public-safe)

Committed repo documentation must use **placeholders** for paths, images, and secrets -
for example `<repo>`, `<runtime_repo>`, `<user_home>`, `<worktree>`, `<private_path>`. No
real local paths, usernames, private machine names, private images, secrets, tokens,
credentials, account data, or other sensitive personal data may be committed; these docs
are **public-safe only**. (This amends the original report, which embedded a real
worktree path; it now reads `<repo>/.claude/worktrees/...`. The N+6.22A test includes a
regression check that fails if a real local path or username reappears.)

## Codex audit target branch

`audit/ghoti-agent-codex-n6-22a-tool-backlog-intake-v2`
