# N+3.45B Orchestrator Tool Routing Audit

Status: Codex source-check/audit lane only.
Date: 2026-05-05
Branch assumption: `audit/ghoti-agent-codex-n3-45-tool-routing`

## Scope

This audit preserves current public tool-routing research for Ghoti. It does not install, clone, run, connect, scrape, post, send, pay, create accounts, or touch live accounts.

## Source Summary

| Tool / concept | Source check | What it claims | Likely Ghoti use | Local / safe / reversible | Install risk | Runtime risk | Account/live risk | Install now? | Recommendation |
|---|---|---|---|---|---|---|---|---|---|
| Prompt bus / copy-paste manager | repo design, no external source required | Local prompt routing and handoff artifacts | Immediate low-risk coordination between ChatGPT, Claude, Codex, and operator | Yes, if file-only and no auto-send | Low | Low | Low if no clipboard auto-send | No install | Build local docs/files first |
| Python automation worker | repo design + stdlib pattern | Deterministic local parsing, reports, validation, queue processing | Replace model calls for repeatable tasks | Yes | Low if stdlib-only | Low | Low | No install | Use before external orchestrators |
| Ollama/Gemma | Verified via Ollama docs | Ollama runs local models including Gemma 3 and offers CLI/API/docs | Cheap summaries, drafts, scoring, compression | Local if model already installed and no web tools | Low if already installed; no new pull in this lane | Medium if model output is over-trusted | Low if no external tools | Already present in Ghoti; no new action | Use only for draft artifacts |
| Obsidian | Verified via Obsidian Help | Local vault is a folder of Markdown files | Durable memory and human-readable local brain | Yes | Low | Low | Low | Already scaffolded | Use now/soon as source-of-truth memory UI |
| Claude Code commands/hooks/agents/MCP | Verified via Anthropic docs | Skills/commands/hooks/MCP can extend Claude Code; hooks can run commands | Future prompt bus hooks and verification gates | Reversible if project-local and reviewed | Medium | High if hooks execute shell automatically | Medium if MCP connects accounts | Not in this lane | Use only after lock + hook safety review |
| Codex cloud/background/parallel tasks | Verified via OpenAI docs | Codex cloud can run background and parallel coding tasks in separate environments | Future audit/source lanes and long-running Codex tasks | Safe if branch-isolated | Low | Medium if stale branches collide | Low | Already available conceptually | Use only with lane locks |
| Ruflo / `ruvnet/ruflo` | Verified public GitHub found; third-party concerns exist | Claude Code multi-agent/orchestration plugins, CLI, MCP server | Candidate orchestrator after Ghoti lane locks mature | Reversible only in isolated clone/sandbox | High: npx/curl/global install paths | High: many-agent automation and MCP control | Medium/high if connected to live tools | No | Isolated clone/intake only after prompt bus |
| OpenClaw | Public GitHub/source-check found; ecosystem has many mirrors/noisy claims | Personal AI assistant/agent runtime with channels/tools | Future worker/operator layer | Not safe until sandboxed | High | High: can touch shell/files/browser/accounts | High if channels/accounts connected | No | Research and isolated sandbox only |
| PaperclipAI/paperclip | Verified GitHub/docs/site found | Node/React platform for managing agent teams/companies, budgets, heartbeats | Future control-plane candidate | Reversible only as isolated local service | High | High: manages agents and goals | Medium/high if connected to accounts or costs | No | Compare after local prompt bus and lane pilot |
| n8n | Verified official docs | Workflow automation with built-in MCP server; can expose/run/build workflows | Future approved automation rails | Reversible if local/self-hosted and disabled | Medium/high | High if workflows have credentials | High if connected to services | No | Later, after connector policy and no-live-action gates |
| CUA / trycua | Verified GitHub found | Computer-use agent infrastructure, sandboxes, SDKs, benchmarks | Future controlled browser/desktop operator | Sandbox-only, not live | High | High: desktop control | High if sessions/accounts used | No | Only after sandbox approval |
| Chrome DevTools MCP/CLI | Verified Chrome docs | DevTools MCP/CLI for coding agents; token-efficient CLI option | Future frontend inspection tool | Local if only localhost/devtools | Medium | Medium/high if controlling real browser | High if logged-in sites used | No | Localhost-only pilot later |
| Firecrawl MCP | Verified Firecrawl docs | Search/scrape/crawl/interact/deep research/browser sessions via MCP/API | Future research extractor | Not local-only; account/API key | Medium/high | High: scraping and browser interaction | High: API key/account/credit usage | No | Research-only until legal/TOS + API budget gates |
| Glif MCP | Source found via MCP directory | Runs hosted Glif workflows like image/meme/ComfyUI/LLM chains | Future creative content drafts | External account/API token likely | Medium | Medium/high: external workflow execution | Medium/high | No | Creative sandbox only after approval |
| Camofox/Camoufox browser | Public GitHub/PyPI found | Anti-detection browser automation/server | Browser lane candidate, but risky | Not safe by default | High | Very high: anti-detection and cookie import | Very high | No | Reject for now except legal/security research |
| JobSpy / python-jobspy / jobspy-mcp | Verified PyPI/docs and MCP repo found | Job-posting scraping across job boards | Future internship research, but not sending/applying | Not safe until legal/TOS reviewed | Medium | High: scraping job platforms | Medium/high | No | Research-only; official application route first |
| Free Claude / leaked / cap-bypass repos | Public warnings found | Claims unlocked/no-limit Claude Code or leaked source | None for Ghoti runtime | Not safe | Very high | Very high malware/legal/provider-risk | High | No | Reject/runtime-forbidden; quarantine-audit only |
| Giveaway bots / fake engagement | Public legal/risk sources found | Automate contest entries or fake social metrics | None | Not safe | High | High | High | No | Reject automation; manual lawful tracking only |

## Source Links

- Ruflo GitHub README: https://github.com/ruvnet/ruflo/blob/main/README.md
- Paperclip GitHub/org: https://github.com/paperclipai
- Paperclip agent docs: https://paperclip.inc/docs/guides/agent-developer/how-agents-work/
- n8n MCP docs: https://docs.n8n.io/advanced-ai/mcp/accessing-n8n-mcp-server/
- Obsidian data storage docs: https://obsidian.md/help/data-storage
- Claude Code skills/slash commands: https://code.claude.com/docs/en/slash-commands
- Claude Code hooks: https://code.claude.com/docs/en/hooks
- Codex cloud docs: https://developers.openai.com/codex/cloud
- Ollama docs: https://docs.ollama.com/
- Chrome DevTools for agents: https://developer.chrome.com/docs/devtools/agents
- Firecrawl MCP docs: https://docs.firecrawl.dev/mcp-server
- CUA GitHub: https://github.com/trycua/cua
- Glif MCP directory: https://mcp.directory/servers/glif
- python-jobspy PyPI: https://pypi.org/project/python-jobspy/
- JobSpy docs: https://mintlify.wiki/speedyapply/JobSpy/introduction
- Coursera terms: https://www.coursera.org/about/terms
- edX terms: https://www.edx.org/edx-terms-service
- Bot legality overview: https://legalclarity.org/are-bots-legal-what-makes-their-use-unlawful/
- Fake engagement risk: https://www.disclosurefacts.com/blog/why-buying-fake-followers-and-likes-backfires
- Claude leak malware warning: https://www.techradar.com/pro/security/be-careful-what-you-click-hackers-use-claude-code-leak-to-push-malware

## Recommended Order

1. Prompt bus/local worker.
2. Obsidian vault local use.
3. Ruflo isolated clone/intake.
4. OpenClaw/Paperclip/n8n isolated comparisons.
5. Browser tools only after controlled sandbox.
6. Live accounts last.

## Why This Order

Prompt bus, Obsidian, Python automation, and Gemma compression create local discipline before adding external autonomy. Ruflo/OpenClaw/Paperclip/n8n/browser tools are powerful precisely because they can coordinate or execute actions; Ghoti needs locks, status, approval gates, and local dry-run conventions before they are connected.

## Current Verdict

Do not install or connect any external orchestrator yet. The safe next step is to let Claude finish the N+3.45A prompt-bus/local-worker lane, then audit it before any runtime tool integration.
