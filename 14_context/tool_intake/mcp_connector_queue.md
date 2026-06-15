# MCP Connector Queue

Connectors awaiting setup, with required env var NAMES only (never values, never
secrets). All templates ship `enabled: false`. Setup steps:
`docs/GHOTI_MCP_SETUP_GUIDE.md`. Ordering: `mcp_connector_roadmap.md`.

## Awaiting setup

| Connector | Priority | Required env vars (names) | Gate |
|-----------|----------|---------------------------|------|
| github | P0 | `GITHUB_TOKEN` | Key, manual. |
| repomix | P0 | none | Local; intake-first to verify package. |
| notion | P0 | `NOTION_API_KEY` | Key, manual. |
| google-drive | P0 | `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REFRESH_TOKEN` | OAuth, manual. |
| google-calendar | P0 | `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REFRESH_TOKEN` | OAuth, manual. |
| gmail | P0 | `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REFRESH_TOKEN` | OAuth, manual; drafts only. |
| figma | P1 | `FIGMA_ACCESS_TOKEN` | Key, manual. |
| composio | P1 | `COMPOSIO_API_KEY` | Account + key, manual. |
| n8n | P1 | `N8N_BASE_URL`, `N8N_API_KEY` | Self-host + key, manual. |
| firecrawl | P1 | `FIRECRAWL_API_KEY` | Key, manual; respect robots/TOS. |
| apify | P1 | `APIFY_TOKEN` | Key, manual; TOS-compliant only. |
| perplexity | P1 | `PERPLEXITY_API_KEY` | Key, manual; verify canonical MCP. |

## Blocked until the browser / computer-use gate

| Connector | Required env vars (names) | Gate |
|-----------|---------------------------|------|
| chrome-devtools | none | Browser/computer-use gate. |
| browserbase | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` | Browser gate + keys, manual. |
| stagehand | `BROWSERBASE_API_KEY` | Browser gate + key, manual. |
| browser-observation-harness | none | Browser/computer-use gate (placeholder). |

## Rules

- Set env vars locally only. Never commit values. Names above are the only thing
  that lives in the repo.
- Flip `enabled: true` only after env vars are set and the safety review passes.
- Browser/computer-use connectors stay blocked until a separate gate.
