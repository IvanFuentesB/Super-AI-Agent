# N+6.7B - Odysseus Feature Intake + Personal Communications Roadmap - Run Report

Branch: feat/ghoti-agent-claude-n6-7b-odysseus-personal-comms-intake
Base: origin/main 67eb4a51ac8d5de538b39ab9437e994c375838cd (unchanged)
Worktree: .claude/worktrees/n6_7b_odysseus_personal_comms_intake
Date: 2026-05-31
Lane: implementation specialist (Claude Code). Codex audits next; a human merges.

## 1. What this milestone did

Recorded the useful patterns from the public README of
`pewdiepie-archdaemon/odysseus` (and adjacent personal-agent ideas) into the Ghoti
tool-intake roadmap as ten **candidate_only** modules. Odysseus is **not cloned**,
**not installed**, and **not run**; no external code executed. Nothing is wired into
the runtime and no new capability is enabled. The change is intake notes + an
additions JSON + a doc + a test, kept in a separate `*_additions_n6_7b.json` so it
runs in parallel with N+6.7A rather than editing that registry.

## 2. Start condition (verified read-only)

- origin/main = 67eb4a51ac8d5de538b39ab9437e994c375838cd; the worktree HEAD matches it.
- The branch was created fresh from origin/main; no N+6.5A or N+6.6A file was modified.
- N+6.7A's registry (`tool_candidate_registry.json`) was inspected read-only and left
  untouched; this milestone adds a separate additions file instead of editing it.

## 3. Files added (7)

| # | File | Purpose |
|---|------|---------|
| 1 | `14_context/tool_intake/odysseus_feature_intake.md` | Odysseus features + its security warnings, candidate-only |
| 2 | `14_context/tool_intake/personal_comms_agent_roadmap.md` | email/WhatsApp/calendar/style ideas, draft-only rules |
| 3 | `14_context/tool_intake/ai_council_and_model_cookbook_roadmap.md` | AI council, cookbook, deep research, document editor |
| 4 | `14_context/tool_intake/tool_candidate_registry_additions_n6_7b.json` | the 10 candidate_only modules |
| 5 | `docs/GHOTI_N6_7B_ODYSSEUS_PERSONAL_COMMS_INTAKE.md` | milestone doc |
| 6 | `01_projects/runtime_mvp/tests/test_n6_7b_odysseus_personal_comms_intake.py` | 18 tests |
| 7 | `14_context/claude_n6_7b_odysseus_personal_comms_intake.md` | this report |

No file outside this list was created, edited, or deleted.

## 4. The ten candidate_only modules

Every module is `status: candidate_only`, `installed: false`, `runtime_wired: false`.

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
| 9 | Personal Style Memory | high | 3 - approval-gated |
| 10 | AI Video Self-Editing Pipeline | medium | 3 - manual upload |

## 5. Personal communications safety (email + WhatsApp)

| Field | Email Triage | WhatsApp |
|-------|--------------|----------|
| `draft_only` | true | true |
| `auto_send` | false | false |
| `account_login` | separate approved milestone (not now) | separate approved milestone (not now) |
| `credentials_stored` | false | false |
| `mass_reply` | false | false |

Both `forbidden_now` lists forbid sending and forbid account login. No message is
deleted, archived, or moved. There is no spam and no fake engagement.

## 6. Safety-flag verification (global_safety, all false)

| Flag | Value |
|------|-------|
| external_repo_cloned | false |
| external_code_executed | false |
| installs_performed | false |
| runtime_wired | false |
| email_login | false |
| whatsapp_login | false |
| telegram_enabled | false |
| mcp_enabled | false |
| browser_use_enabled | false |
| computer_use_enabled | false |
| auto_send_enabled | false |
| social_posting_enabled | false |
| secrets_stored | false |
| live_account_action | false |

Personal Style Memory: `impersonation_without_approval: false`,
`outbound_requires_human_approval: true`, `memory_editable: true`,
`memory_deletable: true`, `sensitive_profiling: false`.
AI Video: `local_pipeline_first: true`, `copyrighted_scraping: false`,
`automated_posting: false`, `approved_assets_only: true`, `fake_engagement: false`.

## 7. Validation

| Check | Result |
|-------|--------|
| `git diff --check` (staged) | clean - no whitespace errors |
| `git show --check --stat HEAD` | clean |
| n6_7b test module | 18 passed, 0 failed |
| `unittest discover -p "test_n6_*.py"` | 48 passed, 0 failed (30 pre-existing n6 tests + 18 new) |
| `public_repo_security_audit.py --run --json` | 150 total / 143 passed / 0 failed / 7 warnings; blocking_findings: []; safe_to_make_public: true; human_review_required: true |

The 7 audit warnings and the `human_review_required` flag are the pre-existing
repository baseline; this milestone adds no new failure and no new blocking finding.

## 8. Direct answers

- Is Odysseus installed, cloned, or run by this milestone? **No** - not cloned, not
  installed, not run; no external code executed.
- Are email and WhatsApp draft-only? **Yes** - labeled DRAFTs only; the human sends.
- Is there any auto-send or auto-reply? **No** - auto-send is disabled globally and
  per module; there is no auto-reply.
- Is there any account login for email, WhatsApp, or calendar? **No** - no login;
  credentials are never stored in the repo or vault.
- Does Personal Style Memory impersonate the user without approval? **No** - every
  outbound requires human approval; the style memory is explicit, editable, deletable.
- Is the AI video pipeline local-first with no copyrighted scraping and no
  auto-posting? **Yes** - local-first over approved assets only; no copyrighted
  scraping; no automated posting; no fake engagement.
- Are MCP, browser-use, computer-use, or Telegram enabled? **No** - none are enabled.
- Is anything wired into the runtime? **No** - `runtime_wired` is false everywhere.
- Was `main` changed or pushed? **No** - main stays at 67eb4a5; only the feature
  branch is pushed.

## 9. What is explicitly NOT enabled

- Odysseus is not cloned, not installed, and not run; no external code executes.
- No email login, no WhatsApp login, no Telegram setup, no MCP install.
- No browser-use, no computer-use, no auto-send, no social posting.
- No secrets stored; no live account action; no runtime wiring.
- `main` is untouched; no N+6.5A or N+6.6A file was modified.

## 10. Codex audit target

Branch `feat/ghoti-agent-claude-n6-7b-odysseus-personal-comms-intake`. The audit
should confirm: every module is candidate_only / not installed / not runtime_wired;
email and WhatsApp are draft-only with no login and no stored credentials; Personal
Style Memory is approval-gated and never impersonates without approval; the AI video
module is local-first with no copyrighted scraping and no auto-posting; and no doc
overclaims that Odysseus is installed/cloned/running or that MCP/browser-use/
computer-use/Telegram is enabled.

## 11. Verdict

IMPLEMENTED. Documentation/intake only; trivially revertable. The feature branch is
pushed to origin; `main` is untouched.
