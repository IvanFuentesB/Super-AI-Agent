# Codex N+3.15 Money Workflow Backlog

Status: codex_audit_plan_only / money_workflow_backlog / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Purpose

Build a practical backlog of Ghoti workflows that can help the user make money while preserving safety gates and reducing API spend. Gemma/Ollama should handle cheap local text work. Claude Code should handle implementation after scope approval. Codex should audit plans, risks, and feasibility. ChatGPT should remain the high-level planning brain.

## Operating Rules

- No autonomous posting, outreach, purchases, trades, payments, legal/tax filings, or live-account actions.
- No fake engagement, spam, deceptive impersonation, platform cap bypass, or account abuse.
- No scraping beyond legal/TOS-safe public-source use.
- No paid tools, cloud APIs, or platform accounts connected without explicit approval.
- Gemma output is advisory only and must not be executed as code or external action.
- Business claims, pricing, and regulated advice require human review.

## Master Backlog

| Workflow | Why it can make money | Required tools | What Gemma can do | What Claude Code should do | What Codex should do | User approvals | Risks / legal / TOS notes | Difficulty | Expected first MVP | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Money-making video watcher/summarizer | Turns high-volume business videos into compact ideas and action lists without burning premium tokens. | YouTube URL, transcript/manual notes, local markdown artifacts, Gemma. | Summarize transcript, extract claims, tools, steps, warnings, and low-risk TODOs. | Later build repo-local templates and optional local intake CLI. | Audit whether the business model is feasible and not spammy. | Approve video source, niche, any external research, and any posting/spend. | Respect YouTube TOS; avoid downloading/scraping where not allowed; use manual transcript or approved source first. | Low | Manual transcript to `14_context/money_workflows/<slug>/video_summary.md`. | 95 |
| Video-to-business-system extractor | Converts random videos into repeatable systems, product ideas, and task queues. | Transcript, notes, risk template, product scoring template. | Extract system steps, required assets, tools, costs, content angles, product ideas. | Implement templates and optional Gemma compression route later. | Review logic, assumptions, and unsafe steps. | Approve which system becomes a project. | Avoid copying creators' products verbatim; use inspiration, not plagiarism. | Low-medium | One folder per video with summary, extracted model, action checklist, product ideas, content calendar, risk notes. | 94 |
| Digital product creation workflow | Fastest path to owned assets: prompt packs, checklists, templates, PDFs, Notion-style libraries. | Markdown templates, Gemma drafts, optional design/export later. | Draft outlines, rewrite notes, create checklists, create first-pass product copy. | Build file templates and later landing/product page scaffolds. | Audit positioning, differentiation, and claims. | Approve final product, pricing, platform, and listing. | Avoid false income claims, copyrighted copying, and regulated advice. | Low | One simple PDF/markdown bundle from existing Ghoti build knowledge. | 92 |
| Prompt pack / Notion template / PDF product workflow | Repackages knowledge into low-cost downloadable products. | Obsidian/vault notes, markdown templates, product scoring rubric. | Cluster notes into modules, draft prompts, create README/checklist. | Create product folder scaffolds and export-ready docs later. | Review quality and buyer promise. | Approve final copy, store platform, and pricing. | Avoid selling unverified results or misleading automation claims. | Low | "AI Operator Starter Kit" markdown bundle. | 90 |
| Whop clipping workflow | Clipping and creator-growth systems can pay through affiliate, rev-share, or service deals. | Creator brief, approved source videos, clip criteria, manual editor/tools. | Summarize long videos, identify hooks, draft clip titles/descriptions. | Later build clip candidate tracker and review queue. | Audit platform rules and monetization assumptions. | Approve creator, rights, posting account, captions, uploads, and outreach. | Rights/TOS risk; no reposting without permission; no fake engagement. | Medium | Manual clip-candidate spreadsheet/markdown queue. | 88 |
| Faceless short-form channel workflow | Shorts/Reels/TikTok can validate niches and drive affiliate/product funnels. | Topic backlog, scripts, AI asset tools, editor, manual posting. | Draft scripts, hooks, caption variants, content calendar. | Later build templates and content queue. | Audit niche saturation, rights, and claims. | Approve niche, platform account, final media, posting, spend. | Platform TOS, copyright, synthetic media disclosure, no spam. | Medium | 14-day content calendar plus 5 script drafts. | 84 |
| Faceless YouTube channel workflow | Longer-form content can build searchable assets and affiliate/product funnels. | Topic research, scripts, voice/video assets, thumbnail plan. | Summarize competitors, draft outlines, titles, hooks, checklists. | Later build episode template and asset tracker. | Audit feasibility and differentiation. | Approve niche, script, assets, posting, affiliate links. | Copyright, reused content policy, misleading claims. | Medium | One channel concept pack with 10 video ideas and first script outline. | 82 |
| AI video generation workflow using Higgsfield/Seedance/Kling/Arcads-style tools | Can produce ads, B-roll, product demos, and short-form creatives quickly. | External AI media tools, prompt library, rights checklist. | Draft prompts, shot lists, variants, and usage notes. | Later create prompt/product library templates. | Audit tool status, cost, rights, and deepfake risk. | Approve paid tool use, prompts, generated media, posting. | Paid/cloud services; synthetic likeness, IP, content policy, no cap bypass. | Medium-high | Research-only tool matrix and 10 safe prompt templates. | 78 |
| Local business lead-gen workflow | Productized websites/automation/checklists for small businesses can generate service revenue. | Public business research, offer template, review queue. | Draft improvement notes and outreach copy for review. | Later build local lead tracker and offer package templates. | Audit legal/TOS, claims, and targeting risk. | Approve leads, outreach text, sending, pricing, commitments. | No automated outreach, no scraping violations, no deceptive identity. | Medium | 10 manually researched leads with proposed improvement notes. | 76 |
| Service arbitrage workflow | Package AI-assisted content, websites, templates, or automation as services. | Offer catalog, delivery checklist, manual client comms. | Draft SOPs, proposals, deliverable checklists. | Later build service delivery templates. | Audit fulfillment risk and claims. | Approve offers, pricing, client messages, delivery promises. | Avoid overpromising, spam, fake testimonials, unpaid tool usage surprises. | Medium | One productized service page draft and fulfillment checklist. | 74 |
| Affiliate/content funnel workflow | Content can route attention to approved affiliate/product offers. | Niche research, affiliate policy review, content calendar. | Summarize offers, draft comparison outlines, risk labels. | Later build funnel docs and tracking templates. | Audit disclosure, claims, and platform rules. | Approve affiliate programs, links, final posts. | FTC disclosure, misleading claims, platform rules. | Medium | One ethical affiliate niche brief with 10 content ideas. | 72 |
| Marketplace research workflow | Finds sellable gaps for digital products or services. | Public marketplaces, manual notes, scoring rubric. | Summarize listings, compare features, extract buyer pains. | Later build product scoring templates. | Audit assumptions and legal copying risk. | Approve target marketplace and product concept. | No copying protected content; respect marketplace TOS. | Low-medium | Research report for one niche with 5 product ideas. | 70 |
| Portfolio/productized service workflow | Turns the user's Ghoti/mechatronics/AI build history into proof and offers. | Existing project docs, CV assets, portfolio template. | Summarize project wins, draft case-study bullets. | Later build portfolio page or service one-pager. | Audit positioning and claim accuracy. | Approve public claims and any publishing. | Privacy, employer/client confidentiality, truthful claims. | Low | One productized service one-pager. | 68 |

## Top 5 Recommended First Workflows

1. Video-to-business-system extractor.
2. Digital product / prompt pack workflow.
3. Money-making video watcher/summarizer.
4. Whop clipping workflow, manual and rights-safe first.
5. Faceless short-form content workflow.

## Why These First

They produce owned artifacts, use Gemma for cheap local work, require no new installs, and avoid live account automation. They also create reusable templates that can later feed Paperclip, n8n, OpenClaw, or dashboard queues after approval gates are proven.

## Deferred Until Stronger Gates Exist

- Automated posting or scheduling.
- Live Whop listing creation.
- Automated outreach.
- Paid AI media generation.
- Affiliate link insertion and tracking.
- Browser/CUA-driven account operations.
- Paperclip/OpenClaw/n8n runtime coordination.
