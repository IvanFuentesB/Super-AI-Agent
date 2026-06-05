# Tool Priority Map (N+6.22A)

Static planning only. Tiering follows the operator's priority rules. Nothing is
installed, cloned, or executed. Machine-readable details:
`tool_backlog_inventory_n6_22a.json`.

## Tier 1 (evaluate first; static-inspect)

- Paperclip - source_needed
- awesome-llm-apps (Shubhamsaboo)
- Understand-Anything - source_needed
- Ruflo (static-inspected in N+6.12A; patterns only)
- gstack - source_needed
- Obsidian-skills - source_needed
- Stop / Stop skill - source_needed
- CodeGraph / Git Nexus / dynamic code graph - source_needed (see `code_graph_lane_n6_22a.md`)
- Automation lane: n8n, Composio, Apify, Firecrawl, Browserbase
- Documents lane: MarkItDown, Stirling PDF, Surya OCR, Tesseract
- Kimi + Claude swarms research - source_needed
- DeepSeek / provider routing research

## Tier 2 (later)

- OpenHuman - source_needed
- TradingAgents (Tauric Research) - blocked/careful (no live trading)
- OpenWA - blocked/careful (no messaging)
- Cloakbrowser - blocked/careful (no anti-detection)
- Docmost
- DocuSeal
- AppFlowy
- Penpot
- Plausible
- Qdrant
- Whisper
- media downloader (ytdlp family) - blocked/careful (ToS / scale)
- Fooocus
- Clerk - needs secret management first
- Bitwarden - secrets-adjacent reference only

## Blocked / careful (gate before any action)

- Trading / live money actions (TradingAgents) - research/paper-only at most.
- Health / medical advice or action - out of scope.
- Account automation / login - out of scope.
- Mass messaging / spam (OpenWA) - out of scope.
- Cloaking / anti-detection (Cloakbrowser) - out of scope.
- Browser automation against real sites (Browserbase, live Apify) - gated.
- Unknown binaries - never run.
- Anything needing secrets / API keys (Composio, Clerk, Browserbase) - deferred to a
  dedicated secret-management milestone.

## Six classification lanes

`coding_brain_code_graph` · `agent_skills_swarms` · `automation_money` ·
`documents_content` · `apps_products` · `apis_model_routing`
