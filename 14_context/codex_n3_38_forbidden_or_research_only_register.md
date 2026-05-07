# N+3.38 Forbidden Or Research-Only Register

Status: Codex safety/backlog only.
Date: 2026-05-01

This register defines tools and ideas that must not be used directly yet. Some may be researched in a narrow, non-executing, source-only way. Others are rejected outright.

| Tool/idea | Why risky | Allowed safe version | Approval required | Future review condition |
| --- | --- | --- | --- | --- |
| free-claude-code/unlocked Claude Code repos | Likely bypass, stolen code, malware, auth/cap evasion, or account risk | Security-audit-only notes; do not clone/install/run | Not approved for use | Only reconsider if official/legal provenance is proven |
| Leaked/stolen/private Claude Code code | Unauthorized and unsafe | None | Not approvable | Never use |
| OBLITERATUS / guardrail removal tools | Encourages bypassing safety/legal constraints and unsafe autonomy | Source-only risk notes | Not for Ghoti runtime | Only discuss as a thing not to connect |
| Unrestricted local LLM lane | Could be used for harmful or unlawful bypasses | Legitimate local analysis only, no bypass use | Human safety approval | Define lawful use cases and audit outputs |
| Scraping tools without legal/TOS review | Can violate platform rules, privacy, copyright, or law | Manual source review and robots/TOS/legal checklist | Per target/source approval | Legal/TOS gate and data-minimization plan |
| cobalt.tools downloads | Downloading media can violate copyright or platform terms | Research legality and permitted sources only | Per download/use approval | Explicit rights/TOS confirmation |
| OSINT tools | Can expose sensitive data, privacy risk, or unlawful targeting | Defensive/security research notes only | Explicit security/legal approval | Narrow lawful scope, no live targeting |
| Live-account automation | Can cause account bans, unauthorized actions, and user harm | Local drafts/checklists only | Explicit per-account approval | Read-only first, then gated manual actions only |
| Posting/account creation/selling/payment tools | Public and money-facing consequences | Draft assets and approval checklists only | Human approval before each public action | Manual execution and metrics logging |
| Email outreach automation | Spam, privacy, deliverability, GDPR, and reputation risk | Personalized draft generation and manual send only | Human approval before every send | Legal/GDPR review and rate limits |
| Job/internship mass-emailing | Spam and reputational harm | Official applications and personalized approved outreach | Human approval before every send | Tracking and personalization proof |
| Subscription/cap/auth/captcha bypass | Violates terms and can be illegal | None | Not approvable | Never use |
| Fake proof/testimonials/engagement | Deceptive and platform-risky | Honest metrics and proof only | Not approvable | Never use |
| Autonomous real-money trading/investment | Financial risk and regulatory concerns | Manual research templates, no advice/automation | Human/qualified review | No autonomous trading |
| Decepticon repo | Unknown and likely adversarial/security-adjacent | Source-only risk audit | Security approval | Exact source and risk assessment |
| DollFactory AI | Possible privacy, age, consent, and adult/companion risks | Source-only market/safety research | Human approval | Safety and platform review |
| Multiple MCP servers | Tool-surface expansion can expose write/shell/network risk | Read-only source audits one at a time | Explicit MCP approval | Tool list, permissions, and threat model |

## Safe default

If a tool claims to unlock, bypass, scrape, download, spam, mass-create accounts, remove guardrails, evade subscriptions, or automate public/money-facing actions, it is rejected or research-only by default.
