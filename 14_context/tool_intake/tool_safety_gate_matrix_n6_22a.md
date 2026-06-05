# Tool Safety Gate Matrix (N+6.22A)

Every candidate maps to a gate. Static-inspect-first always; no install, clone, or
execution until the tool is allowlisted via the N+6.19A sandbox and passes its static
scan.

| Gate | Meaning | Tools |
|------|---------|-------|
| `tier1_static_inspect` | read-only static inspection allowed now; no install | Paperclip\*, awesome-llm-apps, Understand-Anything\*, Ruflo, gstack\*, Obsidian-skills\*, Stop skill\*, CodeGraph\*, n8n, Composio\*, Apify\*, Firecrawl, MarkItDown, Stirling PDF\*, Surya OCR\*, Tesseract, Kimi+Claude swarms\*, DeepSeek routing\* |
| `tier2_later` | deferred to a later milestone | OpenHuman\*, Docmost\*, DocuSeal\*, AppFlowy, Penpot, Plausible, Qdrant, Whisper, Fooocus, Clerk\* |
| `blocked_careful` | gated; not pursued without an explicit policy change | TradingAgents (no live trading), OpenWA (no messaging), Cloakbrowser (no anti-detection), Browserbase (live browser), media downloader (ToS / scale), Bitwarden (secrets-adjacent) |

`*` = `source_needed` or `needs_verification`: the operator must confirm the exact URL
before any intake.

## Hard gates (must pass before ANY runtime action)

- **No installs, no clones, no execution** until the tool is on the N+6.19A allowlist
  and passes its static scan.
- **No secrets / API keys** until a dedicated secret-management milestone exists.
- **No live money or trading**, no health/medical action, no account login, no
  messaging/send, no cloaking/anti-detection, no browser automation against real sites,
  no Docker run, and no unknown binaries.
- **Source-needed items are never guessed**; the operator supplies the exact URL.

## Why a gate per tool

Many of these tools are genuinely useful but carry real risk surfaces (live network,
accounts, money, large binaries, model weights). The matrix keeps every candidate
behind a clear, named gate so usefulness never outruns safety. The Agent Arena
(N+6.21A) can later render the Tier 1 set as a **simulated** swarm before anything
runs.
