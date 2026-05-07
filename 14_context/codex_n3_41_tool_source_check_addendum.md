# N+3.41 Tool Source Check Addendum

Status: Codex source-check/backlog only.
Date: 2026-05-05

No tool below is approved for install, clone, connector setup, MCP connection, runtime wiring, scraping, emailing, posting, payments, or account creation.

This addendum is the N+3.41 source-check snapshot for "all the things we have been talking about" in the Claude Code, Codex, MCP, OpenClaw, CUA, Paperclip, Ruflo, jobs, email, and connector backlog. The Everything Claude Code repo is preserved here as a quarantine-only source-check target, not as approved runtime code.

| Tool/concept | source_check_status | Likely purpose | Useful for Ghoti? | Risk | Install/connect now? | Safe next step | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Everything Claude Code exact repo/source | source found: `affaan-m/everything-claude-code` | Claude/Codex/OpenCode agent harness, skills, commands, hooks, MCP configs, memory/security patterns | yes, as pattern library | high supply-chain/hooks/MCP/script risk | no | quarantine source audit only; no execution | soon research |
| awesome-claudecode / awesome-claude-code | source found: `subinium/awesome-claude-code` and other curated lists | discovery of Claude Code tools, skills, plugins, MCP servers | yes | medium-high supply-chain | no | read list; select individual items for audit | soon research |
| Claude Code `/ultraplan` | official Claude docs found | cloud planning session, review in browser, execute remotely or return to terminal | yes | medium account/cost/cloud execution | no automatic use | use as planning only with approval | soon |
| Claude Code `/ultrareview` | official Claude docs found | cloud multi-agent bug review | yes | medium-high cost/cloud/account | no automatic use | use after human approval for big diffs | later/special |
| Codex background/cloud/parallel tasks | official OpenAI Codex docs found | parallel background coding in isolated environments | yes | medium branch/state drift | no automatic use | combine with lane locks | soon |
| Codex Goal exact named feature | exact official source unverified; community references found | long-running goal workflow | maybe | medium autonomy | no | keep as concept until official source | research |
| JobSpy MCP | source found: `borgius/jobspy-mcp-server` | MCP job search via JobSpy | maybe | high scraping/TOS/GDPR | no | legal/TOS audit only | research |
| `python-jobspy` | source found: PyPI package | scrape/aggregate job listings | maybe | high scraping/TOS/GDPR | no | manual official-route workflow first | research |
| Firecrawl MCP | official docs found | web search/scrape/browser sessions via MCP/API | yes, later | high scraping/API/account/credit | no | legal/TOS/API budget review | later |
| Glif MCP | source found: Glif/PulseMCP | run visual AI workflows | maybe | medium account/content/IP | no | source/TOS/pricing review | research |
| Chrome DevTools MCP | official Chrome docs found | browser debugging/perf/inspection for local apps | yes | medium browser/tool surface | no | local-only frontend testing plan | soon/later |
| Superpowers | source found: Anthropic plugin and `obra/superpowers` | disciplined planning, TDD, debugging, code review skills | yes | medium skill supply-chain if external install | already available in Codex env; no new install | use methodology when available | now/safe |
| Frontend design skills | source found: Claude frontend design skill/blog and community variants | improve UI quality | yes | medium third-party skill supply-chain | no new install | prefer official/curated, audit before use | soon |
| Code review/security review skills | source found: code-review-skill and security-review patterns | release quality and security gates | yes | medium third-party skill supply-chain | no new install | audit source; use official/curated where possible | soon |
| gstack | source found: `garrytan/gstack` references | opinionated Claude Code workflow/team roles | maybe | high hooks/browser automation/skills | no | source audit only | research |
| OpenClaw | source found: docs/site; autonomous agent platform | vital future worker/channel lane | yes | very high live-action/tool/account risk | no | isolated audit after lane locks | later/soon |
| Ruflo | source found from prior checks | multi-agent orchestration | yes, later | high autonomy/supply-chain | no | source audit only | research |
| CUA | source found: `trycua/cua` | computer-use agent sandboxes | yes, vital later | high desktop automation | no | sandbox-only screenshot/read tests after approval | later |
| PaperclipAI/paperclip | source found: `paperclipai/paperclip` | AI company/control-plane orchestration | yes, vital later | high autonomous business/workflow risk | no | isolated source/security audit | later/soon |
| agentcy-agents / agency-agents | source found: `msitarzewski/agency-agents`; exact user spelling likely typo | agent role library/agency prompts | yes | medium supply-chain/role quality | no | extract safe role patterns only | soon research |
| SalesMaxAI / SalesMax AI deals | source found: `salesmax.ai`, Salesmax app | CRM/deal workflow inspiration | maybe | high CRM/contact/payment/live-customer risk | no | feature/pricing/privacy review only | research |
| Everything Claude Code claims | source found; repo contains hooks/scripts/MCP/skills | potentially useful config patterns | maybe | high because broad repo can change behavior across tools | no | quarantine and read-only audit if approved | research |

## Security Notes

- Free/unlocked/leaked Claude Code repos remain quarantine/security-audit-only.
- Everything Claude Code is not the leaked Claude Code source, but it is still a broad third-party harness with scripts, hooks, MCP configs, and commands. Treat it as untrusted until audited.
- MCP servers are new trust boundaries. Firecrawl, Glif, Chrome DevTools, JobSpy, GitHub, and other MCPs must be connected one at a time, with read-only defaults and revocation notes.
- Browser automation and scraping tools require legal/TOS review before use.

## Current Recommendation

Highest practical source-check value:

1. N+3.32 implementation/audit first.
2. N+3.34 Obsidian/compact memory soon.
3. Then a quarantine-only source audit of Everything Claude Code, agency-agents, Superpowers, gstack, and official frontend/security skills.
4. Keep JobSpy, Firecrawl, OpenClaw, CUA, Ruflo, Paperclip, and SalesMaxAI out of runtime until safety rails exist.
