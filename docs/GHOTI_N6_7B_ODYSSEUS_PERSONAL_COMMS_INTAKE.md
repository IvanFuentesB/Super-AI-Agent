# N+6.7B - Odysseus Feature Intake + Personal Communications Roadmap

Status: IMPLEMENTED (safe planning foundation). This milestone extracts useful
patterns from `pewdiepie-archdaemon/odysseus` and related personal-agent ideas into
the Ghoti tool-intake roadmap as **candidate_only** modules. It does **not** install
anything and enables no new capability.

Author lane: implementation specialist (Claude Code). Codex audits next; a human merges.
Date: 2026-05-31

## 1. What this milestone is

A documentation/intake milestone. Odysseus is **not cloned**, **not installed**, and
not run; its public README informs a set of candidate modules Ghoti may build later
through the N+6.7A intake pipeline (inspect -> classify -> sandbox -> integrate).
It runs in parallel with N+6.7A: it adds a separate `*_additions_n6_7b.json` rather
than editing the existing registry.

## 2. Files added (7)

- `14_context/tool_intake/odysseus_feature_intake.md` - the Odysseus features + its
  security warnings, recorded candidate-only.
- `14_context/tool_intake/personal_comms_agent_roadmap.md` - email/WhatsApp/calendar/
  personal-style ideas under strict draft-only rules.
- `14_context/tool_intake/ai_council_and_model_cookbook_roadmap.md` - AI council,
  model cookbook, deep research, and document-editor ideas.
- `14_context/tool_intake/tool_candidate_registry_additions_n6_7b.json` - the 10
  candidate_only modules with per-module fields.
- `docs/GHOTI_N6_7B_ODYSSEUS_PERSONAL_COMMS_INTAKE.md` - this doc.
- `01_projects/runtime_mvp/tests/test_n6_7b_odysseus_personal_comms_intake.py` - tests.
- `14_context/claude_n6_7b_odysseus_personal_comms_intake.md` - run report.

## 3. The ten candidate_only modules

Each module carries: `value`, `risk`, `local_first_path`, `external_service_path`,
`first_safe_test`, `stop_conditions`, `allowed_now`, `forbidden_now`, and
`implementation_phase`. Every module is `candidate_only` with `installed: false` and
`runtime_wired: false`.

| # | Module | Risk | Phase |
|---|--------|------|-------|
| 1 | Odysseus Feature Extraction | low | 0 - documentation |
| 2 | AI Council / Model Compare | low | 1 - local compare |
| 3 | Model Cookbook / Hardware Fit | low | 1 - static cookbook |
| 4 | Deep Research Visual Reports | medium | 2 - local research draft |
| 5 | Document Editor for Project Documentation | low | 2 - draft-diff editor |
| 6 | Email Triage + Reply Drafts | high | 3 - draft-only |
| 7 | WhatsApp Summary + Reply Drafts | high | 3 - draft-only |
| 8 | Calendar/Tasks/Reminders Agent | medium | 2 - local drafts |
| 9 | Personal Style Memory ("thinks like me") | high | 3 - approval-gated |
| 10 | AI Video Self-Editing Pipeline | medium | 3 - manual upload |

## 4. Personal communications: draft-only, never send

Email and WhatsApp are **draft-only**: the agent produces labeled DRAFTs and there is
**no auto-send**. No message is deleted, archived, or moved; there are no mass replies,
no spam, and no fake engagement. There is **no account login** for email, WhatsApp, or
calendar until a separate, approved milestone using each provider's official API, and
**credentials are never stored** in the repo or the Obsidian vault.

## 5. "Thinks like me", safely

Personal Style Memory uses an **explicit, user-curated** preference memory the user can
edit and delete. Drafts are written in the user's style but **labeled DRAFT**; the agent
**never impersonates** the user without approval, and **every outbound requires human
approval**. No sensitive profiling happens without explicit approval.

## 6. AI videos, safely

The AI video pipeline is **local-first** over **user-approved assets only**. There is no
copyrighted scraping, no automated posting, and no fake engagement; exports are drafts
the user uploads manually.

## 7. What is explicitly NOT enabled

- Odysseus is **not cloned**, **not installed**, and not run; no external code executes.
- **No email login. No WhatsApp login. No Telegram setup. No MCP install.**
- **No browser-use. No computer-use.** **No auto-send.** No social posting.
- No secrets stored; no live account action. No runtime wiring.
- **MCP, browser-use, and computer-use are not enabled.** `main` is untouched, and no
  N+6.5A or N+6.6A files were modified.

## 8. What Codex should audit next

1. Every module is `candidate_only`, `installed: false`, `runtime_wired: false`.
2. Email/WhatsApp are draft-only: `auto_send: false`, no login, no stored credentials.
3. Personal Style Memory is approval-gated and never impersonates without approval.
4. The AI video module is local-first with no copyrighted scraping and no auto-posting.
5. No doc claims Odysseus is installed/cloned/running, or that MCP/browser-use/
   computer-use/Telegram is enabled.
6. The change is intake notes + an additions JSON + doc + test only, and is trivially
   revertable.
