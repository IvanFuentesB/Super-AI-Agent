# MCP Connector Roadmap

Priority ordering for the 16 connectors, what each unlocks, and the gate each
needs before it can go live. All templates ship `enabled: false`; OAuth, API
keys, and accounts are always manual human steps. Setup steps:
`docs/GHOTI_MCP_SETUP_GUIDE.md`.

## P0 - enable first (low-risk, high-leverage)

| Connector | Unlocks | Gate needed |
|-----------|---------|-------------|
| github | Read issues/PRs/repo metadata for the agents | `GITHUB_TOKEN` (key, manual) |
| repomix | Pack a repo into one AI-friendly file (local) | none (intake-first to verify package) |
| notion | Read/append notes and databases | `NOTION_API_KEY` (key, manual) |
| google-drive | Read/search docs | OAuth (manual) |
| google-calendar | Read events, propose times | OAuth (manual) |
| gmail | Read/draft email (drafts only) | OAuth (manual) |

## P1 - enable after P0 (more setup or higher risk)

| Connector | Unlocks | Gate needed |
|-----------|---------|-------------|
| figma | Read designs for design-to-code | `FIGMA_ACCESS_TOKEN` (key, manual) |
| composio | Managed multi-SaaS connector hub | `COMPOSIO_API_KEY` (account + key, manual) |
| n8n | Self-hosted automation flows (design first) | `N8N_BASE_URL`, `N8N_API_KEY` (self-host + key, manual) |
| firecrawl | Crawl/scrape to markdown (TOS-compliant) | `FIRECRAWL_API_KEY` (key, manual) + robots/TOS check |
| apify | Actor-based scraping (compliant only) | `APIFY_TOKEN` (key, manual) + TOS check |
| perplexity | Search/context | `PERPLEXITY_API_KEY` (key, manual) + verify canonical MCP |

## Browser / computer-use - blocked until a separate gate

| Connector | Unlocks | Gate needed |
|-----------|---------|-------------|
| chrome-devtools | Inspect page DOM/network for debugging | Separate browser/computer-use safety gate |
| browserbase | Hosted browser (observation first) | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` + browser gate |
| stagehand | Browser automation framework (observation first) | `BROWSERBASE_API_KEY` + browser gate |
| browser-observation-harness | Future observe-only computer-use bridge (placeholder) | Browser/computer-use gate (placeholder) |

## Notes

- A template being present does not enable a capability. Enabling requires local
  env vars, a safety review, then flipping `enabled: true` in a local config.
- Browser and computer-use capabilities stay blocked until a separate gate, even
  if keys are available.
- Crawl/scrape connectors (firecrawl, apify) must respect robots.txt and each
  site's Terms of Service. Official APIs are preferred.
- Setup queue with env var names: `14_context/tool_intake/mcp_connector_queue.md`.
