# Codex N+3.15 Content Factory Tools and Routing

Status: codex_audit_plan_only / content_tool_routing / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Purpose

Map content, business, and agent tools mentioned in Ghoti notes so the project can use them intentionally. This is not an installation plan. It is a routing and risk map for future content-factory and money-workflow experiments.

## Tool and Workflow Routing Table

| Tool / concept | Use case | Status | Core Ghoti or experiments | API/token cost impact | Human approval required | Risk notes |
| --- | --- | --- | --- | --- | --- | --- |
| Higgsfield | AI video/image creative generation, ads, B-roll, short-form visuals. | Mentioned / needs verification. | External experiments first. | Likely paid/cloud credits. | Yes before account, paid use, or publishing. | Rights, likeness, deepfake, commercial license, platform policy. |
| Seedance | AI video generation candidate. | Mentioned / needs verification. | External experiments first. | Likely paid/cloud credits. | Yes. | Cost, rights, synthetic media disclosure, no cap bypass. |
| Kling | AI video generation candidate. | Mentioned / needs verification. | External experiments first. | Likely paid/cloud credits. | Yes. | Rights, account limits, no unsafe/deceptive media. |
| Arcads | AI ad/content factory candidate. | Mentioned / needs verification. | External experiments first. | Likely paid/cloud credits. | Yes. | Ad claims, likeness, paid service, platform rules. |
| Whop | Digital product/community/platform workflow target. | Known platform / not connected. | External business workflow, not core runtime. | Platform/payment fees later. | Yes before listing, account action, payment, upload. | No autonomous selling, no false claims, no account automation. |
| YouTube Shorts | Short-form distribution channel. | Known / no automation. | External channel workflow. | No API by default; possible editing/tool costs. | Yes before posting, account use, affiliate links. | Copyright, reused content, disclosure, spam. |
| TikTok | Short-form distribution channel. | Known / no automation. | External channel workflow. | No API by default; possible editing/tool costs. | Yes before posting. | Platform TOS, spam, rights, synthetic media policy. |
| Instagram Reels | Short-form distribution channel. | Known / no automation. | External channel workflow. | No API by default; possible editing/tool costs. | Yes before posting. | Platform TOS, spam, rights, account safety. |
| Paperclip | Future multi-agent control plane candidate. | Cloned/audited only if prior milestone did so; not runtime-wired. | Future orchestration experiment. | Could increase tool/runtime complexity. | Yes before install/run/control. | Must not receive broad filesystem, secrets, or live-account power early. |
| OpenClaw | Future worker/channel/personal assistant candidate. | Reference/planning only. | Future assistant-channel experiment. | Unknown until evaluated. | Yes before install/run/account use. | Channel credentials and public exposure risk. |
| n8n | Deterministic workflow rails. | Planning-only / not installed. | Future integration after workflow stabilizes. | Local or hosted costs depending deployment. | Yes before install, credentials, external actions. | Powerful automation can send/post/delete if misconfigured. |
| Gemma/Ollama | Local cheap/easy text brain. | Installed and ready per project truth: Ollama 0.9.2, gemma3:4b smoke passed. | Core local helper, but not autonomous operator. | API-free local compute; uses local CPU/GPU/time. | Approval needed for model pulls; inference for local text can be low-risk when scoped. | Output is untrusted advice; no execution from model text. |
| Claude Code | Hard implementation worker. | Available operator tool. | Main implementation lane. | Paid/API/credit cost. | User or task approval for high-risk actions, commits, pushes. | Must preserve file scopes and approval gates. |
| Codex | Audit, planning, verification, scoped repo changes. | Available operator tool. | Audit and code lane. | Paid/API/credit cost. | Approval for risky commands/actions. | Avoid conflicts with Claude lane. |
| ChatGPT | High-level planning and prompt generation. | Available coordination brain. | Strategy/handoff layer. | Paid/API/credit cost. | User controls prompt/handoff. | Keep handoffs compact to save tokens. |
| Skills/plugins | Operator-side capabilities for Codex/Claude sessions. | Available to sessions, not Ghoti runtime. | Operator workflow support. | Depends on skill/plugin. | Yes before external services. | Do not claim runtime wiring unless proven. |
| Prompt library / Notion-style library | Digital product and internal operating memory. | Ready to design locally. | Core docs/product workflow. | API-free if markdown/local. | Approval before selling/publishing. | Avoid unsafe prompts and overclaiming results. |
| Obsidian/vault memory | Compact markdown source of truth. | Local markdown plan exists. | Core memory/support layer. | API-free. | No special approval for local markdown edits. | Do not paste huge logs; no plugin/RAG needed yet. |
| Manual video transcript intake | Source for video-to-business pipeline. | Ready as manual process. | Core money workflow input. | API-free if user supplies transcript. | User approves source and transcript use. | Respect YouTube/platform TOS and copyright. |
| Postiz / social scheduling style tools | Later scheduling workflow. | Mentioned as future reference. | External experiments later. | Could be self-hosted or paid. | Yes before install/account/posting. | Posting automation needs strict approval and platform review. |

## Routing Rules

- Local draft, summary, checklist, and risk-label work goes to Gemma.
- Money strategy, positioning, and architecture go to ChatGPT plus Codex review.
- Repo implementation goes to Claude Code or Codex depending scope.
- Media generation tools stay external experiments until rights, cost, and posting gates are reviewed.
- Paperclip/OpenClaw/n8n remain planning-only until explicit install/run approval.

## Content Workflow Stages

1. Research and transcript intake.
2. Gemma summary and system extraction.
3. Codex feasibility and risk audit.
4. User selects niche and offer.
5. Gemma drafts scripts, hooks, product outlines, and calendars.
6. User approves assets and claims.
7. Claude Code builds repo-local templates or landing drafts if needed.
8. Human manually publishes or approves any platform action.

## Approval Requirements

Explicit approval is required for:

- paid tool signup or usage
- platform account connection
- posting/uploading
- scheduling
- affiliate links
- Whop/store listing
- external outreach
- media using real likenesses or third-party copyrighted material
- any automation that touches live accounts

## Current Verdict

Gemma/Ollama, markdown templates, and Codex/Claude review are the right near-term content factory. Higgsfield, Seedance, Kling, Arcads, Paperclip, OpenClaw, and n8n should stay in research/planning until a specific approved experiment is chosen.
