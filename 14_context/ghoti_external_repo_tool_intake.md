# Ghoti External Repo / Tool Intake Registry

Date: 2026-04-25
Branch: feat/ghoti-visible-operator-stack
Status label: registry_created / research_only / not_runtime_wired

Latest update: 2026-04-26 — RUFLO is TOP PRIORITY for multi-agent orchestration evaluation. AutoBrowser and Obscura are high-priority browser/operator candidates. Rust is verified/planned only; clone/install/runtime wiring still require explicit approval.

## Purpose

Track newly mentioned external repos, tools, services, and concepts before anyone clones, installs, pays for, deploys, or wires them into Ghoti.

This registry is an intake and evaluation surface only. It does not make any tool available to Ghoti runtime, does not authorize installations, and does not imply endorsement.

## Intake Rules

- Add ideas here before cloning or installing.
- Classify each item by use case, risk, priority, and next safe evaluation step.
- Prefer public docs/readme review before local clone.
- Do not touch `21_repos/third_party/**` unless a later milestone explicitly approves.
- Do not connect paid/cloud services without explicit user approval.
- Do not wire external tools into Ghoti runtime until a separate implementation milestone proves approval gates, logging, rollback, and local safety boundaries.
- Keep all business, content, OSINT, lead-gen, store, and finance work aligned with `ghoti-business-research-safe`.
- RUFLO, AutoBrowser, Obscura, and similar operator tools must be evaluated through `14_context/external_repo_evaluation_template.md` before clone/install.
- ChatGPT should carry most high-level reasoning/planning; Claude/Codex should be used for concrete repo execution, verification, and implementation when they are the better fit.

## Evaluation Gates Before Cloning / Installing

1. **Purpose gate:** What exact Ghoti capability would this support?
2. **Safety gate:** Could it enable spam, fake engagement, scraping abuse, credential risk, money movement, legal filing, or unsafe autonomy?
3. **License gate:** Is the license compatible with local research and possible future use?
4. **Maintenance gate:** Is the repo active, documented, and reasonably trustworthy?
5. **Runtime gate:** Does it require secrets, paid services, browser credentials, external accounts, GPUs, Docker, native installs, or background daemons?
6. **Approval gate:** Has the user explicitly approved clone/install/integration?
7. **Isolation gate:** Can it be evaluated as reference-only without modifying Ghoti runtime?
8. **Commit gate:** Are generated/runtime files ignored and excluded from staging?

## Safety / TOS / Legal Boundaries

- No spam, fake engagement, fake accounts, fake reviews, or platform-limit bypass.
- No credential theft, credential abuse, phishing, malware, evasion, or unauthorized access.
- No scraping that violates law, robots.txt, platform terms, or access controls.
- No autonomous posting, outreach, purchases, payments, trades, investments, or legal/tax filings.
- No professional financial/legal/medical advice without human review and disclaimers.
- No unsafe weapon, guided aerospace, or harmful implementation workflows.
- Public-source OSINT must be legal, authorized, privacy-aware, and non-harmful.
- Local or open models must not be used to bypass safety, law, or platform rules.

## Priority Tiers

### Use Soon

Items that may be useful after a read-only review and a narrow, approved follow-up milestone.

### Research Next

Items that are interesting but need docs/license/risk review before any clone or install.

### Watchlist

Items to remember, but not evaluate immediately.

### Do Not Use / Blocked

Items or use patterns that conflict with safety, legality, TOS, or Ghoti's supervised-only boundaries.

## Tool / Repo / Concept Table

| Item | Category | Priority | Current truth | Risk notes | Next safe step |
|---|---|---|---|---|---|
| RUFLO | Multi-agent orchestration | TOP PRIORITY | Mentioned only; not cloned, installed, or wired | Could enable multi-agent orchestration; must avoid account abuse, usage-limit bypass, broad filesystem permissions, and autonomous external actions | Use `14_context/ruflo_priority_evaluation_plan.md`; fill evaluation template before clone/install |
| `LvcidPsyche/auto-browser` | Browser automation repo | High priority | Mentioned only; not cloned or wired | Could expand browser control/autonomy; must remain supervised and approval-gated | Evaluate as supervised browser-control layer; read README/license only first |
| Obscura | Rust/headless browser candidate | High priority | Mentioned only; not cloned or wired | Headless/stealth-adjacent tools can create TOS, privacy, and cap-bypass risk | Research legal/TOS-aware use only; no stealth, evasion, or cap-bypass abuse |
| Rust install | Toolchain | Use soon | Verified available in `14_context/local_tool_readiness_check.md`; prior setup plan remains approval-gated | Native toolchain use can change build/runtime paths; no new install occurred in N+2.7 | Verify first, install only after explicit approval if missing in a future environment |
| `inventree/InvenTree` | Inventory/product/business ops | High priority | Mentioned only; not cloned or wired | Large app; may require Docker/database; not needed in runtime now | Evaluate for inventory/project hardware tracking, not runtime automation |
| Guri Singh GitHub/page | Person/reference | Watchlist | Mentioned only; no repo selected | Personal profile research may drift into privacy/PII | Only public professional review if a specific purpose is approved |
| Arcads AI | Content/ad creative tool | Watchlist | Mentioned only; no account/service connected | Paid/cloud/content generation; ad claims risk; no cap bypass or unlimited-generation abuse | Public feature/pricing research only |
| Kling 3.0 / Kling AI | Video generation tool | Watchlist | Mentioned only; no account/service connected | Paid/cloud media generation; rights/deepfake risks; no cap bypass or unlimited-generation abuse | Public capability/pricing research only |
| Higgsfield | Video/creative AI tool | Watchlist | Mentioned only; no account/service connected | Paid/cloud media generation; rights/deepfake risks; no cap bypass or unlimited-generation abuse | Public capability/pricing research only |
| Seedance | Video generation tool | Watchlist | Mentioned only; no account/service connected | Paid/cloud media generation; rights/deepfake risks; no cap bypass or unlimited-generation abuse | Public capability/pricing research only |
| OpenMontage | Content/video workflow | Research next | Mentioned only; not cloned or wired | Could affect content automation; AGPL/commercial implications may matter; must avoid reupload/copyright issues | Evaluate license, AGPL/commercial implications, and safe content boundaries first |
| Claude Council / contrarian / first-principles agent structures | Agent architecture concept | Use soon | Concept only; not runtime-wired | Could overclaim multi-agent autonomy | Capture as prompt pattern / review checklist first |
| Code review graph | Engineering analysis concept | Research next | Concept only; not runtime-wired | Could require repo mining; privacy/sensitive-code risks | Define local-only analysis scope |
| Apify | Scraping/automation platform | Research next | Mentioned only; no account/service connected | Scraping/TOS/paid cloud risks; must not become spam or unauthorized scraping | Evaluate later for jobs/internship/business research workflows, TOS-aware only |
| PRD requirement for projects/apps | Process concept | Use soon | Concept only | Low risk if used as docs process | Add PRD checklist before app/project builds |
| Supabase / Firebase | Backend/cloud platforms | Watchlist | Mentioned only; no service connected | Cloud, auth, billing, data exposure | Architecture comparison only until approved |
| Adapty.io | Subscription/paywall tool | Watchlist | Mentioned only; no service connected | Billing/app-store/payment implications | Public docs/pricing research only |
| Vercel | Deployment platform | Watchlist | Codex skill exists; not Ghoti runtime-wired | Deployment/billing/env-secret risk | Do not deploy unless user explicitly approves |
| Apple / game deployment | App distribution concept | Watchlist | Mentioned only | Paid accounts, review, legal/compliance | Research requirements only |
| Claude skill promotion / skills repo discovery | Workflow/distribution concept | Research next | Mentioned only | Could mix `.claude/skills` local artifacts into repo accidentally | Keep under strategy docs; do not stage `.claude/skills/` |
| Vercel Labs skills repo | Skills/reference repo | Research next | Mentioned only; not cloned | External repo license/quality unknown | Read public docs/repo before clone |
| Caveman Claude | Claude workflow/tool concept | Watchlist | Mentioned only | Unknown safety/quality | Identify exact source first |
| Token optimizer tools | Context/tooling concept | Research next | Mentioned only | Could over-optimize away safety context | Evaluate as summarization aid only |
| Context optimizer | Context/tooling concept | Research next | Mentioned only | Could lose important constraints | Use only with human-reviewed summaries |
| Token saver MCP | MCP/tooling concept | Research next | Mentioned only; not wired | MCP integration could affect runtime | Docs-only review first |
| Rust token killer | Tooling concept | Research next | Mentioned only; exact repo unknown | Native install/build risk | Identify exact repo; no install yet |
| Legalize / legal AI agent law repos | Legal AI research | Research next | Mentioned only | Legal advice and filing risk | Research-only with disclaimers; no filings |
| AI SEO / agent-trap / prompt-injection research | Safety/security/SEO concept | Research next | Mentioned only; no tools connected | Research target for understanding AI-indexed content, agent-visible SEO traps, and adversarial prompt injection in scraped content | Research-only; read public security/SEO research; capture safety patterns |
| AI agent traps | Safety/security concept | Use soon | Mentioned only | Could involve adversarial examples | Capture as safety checklist |
| Service arbitrage / local lead-gen ideas | Business research | Research next | Concept only | Spam/outreach/fake claim risk | Use `ghoti-business-research-safe`; draft only |
| Real-estate wholesaling-style ideas | Business research | Watchlist | Concept only | Legal/regulatory/ethics risk; jurisdiction-specific | Research-only; no outreach/contracts |
| Many single-purpose Claude agents with shared local memory | Agent architecture concept | High priority | Concept only; not runtime-wired | Could overclaim autonomy; memory privacy risk | Design local, supervised, role-labeled plan only; align with RUFLO evaluation |

## Do Not Use / Blocked Patterns

| Pattern | Reason |
|---|---|
| Phone farm automation | Fake engagement / platform abuse |
| Fake reviews, likes, comments, follows, or views | Manipulation and TOS abuse |
| Cap/quota bypass | Explicitly disallowed |
| Autonomous outreach or posting | Requires human review and approval |
| Autonomous purchases, trades, investments, or filings | Consequential action requiring human control |
| Scraping behind login/paywall/CAPTCHA/access controls | Legal/TOS/authorization risk |
| Doxxing or targeting private individuals | Privacy and harm risk |
| Unsafe aerospace/weapon implementation | Safety risk |

## Next Milestone Recommendations

1. **N+2.8: RUFLO docs/license evaluation** — fill `14_context/external_repo_evaluation_template.md` for RUFLO before any clone/install decision.
2. **N+2.9: AutoBrowser / Obscura comparison** — compare supervised browser-control candidates, legal/TOS boundaries, Windows feasibility, and sandbox needs.
3. **N+3.0: PRD checklist skill or doc** — make every app/project idea start with a small PRD and safety boundary.

## Current Status

- Registry status: `registry_created / research_only / not_runtime_wired`
- Cloned new repos: NO
- Installed new tools: NO
- Runtime wired: NO
- Paid/cloud services connected: NO
- Clone/install approval granted: NO
