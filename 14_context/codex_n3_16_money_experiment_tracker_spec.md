# Codex N+3.16 Money Experiment Tracker Spec

Status: codex_planning_audit_only / tracker_spec / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Purpose

Define a future tracker that Claude Code can implement later. The tracker should make the money workflow measurable: many shots, scored consistently, reviewed regularly, and killed or scaled based on evidence.

## Required Fields

| Field | Type | Notes |
| --- | --- | --- |
| `experiment_id` | string | Stable ID, for example `money_20260428_001`. |
| `date_created` | string | ISO date. |
| `niche` | string | Target niche or market. |
| `hypothesis` | string | What we think will happen and why. |
| `product_or_content_type` | string | Product, short, long video, email lead magnet, offer, etc. |
| `target_audience` | string | Buyer/viewer/customer. |
| `distribution_channel` | string | TikTok, YouTube, email, Whop, Gumroad, LinkedIn, Reddit, etc. |
| `asset_required` | string | Minimum asset needed to test. |
| `effort_score` | number | 1 low effort to 5 high effort. |
| `upside_score` | number | 1 low upside to 5 high upside. |
| `speed_score` | number | 1 slow to 5 fast. |
| `confidence_score` | number | 1 uncertain to 5 confident. |
| `risk_score` | number | 1 low risk to 5 high risk. |
| `expected_learning` | string | What the user learns even if it fails. |
| `approval_required` | array/string | Required approvals before external action. |
| `status` | string | `idea`, `selected`, `asset_draft`, `approval_needed`, `published`, `measuring`, `done`, `blocked`. |
| `published_url` | string | URL or blank. |
| `manual_reference` | string | Local file path or manual note if no URL. |
| `metrics` | object | Impressions, clicks, opt-ins, replies, sales, revenue, time spent. |
| `decision` | string | `scale`, `iterate`, `pause`, `kill`. |
| `notes` | string | Compact notes and links to artifacts. |

## Metrics Fields

```json
{
  "impressions": 0,
  "clicks": 0,
  "opt_ins": 0,
  "replies": 0,
  "sales": 0,
  "revenue": 0,
  "time_spent": 0
}
```

`time_spent` should use minutes or hours consistently. Revenue should include currency in the surrounding record or notes.

## Scoring Formula

```text
priority_score = (upside_score + speed_score + confidence_score - risk_score) / effort_score
```

Interpretation:

- High upside, speed, and confidence increase priority.
- High risk decreases priority.
- High effort reduces priority.
- Low-risk fast tests should rise to the top.

## JSONL Format

Recommended future file:

`14_context/money_workflows/experiment_tracker.example.jsonl`

Example:

```json
{"experiment_id":"money_20260428_001","date_created":"2026-04-28","niche":"AI operator templates","hypothesis":"Builders will want a simple AI operator starter kit because setup and safety are confusing.","product_or_content_type":"digital_product","target_audience":"AI builders and students","distribution_channel":"manual audience + future Gumroad/Whop","asset_required":"markdown template bundle","effort_score":2,"upside_score":4,"speed_score":5,"confidence_score":4,"risk_score":1,"priority_score":6.0,"expected_learning":"Whether operator templates are a clear buyer promise.","approval_required":["pricing","publishing","platform account"],"status":"idea","published_url":"","manual_reference":"14_context/money_workflows/ai_operator_starter_kit/","metrics":{"impressions":0,"clicks":0,"opt_ins":0,"replies":0,"sales":0,"revenue":0,"time_spent":0},"decision":"pause","notes":"Draft locally first; no live store action."}
```

Why JSONL:

- append-friendly
- easy to diff
- easy to parse later
- works without database setup
- safe for Claude Code to generate and validate

## Markdown Table Format

Recommended for human overview:

| ID | Niche | Hypothesis | Channel | Effort | Upside | Speed | Confidence | Risk | Priority | Status | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| money_20260428_001 | AI operator templates | Builders want starter kit | Manual / future Whop | 2 | 4 | 5 | 4 | 1 | 6.0 | idea | pause |

## Dashboard Card Format

Future dashboard card:

```json
{
  "experiment_id": "money_20260428_001",
  "title": "AI Operator Starter Kit",
  "niche": "AI operator templates",
  "priority_score": 6.0,
  "status": "idea",
  "next_action": "Draft markdown MVP",
  "approval_required": ["publishing", "pricing"],
  "blocked_reason": "",
  "metrics_summary": "0 impressions / 0 sales / not published",
  "risk_label": "low"
}
```

## Later SQLite Format

SQLite can come later if JSONL grows too large. Suggested tables:

- `experiments`
- `metrics_snapshots`
- `approvals`
- `assets`
- `decisions`

Do not start with SQLite. JSONL and markdown are enough for the first money OS.

## Decision Rules

- `scale`: metrics show real pull or the user has high conviction and low cost.
- `iterate`: weak but useful signal; improve hook, offer, or channel.
- `pause`: blocked by approval, missing asset, or low energy.
- `kill`: too risky, too much effort, no signal, or violates safety/TOS.

## Approval Rules

Tracker entries can be created freely as local docs. Approval is required before:

- publishing URLs
- sending outreach
- spending money
- using accounts
- collecting data from platforms beyond allowed manual/public use
- adding affiliate links
- creating store listings

## Implementation Recommendation

Claude Code should implement templates first:

- `experiment_tracker.example.jsonl`
- `experiment_tracker.schema_notes.md`
- `experiment_tracker.md`

No automation, posting, scraping, or account actions should be included in the first implementation.
