# ghoti-business-research-safe

**Status:** skill_package_created / not_runtime_wired
**Created:** 2026-04-25
**Branch:** feat/ghoti-visible-operator-stack

---

## Purpose

Support legitimate business research, market analysis, content planning, store/e-commerce research, public-source OSINT, and decision-support workflows while keeping Ghoti local-first, supervised, legal, TOS-aware, and approval-gated.

This skill is for research and planning only. It does not authorize autonomous outreach, posting, purchasing, scraping, account creation, trading, investing, legal filing, tax filing, or external service use.

---

## When to Use

Use this skill for safe versions of:

- Market research.
- Competitor research using public sources.
- Product idea validation.
- Store/e-commerce niche research.
- Content/channel idea research.
- SEO and AI SEO research.
- Business model comparison.
- Pricing, revenue, and cost assumptions.
- Investment simulations and scenario analysis with disclaimers.
- Lead list research only when legal, public, non-spam, and no automated outreach occurs.
- Drafting outreach for human review only.
- Public-source OSINT only when legal, authorized, and not used for harm.

Use it before creating reusable prompt packages for business, money, content, store, investment, lead, OSINT, or growth workflows.

---

## Forbidden Uses

Never use this skill to support:

- Fake engagement, fake followers, fake reviews, fake clicks, or engagement pods.
- Mass spam, bulk unsolicited outreach, phone farm automation, or ban evasion.
- Fake accounts, account farming, deceptive personas, or deceptive impersonation.
- Bypassing platform limits, caps, quotas, rate limits, or safety systems.
- Credential theft, credential abuse, account takeover, or phishing.
- Unauthorized scraping or scraping against law, robots.txt, site terms, or platform policy where not allowed.
- Autonomous sending, posting, commenting, DMing, emailing, calling, or outreach.
- Autonomous payments, purchases, refunds, chargebacks, trades, investments, or money movement.
- Autonomous legal, tax, permit, visa, employment, medical, or regulated filings.
- Regulated financial, legal, tax, medical, or safety advice presented as professional advice.
- Doxxing, harassment, stalking, intimidation, or targeting private individuals.
- Malware, phishing, social engineering, exploit development, credential harvesting, or evasion.
- Unsafe weapon, aerospace, guided rocket, or harmful implementation guidance.
- Using local "less restricted" models to bypass safety, law, platform rules, or consent.

If a request drifts into any of these, stop and switch to the recovery behavior.

---

## Human Approval Gates

Human review is required before any external or consequential action, including:

- Sending outreach, email, DM, comments, posts, proposals, or applications.
- Creating accounts, editing profiles, uploading content, or publishing.
- Purchasing products, ads, subscriptions, domains, or tools.
- Starting paid API usage, cloud jobs, data providers, or SaaS trials.
- Using personal data, lead data, or scraped data.
- Making investment, tax, legal, hiring, firing, medical, safety, or compliance decisions.
- Contacting real people or organizations.

Default output should be draft/research only, with a clear `human_review_required` label.

---

## Source And Evidence Rules

Research outputs must include:

- Source list with URLs, filenames, or clearly labeled local evidence.
- Date of access when useful.
- What was directly observed vs inferred.
- Confidence level or uncertainty notes.
- Assumptions for market size, pricing, revenue, cost, or conversion estimates.
- Missing evidence and suggested next safe checks.

Do not fabricate sources, quotes, metrics, testimonials, traffic estimates, or financial results.

---

## Legal / TOS-Aware Research Rules

Research must stay legal, TOS-aware, and approval-gated.

Allowed:

- Manually reviewing public web pages.
- Reading public docs, public pricing pages, public app/store pages, and public social/media profiles.
- Using official APIs only when credentials and terms are approved by the operator.
- Summarizing public information with citations or source notes.

Not allowed:

- Circumventing paywalls, logins, bot protections, CAPTCHAs, rate limits, or access controls.
- Ignoring robots.txt or explicit platform restrictions for scraping.
- Collecting private data without authorization.
- Using leaked, stolen, or credential-protected data.

---

## Privacy / PII Rules

Minimize personal data.

Rules:

- Prefer company-level or aggregate research.
- Use public professional contact data only when legally and ethically appropriate.
- Do not enrich, deanonymize, or profile private individuals without a legitimate, approved purpose.
- Do not collect sensitive personal data such as health, financial, biometric, political, religious, sexual, or protected-class attributes.
- Do not output doxxing material or harassment targets.
- Redact secrets, credentials, tokens, and private identifiers.

---

## Outreach Boundaries

Allowed:

- Drafting outreach for human review.
- Preparing personalization notes from public, relevant, non-sensitive business context.
- Creating review checklists and approval steps.
- Producing small, manually reviewed lead research tables from legal public sources.

Forbidden:

- Autonomous outreach.
- Bulk unsolicited messages.
- Spam sequences.
- Fake personalization.
- Deceptive claims, impersonation, urgency manipulation, or false scarcity.
- Auto-follow, auto-like, auto-comment, auto-DM, or engagement manipulation.

Every outreach draft must be labeled:

```text
Draft only. Human review and explicit approval required before sending.
```

---

## Scraping Boundaries

Allowed:

- Manual public-source review.
- Small, operator-approved collection from sources where access is legal and allowed.
- Official APIs or exports when authorized.
- Local parsing of files the operator owns or has permission to use.

Forbidden:

- Unauthorized scraping.
- Scraping against robots.txt or platform terms where disallowed.
- Circumventing CAPTCHAs, login walls, paywalls, anti-bot systems, rate limits, or IP blocks.
- Mass harvesting personal data.
- Scraping for spam, fraud, phishing, harassment, fake engagement, or ban evasion.

If scraping legality/TOS is unclear, stop and ask for explicit approval or switch to manual high-level research.

---

## Paid Tool / Cloud Service Boundaries

Do not connect paid/cloud services unless the user explicitly approves:

- Billing scope.
- Account/provider.
- API key handling.
- Data sent.
- Expected cost.
- Shutdown/cleanup plan.

No Vercel, Neon, Cloudflare, Sentry, Hugging Face, Cloudinary, ad platforms, email tools, payment processors, or paid data providers should be connected by default.

---

## Financial / Investment / Tax / Legal Boundaries

Allowed:

- Paper simulations.
- Scenario analysis.
- Educational comparisons.
- Risk notes.
- Assumption-driven spreadsheets.
- Decision-support summaries with disclaimers.

Forbidden:

- Autonomous trades or investment decisions.
- Money movement.
- Personalized financial advice presented as professional advice.
- Tax/legal filings.
- Contract, permit, compliance, or legal submissions without qualified human review.

Required label:

```text
Decision-support only. Not financial, legal, tax, medical, or professional advice. Human review required.
```

---

## Store / E-Commerce Research Boundaries

Allowed:

- Niche research.
- Competitor store comparisons.
- Public product page review.
- Pricing, margin, and cost assumptions.
- Supplier research from public sources.
- Store UX teardown.
- Product validation plan.

Forbidden:

- Autonomous purchases.
- Fake orders.
- Fake reviews.
- Supplier impersonation.
- Ad spend without explicit approval.
- Payment processor setup without explicit approval.
- Scraping marketplaces in violation of terms.

---

## Content Factory / YouTube / Social Media Boundaries

Allowed:

- Content idea research.
- Channel positioning.
- Script outlines.
- SEO and AI SEO keyword research.
- Editing checklists.
- Content calendar drafts.
- Owned-account content drafts for human review.

Forbidden:

- Autonomous posting.
- Fake engagement.
- Reuploading copyrighted content without rights.
- Misleading deepfakes or impersonation.
- Comment/DM automation.
- Ban evasion.
- Phone farm automation.
- Scraping private platform data.

Every content output must distinguish:

- `draft`
- `research`
- `needs_human_review`
- `ready_to_publish_only_after_operator_approval`

---

## OSINT / Security Research Boundaries

Allowed:

- Public-source OSINT for legitimate, authorized, defensive, or journalistic-style research.
- Company-level risk notes.
- Public breach/news summaries without exposing sensitive details.
- Security ownership or repo-risk mapping when authorized.

Forbidden:

- Doxxing.
- Harassment.
- Targeting private individuals.
- Credential harvesting.
- Phishing or social engineering.
- Exploit chaining for harm.
- Malware.
- Evasion.
- Unauthorized vulnerability probing.

If the target or authorization is unclear, stop and ask for clarification.

---

## Required Workflow

1. Classify the request:

```text
market_research | competitor_research | product_validation | ecommerce_research | content_research | seo_research | investment_simulation | lead_research | outreach_draft | osint_security | other
```

2. State safety label:

```text
research_only / human_review_required / not_runtime_wired
```

3. Identify boundaries:

- What is allowed.
- What is forbidden.
- Whether external services, paid tools, personal data, scraping, outreach, or financial/legal/tax implications are involved.

4. Gather sources legally and transparently.
5. Separate facts, inferences, assumptions, and recommendations.
6. Produce draft/research artifacts only.
7. Add human review checkpoint.
8. List blocked or deferred actions.
9. Record files created/updated if working in repo.

---

## Required Final Report Format

```markdown
- research type:
- status label: research_only / human_review_required / not_runtime_wired
- sources used:
- key findings:
- assumptions:
- risks / uncertainty:
- forbidden actions avoided:
- human approval required before:
- files created/updated:
- runtime wiring truth:
- next safe step:
```

---

## Recovery Behavior If A Request Becomes Risky

If the request asks for or drifts into forbidden territory:

1. Stop the risky part.
2. State the exact boundary crossed.
3. Offer a safe alternative, such as:

- high-level market research
- compliance-aware checklist
- human-reviewed draft
- public-source summary
- paper simulation
- risk assessment
- manual review workflow

4. Do not execute external actions.
5. Do not collect or expose private data.
6. Do not use local models or plugins to bypass the boundary.

Example:

```text
I cannot help automate fake engagement or spam outreach. I can help create a human-reviewed content calendar, public-source audience research, or a compliant outreach draft checklist instead.
```

---

*Status: skill_package_created / not_runtime_wired*

*This skill is a Codex operator-side workflow document. It is not wired into the Ghoti runtime, dashboard, approval queue, MCP server, external services, browser executor, or outreach executor.*
