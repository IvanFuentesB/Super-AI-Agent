# Tool Backlog Inventory (N+6.22A)

Static, planning-only. Machine-readable version:
`tool_backlog_inventory_n6_22a.json`. A URL appears only when confidently known;
otherwise the item is `source_needed` and is never guessed. No installs, clones, or
execution. Every candidate is static-inspect-first behind the N+6.19A sandbox gates.

## coding_brain_code_graph

| Tool | Tier | Source |
|------|------|--------|
| CodeGraph / Git Nexus / dynamic code graph | 1 | source_needed |

## agent_skills_swarms

| Tool | Tier | Source |
|------|------|--------|
| awesome-llm-apps | 1 | github.com/Shubhamsaboo/awesome-llm-apps |
| Ruflo | 1 | github.com/ruvnet/ruflo (patterns only) |
| Paperclip | 1 | source_needed |
| Obsidian-skills | 1 | source_needed |
| Stop / Stop skill | 1 | source_needed |
| Kimi + Claude swarms research | 1 | source_needed |

## automation_money

| Tool | Tier | Source | Gate |
|------|------|--------|------|
| n8n | 1 | github.com/n8n-io/n8n | static-inspect |
| Composio | 1 | needs_verification | static-inspect; keys deferred |
| Apify | 1 | needs_verification | live scraping gated |
| Browserbase | 1 | needs_verification | live browser - deferred |
| TradingAgents (Tauric Research) | 2 | needs_verification | blocked: no live trading |
| OpenWA | 2 | needs_verification | blocked: no messaging |
| Cloakbrowser | 2 | source_needed | blocked: no anti-detection |

## documents_content

| Tool | Tier | Source | Gate |
|------|------|--------|------|
| MarkItDown | 1 | github.com/microsoft/markitdown | static-inspect (done N+6.19A) |
| Firecrawl | 1 | github.com/mendableai/firecrawl | live crawl gated |
| Stirling PDF | 1 | needs_verification | static-inspect; no Docker |
| Surya OCR | 1 | needs_verification | no install (weights) |
| Tesseract | 1 | github.com/tesseract-ocr/tesseract | static-inspect |
| Whisper | 2 | github.com/openai/whisper | local-only; no install yet |
| DocuSeal | 2 | needs_verification | no live signing |
| Understand-Anything | 1 | source_needed | static-inspect |
| media downloader (ytdlp family) | 2 | url omitted (scanner) | blocked: ToS / scale |

## apps_products

| Tool | Tier | Source | Gate |
|------|------|--------|------|
| AppFlowy | 2 | github.com/AppFlowy-IO/AppFlowy | study only |
| Penpot | 2 | github.com/penpot/penpot | study only |
| Plausible | 2 | github.com/plausible/analytics | study only |
| Fooocus | 2 | github.com/lllyasviel/Fooocus | no install (weights) |
| Docmost | 2 | needs_verification | no Docker run |
| gstack | 1 | source_needed | static-inspect |
| OpenHuman | 2 | source_needed | deferred |
| Clerk | 2 | needs_verification | needs secret management |
| Bitwarden | 2 | github.com/bitwarden | secrets-adjacent; reference only |

## apis_model_routing

| Tool | Tier | Source | Gate |
|------|------|--------|------|
| DeepSeek (cheap long-context) routing research | 1 | github.com/deepseek-ai (verify) | research only; no keys |
| Qdrant | 2 | github.com/qdrant/qdrant | local-only; GBrain memory lane |
| Composio | 1 | needs_verification | keys deferred |

_Notes, license guesses, and per-tool gates live in the JSON. `needs_verification` and
`source_needed` both require the operator to confirm the exact URL before intake._
