# Master Tool Backlog

Human-readable view of `14_context/tool_intake/tool_registry.json`, grouped by
priority. Nothing here is installed or enabled by being listed. `source_needed`
means the canonical source/URL must be confirmed before any intake.

## P0 - do first

| id | name | category | status | next action |
|----|------|----------|--------|-------------|
| claude-codex-skills-setup | Claude/Codex skills setup | skill | intake_ready | Write skills registry + setup docs; install official Anthropic skills repo by inspection. |
| mcp-connector-templates | MCP connector templates | mcp | intake_ready | Generate config_templates (enabled:false) + MCP setup guide. |
| repo-intake-sandbox | Repo intake sandbox | security | intake_ready | Use repo_intake dry-run, then review report before any adapt. |
| obsidian-ghoti-memory | Obsidian/Ghoti memory | memory | adopt | Reuse existing vault + compact_memory; do not add a second store. |
| repomix | Repomix | repo | needs_source | Confirm official package; intake via repo_intake before use. |
| gitingest | git ingest / gitingest | repo | needs_source | Confirm canonical source; intake-first. |
| code-graph-comprehension | CodeGraph / dynamic code graph | repo | needs_source | Identify maintained OSS; intake-first; no execution. |
| composio-connectors | Composio connectors | mcp | needs_source | Template only; OAuth/keys manual; enabled:false. |
| n8n-connector | n8n automation | automation | needs_source | Plan flows + approval gates; no live execution; template only. |
| local-model-routing | Local model routing (OpenRouter/Ollama) | local_model | intake_ready | Document strategy; real calls audited separately. |
| command-dashboard-hooks | Command dashboard hooks | analytics | intake_ready | Expose --status JSON; add dashboard card only when zero-conflict. |
| plausible-geo-leadgen | Plausible / GEO / lead-gen analytics | analytics | needs_source | Define compliant data sources; no TOS-violating scraping. |
| content-video-pipeline | Content/video pipeline lane | content | adopt | Reuse content-video workflow; no posting/upload. |
| github-mcp | GitHub MCP | mcp | intake_ready | Template only; token via env, enabled:false. |

## P1 - next

| id | name | category | status | next action |
|----|------|----------|--------|-------------|
| browserbase-stagehand | Browserbase / Stagehand observation | automation | needs_source | Observation-only design; no live control; account+keys manual. |
| chrome-devtools-mcp | Chrome DevTools MCP | mcp | needs_source | Template only; browser caps blocked by default. |
| firecrawl | Firecrawl | automation | needs_source | Template only; keys manual; respect robots/TOS. |
| apify | Apify | automation | needs_source | Template only; keys manual. |
| remotion-whisper-mediafetch | Remotion / Whisper / media-fetch | content | needs_source | Install recipe + manual; verify licensing; no copyrighted re-upload. |
| figma-penpot-antv | Figma / Penpot / AntV | design | needs_source | Figma MCP template; Penpot/AntV intake-first. |
| typebot-listmonk | Typebot / Listmonk | automation | needs_source | Plan opt-in funnels; no cold spam; manual setup. |
| cad-text-to-cad | CAD / text-to-CAD / SolidWorks | cad | needs_source | Identify OSS by intake; no license abuse. |
| mem0-claudemem-obsidian | Mem0 / Claude Mem / Obsidian bridge | memory | needs_source | Intake-first; only adopt if it extends the one memory path. |
| superclaude-bmad-archon | SuperClaude / BMAD / Archon | skill | needs_source | Intake-first; extract patterns; do not import wholesale. |
| whop-tiktokshop-dropship | Whop / TikTok Shop / dropshipping | business | needs_source | Research lane; no fake engagement; human runs accounts. |

## P2 - defer

| id | name | category | status | next action |
|----|------|----------|--------|-------------|
| paid-unclear-apis | Paid/heavy/unclear APIs | infrastructure | defer | Revisit after P0/P1 land. |
| heavy-gpu-video | Heavy GPU video tools (Fooocus etc.) | content | defer | Defer; manual install with explicit approval. |
| vps-docker-deploy | VPS / Docker deployments | infrastructure | defer | Docker check-only now; no service start. |
| digital-influencer-advanced | Digital influencer advanced pipeline | content | defer | Defer; require disclosure + platform-TOS compliance. |
| ads-automation-approval | Ads automation (human approval only) | automation | defer | Defer; no autonomous spend ever. |
| tradingagents-research | TradingAgents (research only) | business | defer | Research only; trading is blocked. |

## Reject - do not build

| id | name | reason |
|----|------|--------|
| unofficial-whatsapp | Unofficial WhatsApp automation | TOS violation / account ban risk. Use official WhatsApp Business API only, later. |
| spam-fake-engagement | Spam / fake engagement | Fraud / platform abuse. |
| seat-hoarding-abuse | Seat-hoarding / reservation abuse | Abuse / possible illegality; harms others. |
| false-report-workflows | False-report workflows | Harassment / fraud. |
| payment-account-abuse | Payment / account abuse | Financial fraud. |
| stealth-account-automation | Stealth account automation | TOS violation / deception. Official APIs only. |
