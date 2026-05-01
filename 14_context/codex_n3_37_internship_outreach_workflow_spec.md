# Codex N+3.37 Internship Outreach Workflow Spec

Status: codex_spec_only / legal_safe_drafting / no_sending

Date: 2026-05-01
Branch: feat/ghoti-visible-operator-stack

## Goal

Design a legal, ethical internship search and outreach workflow for the operator.

Target domains:

- Mechatronics
- robotics
- medical automation
- industrial automation
- defense and dual-use engineering, where lawful and appropriate
- embedded systems
- manufacturing automation

Core rule:

Volume comes from good tracking and personalization, not mass spam.

## Safety And Legal Baseline

This is not legal advice.

EU/GDPR caution:

- Use official application routes first.
- Prefer public company career portals and official contact pages.
- Avoid private personal email harvesting.
- Do not scrape at scale.
- Keep records minimal and relevant.
- Respect opt-out requests.
- For EU outreach, verify lawful basis and national ePrivacy rules before sending.

Source checked:

- European Commission lawful basis and GDPR pages: https://commission.europa.eu/law/law-topic/data-protection/rules-business-and-organisations/legal-grounds-processing-data_en
- European Commission legitimate interest page: https://commission.europa.eu/law/law-topic/data-protection/rules-business-and-organisations/legal-grounds-processing-data/grounds-processing/what-does-grounds-legitimate-interest-mean_en

## Workflow Overview

1. Build company list
2. Rank fit
3. Identify official application route
4. Prepare normal application material
5. Prepare optional personalized outreach draft
6. Human review
7. Human manually sends if appropriate
8. Track status
9. Follow up manually and politely
10. Archive or stop

## Company Discovery

Allowed sources:

- official company websites
- career pages
- university career boards
- LinkedIn public company pages, manually reviewed
- internship portals
- official job boards
- conference/exhibitor lists where terms allow
- local chambers or robotics/automation directories

Forbidden by default:

- scraping personal emails
- buying lead lists
- scraping private social profiles
- bypassing platform limits
- automated LinkedIn messaging
- automated email sending

## Fit Ranking

Company fit fields:

```text
company_id:
company_name:
website:
country:
city:
industry:
relevance:
mechatronics_fit:
robotics_fit:
medical_automation_fit:
defense_or_dual_use_fit:
automation_fit:
language_fit:
visa_or_work_auth_notes:
internship_page:
official_application_url:
public_contact_url:
risk_notes:
priority_score:
```

Scoring dimensions:

- technical fit
- location fit
- internship availability
- portfolio relevance
- learning value
- application route clarity
- ethical/legal comfort

## Official Route First

For every company, Ghoti should check:

1. Does an internship page exist?
2. Is there a specific job posting?
3. Is there a general student application form?
4. Is there a recruitment email listed publicly?
5. Is there a contact form?
6. Is there a named recruiter only on official pages?

If an official application route exists, use that first.

## Outreach Drafting

Outreach drafts must be:

- short
- personalized
- factual
- not manipulative
- not mass-blasted
- clear about why the company fits
- clear about what the operator can contribute
- easy to ignore
- never sent automatically

Draft variants:

- recruiter note
- hiring manager note
- founder/CTO note for small companies
- professor/lab note
- alumni/network warm intro note

## High-Rank Outreach Caution

High-rank or executive outreach can be useful only when:

- the company is small enough that this is normal
- the note is very short and respectful
- there is a legitimate public business contact route
- the operator has a strong specific reason for contacting that person

Avoid:

- personal/private addresses
- repeated follow-ups
- pressure tactics
- flattery spam
- mass executive blasts

## Application Material Pack

For each target:

```text
company_brief.md
fit_rationale.md
resume_tailoring_notes.md
cover_letter_draft.md
portfolio_project_selection.md
outreach_draft_optional.md
operator_review_checklist.md
status_record.json
```

## Tracking Model

Suggested local JSONL:

```text
14_context/career_workflows/internship_targets.jsonl
```

Fields:

```text
target_id
created_at
company_name
website
country
city
industry
fit_score
official_application_url
public_contact_channel
application_status
last_action
next_manual_action
follow_up_date_optional
materials_path
human_approved_before_send
notes
```

## Human Approval Gate

Before every send:

```text
APPROVE MANUAL INTERNSHIP OUTREACH FOR <target_id>
```

This approval only records review. Ghoti must not send.

## What Gemma Can Do

Gemma/Ollama may:

- summarize local company notes
- draft fit rationale
- rewrite cover letter drafts
- classify risk
- create checklists
- compress target notes

Gemma must not:

- scrape websites
- send emails
- access accounts
- invent facts
- fabricate experience
- generate fake references

## What Claude Code Can Do Later

Claude Code may later implement:

- local target tracker templates
- local draft generation helper
- read-only dashboard card
- status summaries

Only after approval:

- no live email integration
- no LinkedIn automation
- no scraping workflows

## What Codex Should Do

Codex should:

- audit target workflow logic
- review legal/safety gates
- compare tools
- write implementation specs

## Verdict

Internship outreach is a good Ghoti lane if it stays official-route-first, human-sent, personalized, and legally cautious. Do not build mass sending or scraping. Build tracking and draft quality first.
