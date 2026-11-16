# Ghoti MCP Setup Guide

How to enable an MCP connector from a disabled-by-default template. Nothing in
this repo is live: every template ships with `enabled: false`, no secrets are
stored, and no account actions run until a human completes setup and a safety
review.

## Hard rules (apply to every connector)

- No secrets in the repo. Set credentials as local environment variables only.
- Templates default to `enabled: false`. Do not commit an enabled config with
  secrets inlined.
- No live account actions yet: no sending email, posting, purchases, payments,
  or trading.
- Browser and computer-use capabilities stay blocked until a separate gate
  (see "Browser / computer-use stay blocked" below).
- Use official APIs only. Respect each provider's Terms of Service and
  `robots.txt` for any crawl/scrape connector.

## Enable a connector (checklist)

1. Copy the template, do not edit it in place:
   `14_context/mcp_connectors/config_templates/<id>.template.json`
   to your real config path (the template names a `config_path_placeholder`,
   e.g. `23_configs/mcp/<id>.json`). The real config is local, not committed
   with secrets.
2. Set the required env vars locally (names listed in the table below and in the
   template's `required_env_vars`). Never paste values into any tracked file.
3. Complete the safety review for that connector: confirm `allowed_capabilities`
   are read-only / non-destructive and that `blocked_capabilities` remain
   blocked.
4. Flip `enabled: true` only in your local config, only after steps 2-3.
5. Run the connector's `test_command` (a read-only smoke test) to confirm wiring.
6. Stop if anything writes outside the repo root, performs an outbound action,
   or touches a blocked capability. Those require explicit human confirmation.

## The 16 connectors

| Connector | Purpose | Required env vars | Safety note |
|-----------|---------|-------------------|-------------|
| github | Read/manage issues, PRs, repo metadata | `GITHUB_TOKEN` | Read-only first; force-push/secrets/billing stay blocked. |
| gmail | Read/draft email | `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REFRESH_TOKEN` | Drafts only; sending stays blocked. |
| google-calendar | Read events, propose times | `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REFRESH_TOKEN` | Read/propose only; no auto-accept or invite sending. |
| google-drive | Read/search docs | `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REFRESH_TOKEN` | Read-only; no edit/delete/share. |
| notion | Read/append notes and databases | `NOTION_API_KEY` | Read first; appends only after review. |
| figma | Read designs for design-to-code | `FIGMA_ACCESS_TOKEN` | Read-only metadata/design context. |
| chrome-devtools | Inspect page DOM/network for debugging | none | Browser capability: blocked until the separate gate. |
| browserbase | Hosted browser (observation design first) | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` | Browser capability: blocked until the separate gate. |
| composio | Managed multi-SaaS connector hub | `COMPOSIO_API_KEY` | List/read only; each downstream action needs its own review. |
| n8n | Self-hosted automation flows (design first) | `N8N_BASE_URL`, `N8N_API_KEY` | Design flows on paper; no live execution. |
| stagehand | Browser automation framework (observation first) | `BROWSERBASE_API_KEY` | Browser capability: blocked until the separate gate. |
| firecrawl | Crawl/scrape to markdown (TOS-compliant only) | `FIRECRAWL_API_KEY` | Respect robots.txt/TOS; only pages you may read. |
| apify | Actor-based scraping (compliant use only) | `APIFY_TOKEN` | Compliant actors only; no TOS-violating scraping. |
| perplexity | Search/context | `PERPLEXITY_API_KEY` | Verify canonical MCP first; search only. |
| repomix | Pack a repo into one AI-friendly file | none | Local-only packing; no network beyond the target repo. |
| browser-observation-harness | Future observe-only computer-use bridge (placeholder) | none | Placeholder; blocked until the separate computer-use gate. |

## Browser / computer-use stay blocked

`chrome-devtools`, `browserbase`, `stagehand`, and `browser-observation-harness`
expose browser or computer-use surfaces. These remain blocked until a separate
safety gate explicitly authorizes them. Having a template present does not enable
the capability; it only documents the wiring for later, human-approved setup.

## Where things live

- Templates: `14_context/mcp_connectors/config_templates/<id>.template.json`
- Connector roadmap (P0/P1 ordering): `14_context/mcp_connectors/mcp_connector_roadmap.md`
- Setup queue + env var names: `14_context/tool_intake/mcp_connector_queue.md`
- Manual setup matrix: `14_context/tool_stack/manual_setup_required.md`
- Writer: `python 03_scripts/tool_stack/ghoti_tool_stack.py --write-mcp-templates`
