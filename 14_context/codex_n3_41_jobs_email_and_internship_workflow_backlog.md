# N+3.41 Jobs, Email, And Internship Workflow Backlog

Status: Codex backlog/spec only.
Date: 2026-05-05

Ghoti should help the operator find internships/jobs ethically, especially in Mechatronics, robotics, medical automation, defense, automation, and related engineering fields. This job/internship email client concept must remain research/draft-only until the operator approves each external action.

## Source-Checked Candidates

| Tool/concept | Source-check status | Notes | Current verdict |
| --- | --- | --- | --- |
| JobSpy MCP | source found: `borgius/jobspy-mcp-server` | MCP wrapper around JobSpy for job search across job boards | research-only |
| `python-jobspy` | source found: PyPI `python-jobspy` | Scrapes/aggregates Indeed, LinkedIn, Glassdoor, ZipRecruiter, Google Jobs, Bayt, Naukri | research-only until legal/TOS gate |
| JobSpy APIs/workers | source found | Hosted scrape APIs exist, but add API/cost/data risk | reject live use for now |

## Core Workflow

1. Identify target roles.
2. Search official company career pages first.
3. Use public job boards manually or through approved, ToS-compliant tooling only.
4. Rank fit for Mechatronics / robotics / medical automation / defense / automation.
5. Build a status tracker.
6. Draft application materials.
7. Draft personalized outreach only when appropriate.
8. Human reviews every message and application.
9. Human sends manually or explicitly approves a future send workflow.
10. Log results and follow-ups.

## Official Route First

For each company:

- Find official careers page.
- Find official internship program page.
- Find official application portal.
- Prefer the official application route over cold outreach.
- Do not bypass applicant systems.
- Do not spam employees if an official route exists.

## Fit Scoring

Score each opportunity 1-5:

- role_fit
- location_or_remote_fit
- visa_or_work_authorization_fit
- Mechatronics_fit
- robotics_fit
- medical_automation_fit
- defense_or_security_fit
- automation_fit
- project_alignment
- application_deadline_urgency
- networking_signal

Output:

- total_fit_score
- priority_bucket: A/B/C/D
- next_manual_action

## Public Company/Contact Research

Allowed:

- official careers pages
- official company contact pages
- public recruiting emails listed by the company
- public LinkedIn/company pages read manually
- conference/event pages
- university career fair pages

Forbidden without legal/TOS review:

- private personal email harvesting
- scraping LinkedIn
- scraping job boards
- buying email lists
- bypassing rate limits or auth
- using browser automation against logged-in accounts
- mass profile collection

## Outreach Draft Structure

Subject lines should be short and specific:

- `Mechatronics internship - robotics automation portfolio`
- `Robotics internship question - Ivan Fuentes`
- `Medical automation internship fit`
- `Automation engineering internship inquiry`

Email body should be concise:

- One sentence context.
- Three bullets showing fit, credentials, and project proof.
- One clear ask.
- Polite close.
- No hype, fake urgency, fake connection, or exaggerated claims.

## Connection Signals To Find

Only use truthful, public signals:

- same school or alumni network
- public event attendance
- career fair
- mutual technical interest
- company tech stack
- robotics/automation product line
- medical device or lab automation focus
- defense/security compliance relevance
- published internship program
- public recruiter or careers contact

Never invent a connection.

## Email Client Rules

Future email workflow:

- may draft emails locally
- may read only after explicit account connector approval
- may never send without human approval
- must show exact recipient, subject, body, attachments, and reason before send
- must log every approval and send
- must support cancellation
- must not mass-send
- must not hide unsubscribe/legal requirements where commercial

User's real email may be used only with explicit approval for that task. Future Ghoti-owned email may exist only after the account strategy is approved.

## Legal And Platform Gates

Source-check notes:

- FTC CAN-SPAM guidance applies to commercial email and sets requirements for truthful headers/subjects, identification, opt-out, and sender address.
- LinkedIn terms prohibit unauthorized scraping/data extraction and automation.
- Job board scraping may violate terms even when data is publicly visible.
- GDPR/European outreach requires careful lawful basis, data minimization, transparency, and respect for objections.

## First Safe Local Experiment

Create a local tracker with 20 companies:

- company
- official careers URL
- internship URL
- role title
- fit scores
- connection signals
- application deadline
- official application route
- outreach draft needed yes/no
- human_review_status
- next_manual_action

No scraping, no email sending, no account connection.

## Current Recommendation

Jobs/internship workflow is soon/high-value, but JobSpy and MCP job scraping remain research-only. Start with manual official-route research and local draft emails, then evaluate JobSpy only after a legal/TOS/GDPR gate.
