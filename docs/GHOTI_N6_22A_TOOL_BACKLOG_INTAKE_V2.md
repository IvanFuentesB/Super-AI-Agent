# Ghoti N+6.22A - Tool Backlog Intake v2 (static)

This milestone is **static intake and planning only**. It classifies a large new tool
backlog into six lanes, sets Tier 1 / Tier 2 / blocked priorities, records a per-tool
safety gate, and stands up the **Repo Memory Vault v1**. Nothing is installed, cloned,
or executed; no secrets are touched; and **no `agent_arena` files are modified**
(N+6.21B is auditing in parallel).

## What this produces

- Inventory: `14_context/tool_intake/tool_backlog_inventory_n6_22a.{md,json}`
- Priority map: `14_context/tool_intake/tool_priority_map_n6_22a.md`
- Safety gate matrix: `14_context/tool_intake/tool_safety_gate_matrix_n6_22a.md`
- Lane docs: `paperclip_tier1_intake`, `awesome_llm_apps_tier1_intake`,
  `code_graph_lane`, `money_automation_lane`, `model_provider_lane`,
  `rust_runtime_lane` (all `*_n6_22a.md`).
- Repo Memory Vault v1: `14_context/memory_vault/` + `docs/GHOTI_REPO_MEMORY_VAULT.md`.

## Six classification lanes

`coding_brain_code_graph` · `agent_skills_swarms` · `automation_money` ·
`documents_content` · `apps_products` · `apis_model_routing`.

## Priority summary

- **Tier 1:** Paperclip\*, awesome-llm-apps, Understand-Anything\*, Ruflo, gstack\*,
  Obsidian-skills\*, Stop skill\*, CodeGraph\*, n8n, Composio\*, Apify\*, Firecrawl,
  Browserbase\*, MarkItDown, Stirling PDF\*, Surya OCR\*, Tesseract, Kimi+Claude
  swarms\*, DeepSeek/provider routing\*.
- **Tier 2:** OpenHuman\*, TradingAgents (blocked), OpenWA (blocked), Cloakbrowser
  (blocked), Docmost\*, DocuSeal\*, AppFlowy, Penpot, Plausible, Qdrant, Whisper, media
  downloader (blocked), Fooocus, Clerk\*, Bitwarden (careful).
- **Blocked / careful:** live trading/money, health/medical, account automation, mass
  messaging, cloaking/anti-detection, live browser automation, unknown binaries, and
  anything needing secrets/keys before a secret-management milestone.

(`*` = `source_needed` / `needs_verification`: the operator must confirm the exact URL.)

## Source discipline

A URL is recorded only when confidently known; otherwise the item is `source_needed`
and is never guessed. No installs, no clones, no execution, no secrets/keys, no Docker,
no live money/messaging/account/browser actions.

## Rust note

Rust is **not needed now**; the planning lanes are Python + Markdown. A future Rust lane
is reserved only for concrete high-performance / time-sensitive needs (agent runtime,
file watchers, tracing, local IPC, long-running services). See
`14_context/tool_intake/rust_runtime_lane_n6_22a.md`. **Do not introduce Rust now.**

## Repo Memory Vault v1

A token-efficient durable memory area (`14_context/memory_vault/`) so the main memory
keeps only the short reminder while details live as Markdown. Categories: `lists/`,
`preferences/`, `tool_backlog/`, `project_notes/`, plus `templates/` and `INDEX.md`. No
secrets or sensitive personal data. See `docs/GHOTI_REPO_MEMORY_VAULT.md`.

## Dependency

Built from `origin/main e126fb2` (N+6.20B merged). **N+6.21B (agent arena) is auditing
in parallel; this lane touches no `agent_arena` files**, so the two can run
concurrently without conflict.

## Next milestone

Tool Intake v3: resolve the `source_needed` / `needs_verification` URLs with the
operator, then static-clone the highest-value Tier 1 items into the N+6.19A allowlisted
sandbox (shallow, static-scan-first) - still no installs, no live actions.
