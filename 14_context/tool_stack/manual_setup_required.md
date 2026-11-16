# Manual Setup Required

These need a human to complete setup (OAuth/keys/accounts). Agents never do
these live. Env-var names only; never commit values.

## MCP connectors (set env vars locally, then flip enabled:true after review)

- GitHub: `GITHUB_TOKEN`
- Gmail: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REFRESH_TOKEN`
- Google Calendar / Drive: same Google OAuth vars
- Notion: `NOTION_API_KEY`
- Figma: `FIGMA_ACCESS_TOKEN`
- Browserbase / Stagehand: `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID`
- Composio: `COMPOSIO_API_KEY`
- n8n: `N8N_BASE_URL`, `N8N_API_KEY`
- Firecrawl: `FIRECRAWL_API_KEY`
- Apify: `APIFY_TOKEN`
- Perplexity: `PERPLEXITY_API_KEY`

## Skills needing manual install

See `14_context/tool_stack/skills_registry.json` (manual_required=true rows) and
`docs/GHOTI_AGENT_SKILLS_SETUP.md`. Do not overwrite user/global skill folders.

## Local models (optional)

- Ollama present locally; OpenRouter optional (`OPENROUTER_API_KEY`) as fallback.
