# Codex N+3.17 Tooling Priority and Risk Audit

Status: codex_audit_only / tooling_priority_review / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 77bfb74

## Purpose

Rank future tools and concepts for Ghoti while keeping the current milestone conservative. This audit does not install, clone, run, wire, or stage any external tool or third-party repo content.

## Priority Ranking

1. Gemma compression and money workflow foundation.
2. Experiment tracker and video-to-money runner.
3. Dashboard/launcher quality.
4. Paperclip isolated evaluation.
5. n8n rails.
6. OpenClaw worker/channel.
7. Unity-MCP mobile game lane.
8. Mythos verification patterns.
9. Dolphin/CUDA later.

## Candidate Reviews

### 1. PaperclipAI / `paperclipai/paperclip`

Potential role:

- Future zero-human-company or control-plane candidate.
- Could coordinate workers, budgets, goals, tasks, status, and handoffs.
- Could become useful once Ghoti has stable worker cards and money workflow trackers.

Current truth:

- Planning-only.
- Not installed by this milestone.
- Not wired into Ghoti runtime.
- Separate approval required before install or run.

Risks:

- A control plane can become over-permissioned quickly.
- Could touch files, agents, accounts, or tools if installed carelessly.
- Needs sandbox and task-scope model before real use.

Safe next step:

- Isolated read-only source evaluation or install checklist only.
- Map Paperclip concepts to Ghoti worker cards and experiment tracker.

### 2. OpenClaw

Potential role:

- Future worker/channel/multi-agent candidate.
- Possible personal assistant, channel interface, or managed worker under Ghoti/Paperclip control.

Current truth:

- Reference/planning-only.
- Not runtime-wired.
- No install or run in this milestone.

Risks:

- Channel integrations and assistant surfaces can touch live accounts.
- Public exposure or broad credentials would be high risk.

Safe next step:

- Extract safe architectural ideas only.
- No credentials, channels, live accounts, or runtime wiring.

### 3. n8n

Potential role:

- Deterministic workflow rails later.
- Good for boring repeatable steps after the manual process is stable:
  - scheduled checks
  - local webhooks
  - file watchers
  - notification triggers
  - queue creation

Current truth:

- Planning-only.
- Not installed.
- Not runtime-wired.

Risks:

- Can send emails, post, call APIs, and process credentials if misconfigured.
- Easy to accidentally turn drafts into live actions.

Safe next step:

- No install yet.
- First future use should be local-only trigger planning.

### 4. `ivanmurzak/Unity-MCP` / AI Game Developer Unity Skills MCP

Potential role:

- Future simple phone game lane.
- Could help prototype tiny mobile games or Unity game mechanics later.

Current truth:

- Planning-only.
- Not installed.
- No Unity, App Store, Google Play, build, or publishing action.

Risks:

- Unity setup, build tools, app-store accounts, ads/IAP, platform policies.
- MCP tools can be powerful if attached to project files and build systems.

Safe next step:

- Create simple phone game pipeline templates only.
- Evaluate repo/license/source before any clone or install.
- Keep game ideas as product experiments first, not store releases.

### 5. Mythos

Potential role:

- Audit-only safety/control concept.
- Useful pattern source for verification loops and task budgets.

Current truth:

- Do not clone leaked/proprietary code.
- Do not copy leaked code.
- No install.
- No runtime wiring.

Safe patterns to extract:

- strict verification
- correction loops
- file hash truth
- task budgets
- audit logs
- explicit PASS/FAIL gates
- bounded worker scopes

Risks:

- Leaked/proprietary code and unsafe provenance.
- Overclaiming capabilities from concepts not implemented locally.

Safe next step:

- Write a clean-room verification pattern note only, if needed.

### 6. Dolphin / Uncensored Local Models

Potential role:

- Evaluation-only for legitimate local analysis.
- Could be used for offline brainstorming on harmless local data if legally and safely acquired.

Current truth:

- Not installed or wired.
- Not needed for current money workflow foundation.

Risks:

- User explicitly must not use "less restricted" models to bypass law, safety, platform rules, or provider limits.
- Lower safety model behavior can create poor or risky advice.

Safe next step:

- Defer.
- If evaluated later, restrict to harmless local text classification and compare quality against Gemma.

### 7. CUDA / GPU

Potential role:

- Future local inference acceleration.
- Could make Gemma or other local models faster.

Current truth:

- No CUDA install now.
- Not required for current template/tracker work.

Risks:

- Driver/toolchain churn.
- Large downloads.
- Can distract from money workflow shipping.

Safe next step:

- Defer until local Gemma workflow proves useful enough to justify optimization.

## Why Gemma + Money Foundation Comes First

The fastest practical win is to reduce paid API usage while producing money workflow artifacts:

- Gemma compresses and drafts locally.
- Money templates create many shots.
- Experiment tracker measures results.
- Codex audits risks.
- Claude Code implements local tools.

This creates value before adding another large orchestrator.

## What Must Stay Blocked

- No live posting.
- No outreach automation.
- No scraping abuse.
- No paid tool action.
- No app-store action.
- No Whop/Gumroad/Shopify account action.
- No Paperclip/OpenClaw/n8n/Unity-MCP install or run.
- No Mythos leaked-code clone/copy/install.
- No Dolphin/safety-bypass use.
- No CUDA install.
- No live account credentials.

## Final Verdict

Build the Gemma compression and money workflow foundation first. Evaluate Paperclip, n8n, OpenClaw, Unity-MCP, Mythos patterns, Dolphin, and CUDA only after the repo-local numbers-game system is working and approval-gated.
