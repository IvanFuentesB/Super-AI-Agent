# Money / automation lane (N+6.22A)

Static, planning-only. This lane is about **automation that could eventually support
content/products**, not about taking live money actions.

## Candidates

- **n8n** (`github.com/n8n-io/n8n`) - self-hostable workflow automation. Source-available
  license (not OSI); verify terms. Static-inspect first; no install, no Docker run.
- **Composio** - agent tool/integration layer. `needs_verification`; needs API keys to
  run, so deferred to a secret-management milestone.
- **Apify** - web scraping/automation platform. `needs_verification`; live scraping is
  gated; account/keys deferred.
- **Firecrawl** (`github.com/mendableai/firecrawl`) - crawl + convert sites to markdown.
  Live crawling against real sites is gated; static-inspect first.
- **Browserbase** - hosted headless browser. `needs_verification`; live browser
  automation is deferred behind the browser + secret gates.

## Explicitly blocked / careful

- **TradingAgents (Tauric Research)** - study the multi-agent design only. **No live
  trading, no orders, no transfers, no money movement** - research/paper-only at most.
- **OpenWA** - messaging automation. **Blocked**: no messaging/send, no account login.
- **Cloakbrowser** - anti-detection browser. **Blocked**: conflicts with the
  no-cloaking, no-anti-detection policy.

## Hard rules for this lane

- No live money, no trading, no payments, no transfers.
- No account login, no messaging/send, no mass outreach.
- No browser automation against real sites until a separate, gated milestone.
- No secrets/API keys until a secret-management milestone.
- Everything is static-inspect-first behind the N+6.19A allowlisted sandbox.

The genuinely safe near-term value here is **local content/document automation**
(n8n-style workflows run locally, Firecrawl/MarkItDown for content) - never live money.
