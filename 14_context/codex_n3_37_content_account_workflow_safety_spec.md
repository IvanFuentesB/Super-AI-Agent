# Codex N+3.37 Content Account Workflow Safety Spec

Status: codex_spec_only / no_live_accounts / no_posting

Date: 2026-05-01
Branch: feat/ghoti-visible-operator-stack

## Goal

Design a future safe content-channel workflow for Ghoti that supports many experiments without crossing into unsafe autonomy.

Core money principle:

- many channels
- many content shots
- many product experiments
- fast feedback
- honest metrics
- no fake engagement
- no public action without human approval

## Future Workflow Scope

Channels:

- YouTube Shorts
- YouTube long-form
- TikTok
- Instagram Reels
- X/Twitter
- LinkedIn
- Reddit/community posts where allowed
- email list

Content types:

- short-form scripts
- long-form outlines
- thumbnails
- titles
- descriptions
- hashtags
- calls to action
- email lead magnets
- repurposing maps
- batch calendars

## Local-First Asset Flow

All assets should be drafted locally first:

```text
14_context/money_workflows/content_batches/
11_exports/content/<channel_or_experiment_slug>/
05_logs/content_batches/<run_id>/
```

Example local artifacts:

```text
script_batch.md
thumbnail_brief.md
metadata_draft.md
repurposing_map.md
posting_calendar_draft.md
claims_review.md
operator_review_checklist.md
run_summary.json
```

## Style Consistency

Each channel should have a local style card:

```text
channel_name:
target_audience:
tone:
visual_style:
forbidden_claims:
cta_style:
posting_frequency_target:
examples_to_reference:
examples_to_avoid:
review_status:
```

Gemma may draft style cards from local notes, but the operator must approve canonical style.

## Batch Planner Requirements

Future content planner outputs:

- 30 hooks
- 10 scripts
- 10 thumbnail/title concepts
- 10 metadata drafts
- 5 CTA variants
- 5 lead magnet ideas
- repurposing map
- platform-specific safety notes
- human review checklist

The planner must not:

- log into accounts
- post
- schedule
- send DMs
- scrape comments
- buy ads
- create accounts
- impersonate people
- fabricate proof
- generate child-targeted deceptive content

## Scheduling Drafts

Scheduling support is draft-only:

```text
date:
platform:
asset_path:
title:
caption:
cta:
approval_required: true
manual_post_only: true
```

No direct integration with YouTube, TikTok, Instagram, Meta, X, or scheduling tools until a separate explicit approval milestone.

## Metrics Intake

Metrics should be manually recorded:

```text
content_id:
platform:
posted_url:
date_posted:
impressions:
views:
watch_time:
clicks:
opt_ins:
comments:
shares:
sales:
notes:
```

No automated scraping or account API reads by default.

## Human Review Checkpoints

Required before publishing:

1. Claims review
2. IP/copyright review
3. Platform policy review
4. Audience safety review
5. CTA/offer review
6. Final operator approval

Suggested approval phrase:

```text
APPROVE MANUAL CONTENT POST REVIEW FOR <content_batch_id>
```

This phrase does not authorize Ghoti to post. It only records that the operator reviewed the draft and may manually post externally.

## Kids / Kid-Adjacent Content

If content is for kids or kid-adjacent audiences, extra safety and platform compliance review is required before publishing.

Additional checks:

- no manipulative monetization
- no unsafe challenges
- no deceptive educational claims
- no collection of child personal data
- no targeted ads or funnels aimed at children
- comply with platform child-safety rules
- operator must manually review visuals, voice, thumbnails, and descriptions

Default recommendation:

Avoid kid-targeted monetized automation until Ghoti has a dedicated child-safety review checklist.

## Prohibited Tactics

Forbidden:

- fake engagement
- fake testimonials
- fake scarcity
- fake income claims
- comment bots
- DM bots
- mass account creation
- account farming
- scraping comments or profiles at scale
- using copyrighted characters/IP without permission
- deepfake likeness use without explicit consent
- medical/financial/legal guarantees

## Safe Future Implementation

Start with:

- local content batch templates
- local style cards
- read-only dashboard cards
- manual metrics intake
- Gemma draft-only hooks/scripts

Do not start with:

- account APIs
- scheduler integrations
- auto-posting
- comment scraping
- paid ads
- child-targeted funnels

## Verdict

Ghoti can safely help produce many content shots if the system remains local-first, draft-only, and human-reviewed. The dashboard should track progress and metrics, not execute public actions.
