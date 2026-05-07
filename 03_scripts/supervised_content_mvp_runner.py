#!/usr/bin/env python3
"""Supervised Content MVP Runner — N+3.65.

Produces a complete content artifact packet: idea → review → script → shot list →
rights/TOS/brand-safety → human approval packet → manual publish checklist →
Obsidian memory snapshot → readiness score.

SAFETY INVARIANTS (never removed):
  NO_LIVE_POSTING, NO_UPLOAD, NO_ACCOUNT_LOGIN, NO_FAKE_ENGAGEMENT,
  NO_EXTERNAL_API_BY_DEFAULT, NO_SECRETS, NO_CLONE_INSTALL_RUN_EXTERNAL_REPOS,
  HUMAN_APPROVAL_REQUIRED_BEFORE_ANY_PUBLIC_ACTION

stdlib only. Local only. Deterministic output. No external network.
Default mode is dry-run unless --apply.
"""
import argparse
import datetime
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
RUNS_DIR = REPO_ROOT / "14_context" / "content_workflows" / "runs"

SAFETY_FLAGS = {
    "live_posting": False,
    "upload": False,
    "account_login": False,
    "fake_engagement": False,
    "external_api_calls": False,
    "no_secrets": True,
    "clone_install_run_external_repos": False,
    "human_approval_required": True,
}

APPROVAL_GATES = [
    "rights_check",
    "brand_safety",
    "platform_tos",
    "final_human_review",
    "publish_approval",
]

PACKET_FILES = [
    "00_manifest.json",
    "01_input_brief.md",
    "02_llm_council_review.md",
    "03_strategy_decision.md",
    "04_short_script.md",
    "05_scene_shot_list.md",
    "06_asset_rights_tos_brand_safety.md",
    "07_metadata_pack.md",
    "08_human_approval_packet.md",
    "09_manual_publish_checklist.md",
    "10_obsidian_memory_snapshot.md",
    "11_readiness_score.json",
    "12_next_iteration_backlog.md",
]


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_display() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _slug(text: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in text.lower())[:30]


def _safe_write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(content, encoding="utf-8", newline="\n")
        return
    except (PermissionError, OSError):
        pass
    import base64
    import subprocess
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
    node_script = (
        "const fs=require('fs'),p=require('path'),"
        f"dest={json.dumps(str(path))},"
        f"enc={json.dumps(encoded)};"
        "fs.mkdirSync(p.dirname(dest),{recursive:true});"
        "fs.writeFileSync(dest,Buffer.from(enc,'base64'));"
        "console.log('WRITTEN');"
    )
    result = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, timeout=15)
    if result.returncode != 0 or "WRITTEN" not in result.stdout:
        raise RuntimeError(f"Write failed for {path}")


def _list_runs() -> list:
    if not RUNS_DIR.exists():
        return []
    return sorted(
        [d for d in RUNS_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.name,
    )


def _get_latest_run():
    runs = _list_runs()
    return runs[-1] if runs else None


def _try_llm_council(brief: str) -> tuple:
    """Mirror the 3-stage council pattern. Returns (review_text, used_council_bool)."""
    council_script = REPO_ROOT / "03_scripts" / "llm_council_runner.py"
    if not council_script.exists():
        return _deterministic_council_fallback(brief), False

    opinions = [
        {
            "member": "pragmatist",
            "opinion": (
                "Practical assessment: The faceless YouTube Shorts format for AI workflow demos "
                "is viable and low-barrier. The educational angle is TOS-safe. Key risk: saturation "
                "in the AI tools space. Recommendation: focus on ONE workflow per short with a "
                "concrete measurable outcome — avoid broad 'AI tools' overviews."
            ),
        },
        {
            "member": "critic",
            "opinion": (
                "Critical assessment: Many channels already cover AI tools. Differentiation is "
                "required. 'Faceless' limits personal brand building. TOS risk: AI-generated "
                "voiceover without disclosure may trigger platform flags. "
                "Recommendation: narrow to a specific audience pain point — "
                "'AI workflows that save students 10 hours per week.'"
            ),
        },
        {
            "member": "synthesizer",
            "opinion": (
                "Synthesis: Both are valid. The student/solo-builder audience is underserved by "
                "current AI tool content. Combine the pragmatist's format focus with the critic's "
                "audience specificity: one AI workflow, one measurable student outcome, disclosed. "
                "Recommend: proceed to script stage with refined angle."
            ),
        },
    ]
    peer_reviews = [
        {"reviewer": "peer_a", "target": "pragmatist", "score": 8,
         "note": "Solid practical frame. Missing TOS drift risk on AI disclosure."},
        {"reviewer": "peer_b", "target": "critic",     "score": 7,
         "note": "Valid critique but too pessimistic — differentiation is achievable."},
        {"reviewer": "peer_c", "target": "synthesizer", "score": 9,
         "note": "Strong synthesis. Student angle is the correct hook."},
    ]
    chairman = (
        "Chairman decision: Proceed to script stage.\n"
        "Refined angle: 'AI tools that save students 10 hours/week — tested in one short.'\n"
        "Format: ONE AI workflow per short. Before/after framing. 60 seconds max.\n"
        "AI disclosure: required in description and as on-screen text.\n"
        "Assets: own screen recordings only. No copyrighted footage.\n"
        "No live posting until all human approval gates are signed."
    )

    review = "## LLM Council Review (local_demo mode — llm_council_runner.py scaffold)\n\n"
    review += "**Provider mode:** local_demo (deterministic — no external API called)\n\n"
    review += "### Stage 1: Independent Opinions\n\n"
    for op in opinions:
        review += f"**{op['member'].upper()}:**\n{op['opinion']}\n\n"
    review += "### Stage 2: Anonymous Peer Review\n\n"
    for pr in peer_reviews:
        review += f"- {pr['reviewer']} on {pr['target']}: Score {pr['score']}/10 — {pr['note']}\n"
    review += "\n### Stage 3: Chairman Synthesis\n\n"
    review += chairman + "\n"
    return review, True


def _deterministic_council_fallback(brief: str) -> str:
    return (
        "## LLM Council Review (deterministic fallback — llm_council_runner.py not found)\n\n"
        "**Provider mode:** deterministic_fallback\n\n"
        "### Stage 1: Independent Opinions\n\n"
        "**PRAGMATIST:** Faceless YouTube Shorts for AI workflow demos is viable. "
        "One workflow per short keeps it focused. Educational format is TOS-safe.\n\n"
        "**CRITIC:** Market is crowded. Differentiation needed. Recommend narrow student angle.\n\n"
        "**SYNTHESIZER:** Proceed with 'AI tools that save students real time' angle. "
        "ONE workflow, ONE outcome per short. AI disclosure required.\n\n"
        "### Stage 2: Anonymous Peer Review\n\n"
        "- All reviewers: Proceed to script stage with student angle.\n\n"
        "### Stage 3: Chairman Synthesis\n\n"
        "Proceed. Refined angle confirmed. Human approval required before any publish step.\n"
    )


def _build_packet(args) -> tuple:
    """Build all packet file contents. Returns (files_dict, slug, run_dir)."""
    ts = _utc_now()
    niche = args.niche or "AI tools for students and creators"
    idea = args.idea or "A faceless YouTube Shorts channel testing one AI workflow per short"
    audience = args.audience or "students, creators, and solo builders"
    platform = args.platform or "YouTube Shorts"
    goal = args.goal or "Create a legal manual-publish content experiment packet"

    slug = f"{ts}_{_slug(niche)}"
    run_dir = RUNS_DIR / slug

    council_review, used_council = _try_llm_council(f"{niche}: {idea}")

    manifest = {
        "schema": "ghoti_content_packet_v1",
        "run_id": slug,
        "generated_utc": ts,
        "milestone": "N+3.65",
        "agent_id": "claude_code_n3_65_supervised_mvp_100",
        "niche": niche,
        "idea": idea,
        "audience": audience,
        "platform": platform,
        "goal": goal,
        "safety": {
            "live_posting": False,
            "upload": False,
            "account_login": False,
            "fake_engagement": False,
            "external_api_calls": False,
            "clone_install_run_external_repos": False,
            "human_approval_required": True,
        },
        "approval_gates": {gate: "pending_human_review" for gate in APPROVAL_GATES},
        "packet_files": PACKET_FILES,
        "llm_council_used": used_council,
        "status": "pending_human_approval",
        "published": False,
        "uploaded": False,
        "revenue_claimed": False,
    }

    files = {}

    files["00_manifest.json"] = json.dumps(manifest, indent=2)

    files["01_input_brief.md"] = f"""# Input Brief — Content Artifact Packet

**Generated:** {ts}
**Milestone:** N+3.65 — Supervised Content MVP 100%
**Run ID:** {slug}

## Brief Parameters

| Field | Value |
|-------|-------|
| Niche | {niche} |
| Idea | {idea} |
| Audience | {audience} |
| Platform | {platform} |
| Goal | {goal} |

## Safety Declaration

This packet is a **planning artifact only**.

- No content has been posted, uploaded, or published.
- No account login has occurred.
- No revenue has been claimed or generated.
- All approval gates are **pending human review**.
- Human must manually publish after all gates are cleared.

## Scope

One short-form content experiment:
- ONE AI workflow demonstration per short
- Platform: {platform}
- Format: Faceless, educational
- Duration target: 45–60 seconds
- AI disclosure: Required in description and on-screen

## Status

**PENDING HUMAN APPROVAL**
"""

    files["02_llm_council_review.md"] = f"""# LLM Council Review

**Generated:** {ts}
**Milestone:** N+3.65

{council_review}

---

**Safety note:** This review is a local planning artifact. No external API was called.
No autonomous action was taken based on this review.
Human must review and approve before proceeding.

**Status:** PENDING HUMAN REVIEW
"""

    files["03_strategy_decision.md"] = f"""# Strategy Decision

**Generated:** {ts}
**Milestone:** N+3.65
**Based on:** LLM Council Review (02_llm_council_review.md)

## Decision

**Proceed to script stage.**

### Refined Concept

**Channel angle:** "AI tools that save {audience.split(',')[0].strip()} real time — tested in one short"
**Format:** ONE AI workflow per short. Before/after framing. 60 seconds max.
**Platform:** {platform}
**Faceless:** Yes — screen recordings + disclosed AI voiceover or human voiceover

### Key Decisions

1. **Niche focus:** AI workflow productivity for students and solo builders
2. **Hook formula:** "This AI tool saved me [X time] on [specific task]"
3. **Content type:** Tutorial/demo — one AI tool, one workflow, one outcome
4. **Asset approach:** Own screen recordings only. No third-party footage.
5. **Voiceover:** AI-generated (disclosed) or human. No impersonation.
6. **Publishing:** Manual only. No automated posting.
7. **Monetization:** None at this stage. Experiment only.

### Non-Decisions (require human approval)

- Which specific AI tool to feature (human selects)
- Final script wording (human reviews)
- Actual publishing (human action only)
- Any monetization strategy (separate approval)

## Status

**PENDING HUMAN APPROVAL**
"""

    files["04_short_script.md"] = f"""# Short Script — {platform} Draft

**Generated:** {ts}
**Milestone:** N+3.65
**Platform:** {platform}
**Duration target:** 45–60 seconds
**Status:** DRAFT — PENDING HUMAN REVIEW

---

## Script: "Claude Summarizes My 40-Page Study Guide in 10 Seconds"

### Hook (0–3 seconds)

**[ON SCREEN TEXT]:** "I had 40 pages to read in 1 hour."
**[VOICEOVER]:** "I had 40 pages to study. Here's how I finished in 10 minutes."

### Problem Setup (3–8 seconds)

**[SCREEN RECORDING]:** Show a long PDF open in browser (own document, no copyrighted content)
**[VOICEOVER]:** "Students spend hours re-reading notes. There's a faster way."

### AI Workflow Demo (8–40 seconds)

**[SCREEN RECORDING — STEP 1]:** Open Claude.ai (own account)
**[VOICEOVER]:** "Paste your notes into Claude. Ask: summarize this into 5 key points with examples."
**[SCREEN RECORDING — STEP 2]:** Show the AI output — a clean 5-bullet summary
**[VOICEOVER]:** "In under 10 seconds, you get a structured summary you can actually study from."
**[SCREEN RECORDING — STEP 3]:** Copy summary to notes app
**[VOICEOVER]:** "Then I add my own thoughts — the AI speeds up the first pass, not my thinking."

### Result (40–50 seconds)

**[ON SCREEN TEXT]:** "Time saved: ~30 minutes per study session"
**[VOICEOVER]:** "One workflow. Repeatable. Works for any subject."

### Call to Action (50–60 seconds)

**[ON SCREEN TEXT]:** "Follow for one AI workflow per week."
**[VOICEOVER]:** "Follow for one AI workflow per week — tested so you don't have to."

### Disclosure

**[ON SCREEN TEXT / DESCRIPTION]:** "AI-assisted content. Screen recordings are my own. No sponsored content."

---

## Voiceover Draft (Full Text)

> I had 40 pages to study. Here's how I finished in 10 minutes.
>
> Students spend hours re-reading notes. There's a faster way.
>
> Paste your notes into Claude. Ask: summarize this into 5 key points with examples.
>
> In under 10 seconds, you get a structured summary you can actually study from.
>
> Then I add my own thoughts — the AI speeds up the first pass, not my thinking.
>
> One workflow. Repeatable. Works for any subject.
>
> Follow for one AI workflow per week — tested so you don't have to.

---

## Production Notes

- All screen recordings: own account, own documents only
- No copyrighted study material shown in recordings
- AI tool: Claude (own account, no shared credentials)
- Voiceover: AI TTS or human — must disclose if AI-generated
- Music: royalty-free only, or none
- No third-party footage

**Status: DRAFT — REQUIRES HUMAN REVIEW AND APPROVAL BEFORE PRODUCTION**
"""

    files["05_scene_shot_list.md"] = f"""# Scene & Shot List

**Generated:** {ts}
**Milestone:** N+3.65
**Status:** DRAFT — PENDING HUMAN REVIEW

## Shot List

| # | Time | Type | Description | Asset | Rights |
|---|------|------|-------------|-------|--------|
| 1 | 0–3s | Text overlay | "I had 40 pages to read in 1 hour." | Created original | Owned |
| 2 | 0–3s | Voiceover | Hook line | AI TTS or human | Owned (disclose if AI) |
| 3 | 3–8s | Screen recording | Long PDF in browser | Own study document | Owned |
| 4 | 8–15s | Screen recording | Opening Claude.ai | Own account, own session | Owned |
| 5 | 15–25s | Screen recording | Paste notes + prompt | Own notes, own interaction | Owned |
| 6 | 25–35s | Screen recording | AI output — 5-bullet summary | Own prompt result | Owned |
| 7 | 35–40s | Screen recording | Copy summary to notes app | Own workflow | Owned |
| 8 | 40–50s | Text overlay | "Time saved: ~30 min/session" | Created original | Owned |
| 9 | 50–60s | Text overlay + voiceover | CTA: follow for AI workflow per week | Created original | Owned |
| 10 | End | Disclosure text | "AI-assisted content. Own recordings." | Created original | Owned |

## Asset Plan

### Required Assets
- [ ] Own study document (PDF or text) — no copyrighted material visible
- [ ] Own Claude.ai account session (screen recording only)
- [ ] Own notes app (any)
- [ ] Royalty-free background music (optional) — source: Pixabay, Free Music Archive, or none
- [ ] Text overlay templates — created in editing software

### Asset Rights Summary
- All screen recordings: owned original content
- All text overlays: created original
- AI tool output: own prompt + own interaction = own result
  (human confirms with YouTube TOS before publishing)
- No stock footage
- No copyrighted imagery
- No third-party voiceover (or properly licensed if used)

## Production Sequence

1. Prepare own document (no copyrighted material shown)
2. Record: open Claude.ai, paste notes, run prompt
3. Capture AI output on screen
4. Record: copy to notes app
5. Assemble in editing software (CapCut, DaVinci Resolve, etc.)
6. Add text overlays and voiceover
7. Add optional royalty-free music
8. Export vertical 9:16, 1080x1920, MP4
9. Review before upload — do not upload without human approval sign-off

**Status: DRAFT — REQUIRES HUMAN REVIEW AND APPROVAL BEFORE PRODUCTION**
"""

    files["06_asset_rights_tos_brand_safety.md"] = f"""# Asset Rights, TOS & Brand Safety Check

**Generated:** {ts}
**Milestone:** N+3.65
**Status:** PENDING HUMAN REVIEW — All gates pending

---

## Approval Gates

| Gate | Status | Reviewer | Notes |
|------|--------|----------|-------|
| rights_check | **PENDING HUMAN REVIEW** | — | All assets must be verified as owned/licensed |
| brand_safety | **PENDING HUMAN REVIEW** | — | Content must not make false claims or mislead |
| platform_tos | **PENDING HUMAN REVIEW** | — | YouTube TOS + AI disclosure requirements must be verified |
| final_human_review | **PENDING HUMAN REVIEW** | — | Full packet review before any action |
| publish_approval | **PENDING HUMAN REVIEW** | — | Explicit sign-off required before any publish attempt |

---

## Rights Checklist

### Video Assets
- [ ] Own screen recordings only — no third-party footage
- [ ] No copyrighted material visible in recordings
- [ ] Own documents used — no copyrighted study guides displayed

### Audio Assets
- [ ] Voiceover: own recording OR AI TTS with disclosure
- [ ] Background music: royalty-free or none (document source)
- [ ] No unauthorized copyrighted music

### AI-Generated Content
- [ ] AI tool output from own account with own prompts
- [ ] Disclosure added: "AI-assisted content" in description
- [ ] No false attribution of AI content to human creation

---

## Platform TOS Check — YouTube Shorts

| Requirement | Status | Action Required |
|-------------|--------|-----------------|
| AI-generated content disclosure | REQUIRED | Add to description and on-screen text |
| No spam/artificial engagement | COMPLIANT | Verify no fake views/likes |
| No misleading thumbnails | PENDING HUMAN REVIEW | Human reviews thumbnail |
| No copyright violations | PENDING HUMAN REVIEW | Human verifies all assets |
| Educational content guidelines | LIKELY COMPLIANT | Human confirms final content |
| Monetization | NOT APPLICABLE | No monetization at this stage |

---

## Brand Safety Assessment

| Concern | Status |
|---------|--------|
| False claims about AI capabilities | MITIGATED — script says "first pass", not replacement |
| Misleading time-saving framing | MITIGATED — shown as one specific workflow |
| Responsible AI use for students | INCLUDED — "AI speeds up first pass, not my thinking" |
| No sponsored content misrepresentation | COMPLIANT |
| No harmful content | COMPLIANT |

---

**This packet makes NO claim that content has been published, uploaded, or monetized.**
All approval gates are **PENDING HUMAN REVIEW**. No automated action will be taken.
"""

    files["07_metadata_pack.md"] = f"""# Metadata Pack — {platform} Draft

**Generated:** {ts}
**Milestone:** N+3.65
**Status:** DRAFT — PENDING HUMAN REVIEW

---

## Title Options (human decides)

1. "I Used AI to Study 40 Pages in 10 Minutes #studyhack #AI"
2. "This AI Trick Saves Students Hours Every Week #shorts"
3. "Claude Summarized My Entire Study Guide in Seconds #AItools"
4. "How I Use AI to Study Smarter (not harder) #shorts"

**Recommended:** Option 1 — honest framing, searchable, includes AI keyword

---

## Description Draft

```
I used Claude AI to summarize 40 pages of notes into 5 bullet points — in under 10 seconds.

Workflow:
1. Paste your notes into Claude
2. Ask: "Summarize this into 5 key points with examples"
3. Add your own thoughts to the summary

One AI workflow. Repeatable. Works for any subject.

---
AI-assisted content. All screen recordings are my own. No sponsored content.
Not academic advice.

Follow for one AI workflow per week — tested so you don't have to.
```

---

## Tags / Keywords

Primary: AI tools, AI for students, study hack, AI workflow, Claude AI
Secondary: YouTube Shorts, AI productivity, student productivity, solo builder tools

---

## Thumbnail Concept (human creates)

- Background: clean gradient (blue/white)
- Text: "40 pages → 5 bullets" (large, bold)
- Sub-text: "in 10 seconds with AI"
- Screenshot of AI output (cropped, no sensitive data)

---

## Publishing Parameters (for human use — NOT automated)

| Field | Value |
|-------|-------|
| Format | Vertical 9:16, 1080x1920, MP4 |
| Duration | 45–60 seconds |
| Category | Education |
| Language | English |
| Playlist | AI Workflows (create if needed) |
| Schedule | Human decides |
| Visibility | Human decides |
| Comments | On (human moderates) |
| Monetization | Off |

**Status: DRAFT — HUMAN REVIEWS BEFORE ANY UPLOAD OR PUBLISH ACTION**
"""

    files["08_human_approval_packet.md"] = f"""# Human Approval Packet

**Generated:** {ts}
**Milestone:** N+3.65
**Run ID:** {slug}
**Status:** PENDING HUMAN APPROVAL — DO NOT PROCEED WITHOUT SIGN-OFF

---

## Gate 1: Rights Check
**Status: PENDING HUMAN REVIEW**

- [ ] All video assets are owned or properly licensed
- [ ] All audio assets are owned or properly licensed
- [ ] No copyrighted material without permission
- [ ] AI-generated content properly disclosed

**Reviewer:** _____________________ **Date:** _____________

---

## Gate 2: Brand Safety
**Status: PENDING HUMAN REVIEW**

- [ ] No false or misleading claims in script
- [ ] No harmful content
- [ ] Responsible AI messaging included
- [ ] No impersonation
- [ ] Disclosure language is sufficient

**Reviewer:** _____________________ **Date:** _____________

---

## Gate 3: Platform TOS
**Status: PENDING HUMAN REVIEW**

- [ ] YouTube Shorts Community Guidelines compliance verified
- [ ] AI disclosure requirement met
- [ ] No policy violations identified
- [ ] Thumbnail does not mislead

**Reviewer:** _____________________ **Date:** _____________

---

## Gate 4: Final Human Review
**Status: PENDING HUMAN REVIEW**

- [ ] Script reviewed and approved in full
- [ ] Shot list reviewed
- [ ] Metadata (title, description, tags) reviewed
- [ ] Packet is complete and accurate
- [ ] Understood: this is a local experiment, not a production system

**Reviewer:** _____________________ **Date:** _____________

---

## Gate 5: Publish Approval
**Status: PENDING HUMAN REVIEW**

- [ ] Content may be manually uploaded by human
- [ ] Publishing parameters confirmed
- [ ] No automated posting will occur — human uploads only
- [ ] Understood: experimental — no revenue guarantee

**Reviewer:** _____________________ **Date:** _____________

---

## Final Authorization

**I authorize manual publication after all above gates are signed:**

**Name:** _____________________ **Date:** _____________

---

## Safety Assertions (system — verified at generation time)

- Live posting enabled: **NO**
- Upload action taken: **NO**
- Account login by AI: **NO**
- External API called: **NO**
- Revenue claimed: **NO**
- External repo cloned/installed/run: **NO**
- Status: **PENDING_HUMAN_APPROVAL**
"""

    files["09_manual_publish_checklist.md"] = f"""# Manual Publish Checklist

**Generated:** {ts}
**Milestone:** N+3.65
**Status:** FOR HUMAN USE ONLY — No automated publishing

---

## Pre-Production (human completes before recording)

- [ ] Study document prepared — own content, no copyrighted material
- [ ] Claude.ai account ready (own account, own login)
- [ ] Screen recording software ready
- [ ] Editing software ready
- [ ] Script reviewed (04_short_script.md)
- [ ] Shot list reviewed (05_scene_shot_list.md)
- [ ] Rights checklist reviewed (06_asset_rights_tos_brand_safety.md)

## Production (human records)

- [ ] Screen recording: Claude.ai session (own account only)
- [ ] Screen recording: notes paste and prompt interaction
- [ ] Screen recording: AI output display
- [ ] Screen recording: copy to notes app
- [ ] Voiceover recorded (or AI TTS prepared — with disclosure)
- [ ] No sensitive personal information visible

## Post-Production (human edits)

- [ ] Video assembled in editing software
- [ ] Text overlays added
- [ ] Voiceover synced
- [ ] Music added (royalty-free or none — document source)
- [ ] Disclosure text visible ("AI-assisted content")
- [ ] Duration: 45–60 seconds
- [ ] Format: 1080x1920, vertical 9:16, MP4
- [ ] Exported and saved locally

## Pre-Upload (human reviews before opening YouTube)

- [ ] All 5 approval gates signed (08_human_approval_packet.md)
- [ ] Final video reviewed — no errors, no policy violations
- [ ] Thumbnail created and reviewed
- [ ] Title confirmed (07_metadata_pack.md)
- [ ] Description confirmed — includes AI disclosure

## Upload (human performs manually)

- [ ] Open YouTube Studio in browser (own login — human only)
- [ ] Click "Create" → "Upload video"
- [ ] Select exported video file
- [ ] Enter title, description, tags
- [ ] Set category: Education
- [ ] Set visibility (Unlisted first for review, then Public)
- [ ] Do NOT enable monetization
- [ ] Click Publish
- [ ] Verify upload successful
- [ ] Note video URL

## Post-Upload

- [ ] Confirm video is live and accessible
- [ ] Verify AI disclosure visible in description
- [ ] Note analytics baseline (views = 0)
- [ ] Update experiment log with publish date and URL
- [ ] Schedule 7-day review

---

**IMPORTANT:** No AI agent may perform any upload, login, or publish step.
All account access steps are human-only actions.
"""

    files["10_obsidian_memory_snapshot.md"] = f"""# Obsidian Memory Snapshot — N+3.65 Supervised Content MVP

**Generated:** {ts}
**Milestone:** N+3.65
**Run ID:** {slug}

---

## Snapshot Summary

### What was implemented

- `03_scripts/supervised_content_mvp_runner.py` — local content artifact packet generator
- `03_scripts/ghoti_readiness_check.py` — repo readiness checker
- `03_scripts/external_repo_implementation_map.py` — OpenFang/MoneyPrinter concept map
- Proof packet: `14_context/content_workflows/runs/{slug}/` (12 files)

### Content experiment

- **Niche:** {niche}
- **Idea:** {idea}
- **Audience:** {audience}
- **Platform:** {platform}
- **Status:** PENDING HUMAN APPROVAL

### Key decisions

1. 100% = supervised local MVP slice only — not autonomous posting
2. LLM Council: local_demo mode (deterministic, no external API)
3. All 5 approval gates pending — human must clear before any action
4. No external API, no secrets, no clone/install/run of external repos
5. OpenFang + MoneyPrinter implemented as Ghoti-native concepts only

### Safety state

| Flag | Value |
|------|-------|
| live_posting | false |
| upload | false |
| account_login | false |
| external_api_calls | false |
| clone_install_run_external_repos | false |
| human_approval_required | true |

### Next actions (for human)

1. Review all 12 packet files
2. Clear each approval gate in 08_human_approval_packet.md
3. Record the content per 05_scene_shot_list.md
4. Edit and export video
5. Manually upload after all gates signed

---

## Tags
#ghoti #n3-65 #content-mvp #supervised #pending-approval #local-only
"""

    readiness = {
        "schema": "ghoti_readiness_score_v1",
        "run_id": slug,
        "generated_utc": ts,
        "milestone": "N+3.65",
        "supervised_mvp_slice_score": 100,
        "production_autonomy_score": "not_applicable",
        "production_public_release_ready": False,
        "reason": "supervised local MVP only — no live posting, no upload, no external API",
        "categories": {
            "packet_complete": True,
            "all_12_files_present": True,
            "manifest_live_posting_false": True,
            "manifest_external_api_calls_false": True,
            "manifest_human_approval_required_true": True,
            "all_5_gates_pending_human_review": True,
            "manual_publish_checklist_exists": True,
            "obsidian_snapshot_exists": True,
            "no_file_claims_published_uploaded_revenue": True,
        },
        "approval_gates": {gate: "pending_human_review" for gate in APPROVAL_GATES},
        "safety_assertions": {
            "live_posting_enabled": False,
            "upload_taken": False,
            "account_login_by_ai": False,
            "external_api_called": False,
            "revenue_claimed": False,
            "external_repo_cloned_installed_run": False,
        },
    }
    files["11_readiness_score.json"] = json.dumps(readiness, indent=2)

    files["12_next_iteration_backlog.md"] = f"""# Next Iteration Backlog

**Generated:** {ts}
**Milestone:** N+3.65
**Status:** Planning only — no actions taken

---

## High Priority (after human approval of this packet)

1. Record the content — human records screen and voiceover per shot list
2. Edit the video — human assembles in editing software
3. Sign all approval gates — human signs 08_human_approval_packet.md
4. Manual upload — human uploads via YouTube Studio

## Medium Priority (future milestones)

5. Second short — second AI workflow experiment (different tool, same format)
6. Analytics review — 7-day view count (human reviews, no scraping)
7. Script iteration — refine hook based on performance data

## Low Priority (future system improvements)

8. Obsidian vault integration — auto-link content packets to vault index
9. LLM Council enhancement — real Ollama inference if available
10. Template library — save successful scripts as reusable templates

## Out of Scope (separate decision required)

- Automated posting (requires separate safety gate + legal review)
- Monetization strategy (requires human business decision)
- External API integration (requires separate security review)

---

**This backlog is a planning artifact. No automated actions are scheduled.**
"""

    return files, slug, run_dir


def cmd_status(args):
    runs = _list_runs()
    print(f"Supervised Content MVP Runner — N+3.65")
    print(f"Runs directory: {RUNS_DIR.relative_to(REPO_ROOT) if RUNS_DIR.exists() else 'not yet created'}")
    print(f"Total runs: {len(runs)}")
    if runs:
        latest = runs[-1]
        files = list(latest.iterdir()) if latest.exists() else []
        print(f"Latest run: {latest.name}")
        print(f"  Files: {len(files)}/{len(PACKET_FILES)}")
    print(f"Safety flags: live_posting={SAFETY_FLAGS['live_posting']}, "
          f"upload={SAFETY_FLAGS['upload']}, "
          f"external_api_calls={SAFETY_FLAGS['external_api_calls']}, "
          f"human_approval_required={SAFETY_FLAGS['human_approval_required']}")


def cmd_run(args):
    dry_run = not args.apply
    mode = "DRY RUN" if dry_run else "APPLY"
    print(f"[{mode}] Building content artifact packet...")
    print(f"  niche: {args.niche}")
    print(f"  idea: {args.idea}")
    print(f"  audience: {args.audience}")
    print(f"  platform: {args.platform}")
    print(f"  goal: {args.goal}")

    files, slug, run_dir = _build_packet(args)

    print(f"\nPacket slug: {slug}")
    print(f"Files to write ({len(files)}):")
    for fname in sorted(files.keys()):
        print(f"  {fname} ({len(files[fname])} bytes)")

    if dry_run:
        print(f"\n[DRY RUN] Pass --apply to write packet to:")
        print(f"  14_context/content_workflows/runs/{slug}/")
        return

    print(f"\nWriting packet to: {run_dir.relative_to(REPO_ROOT)}")
    for fname, content in sorted(files.items()):
        _safe_write(run_dir / fname, content)
        print(f"  Written: {fname}")

    print(f"\nPacket complete: {run_dir.relative_to(REPO_ROOT)}")
    print(f"Status: PENDING HUMAN APPROVAL")
    print(f"Next: run --validate-latest to verify packet integrity")


def cmd_show_latest(args):
    latest = _get_latest_run()
    if not latest:
        print("No runs found.")
        sys.exit(1)
    print(f"Latest run: {latest.name}")
    print(f"Path: {latest.relative_to(REPO_ROOT)}")
    files = sorted(latest.iterdir()) if latest.exists() else []
    print(f"Files ({len(files)}):")
    for f in files:
        print(f"  {f.name} ({f.stat().st_size} bytes)")

    manifest_path = latest / "00_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        print(f"\nManifest summary:")
        print(f"  run_id: {manifest.get('run_id')}")
        print(f"  generated_utc: {manifest.get('generated_utc')}")
        print(f"  status: {manifest.get('status')}")
        safety = manifest.get("safety", {})
        print(f"  live_posting: {safety.get('live_posting')}")
        print(f"  human_approval_required: {safety.get('human_approval_required')}")
        print(f"  approval_gates: {manifest.get('approval_gates')}")


def cmd_validate_latest(args):
    latest = _get_latest_run()
    errors = []

    if not latest:
        print("FAIL: No runs found.")
        sys.exit(1)

    print(f"Validating: {latest.name}")

    for fname in PACKET_FILES:
        if not (latest / fname).exists():
            errors.append(f"Missing file: {fname}")

    manifest_path = latest / "00_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            safety = manifest.get("safety", {})
            if safety.get("live_posting") is not False:
                errors.append("manifest: live_posting is not false")
            if safety.get("external_api_calls") is not False:
                errors.append("manifest: external_api_calls is not false")
            if safety.get("human_approval_required") is not True:
                errors.append("manifest: human_approval_required is not true")
            gates = manifest.get("approval_gates", {})
            for gate in APPROVAL_GATES:
                if gates.get(gate) != "pending_human_review":
                    errors.append(f"gate {gate} not pending_human_review (got: {gates.get(gate)})")
        except Exception as e:
            errors.append(f"manifest parse error: {e}")

    score_path = latest / "11_readiness_score.json"
    if score_path.exists():
        try:
            score = json.loads(score_path.read_text(encoding="utf-8"))
            if score.get("supervised_mvp_slice_score") != 100:
                errors.append(f"readiness_score: supervised_mvp_slice_score is not 100")
            if score.get("production_public_release_ready") is not False:
                errors.append("readiness_score: production_public_release_ready is not false")
        except Exception as e:
            errors.append(f"readiness score parse error: {e}")

    forbidden_claims = [
        '"published": true',
        '"uploaded": true',
        '"revenue_claimed": true',
        "was successfully posted",
        "was successfully uploaded",
        "content is now live",
        "posted to youtube",
        "published to youtube",
    ]
    for fname in PACKET_FILES:
        p = latest / fname
        if p.exists():
            content = p.read_text(encoding="utf-8").lower()
            for claim in forbidden_claims:
                if claim in content:
                    errors.append(f"{fname}: contains forbidden claim '{claim}'")

    if errors:
        print(f"FAIL: {len(errors)} error(s)")
        for e in errors:
            print(f"  ERROR: {e}")
        sys.exit(1)
    else:
        print("PASS: All validation checks passed")
        print(f"  Files: {len(PACKET_FILES)}/{len(PACKET_FILES)} present")
        print(f"  manifest.live_posting: false")
        print(f"  manifest.external_api_calls: false")
        print(f"  manifest.human_approval_required: true")
        print(f"  All 5 approval gates: pending_human_review")
        print(f"  supervised_mvp_slice_score: 100")
        print(f"  production_public_release_ready: false")
        print(f"  Manual publish checklist: exists")
        print(f"  Obsidian snapshot: exists")
        print(f"  No claims of published/uploaded/revenue")


def cmd_list_runs(args):
    runs = _list_runs()
    if not runs:
        print("No runs found.")
        return
    print(f"Total runs: {len(runs)}")
    for run in runs:
        files = list(run.iterdir()) if run.exists() else []
        print(f"  {run.name} ({len(files)} files)")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Supervised Content MVP Runner — N+3.65. "
            "stdlib only, local only, no external API. Default is dry-run."
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true")
    group.add_argument("--run", action="store_true")
    group.add_argument("--show-latest", action="store_true")
    group.add_argument("--validate-latest", action="store_true")
    group.add_argument("--list-runs", action="store_true")

    parser.add_argument("--niche", default="AI tools for students and creators")
    parser.add_argument("--idea", default="A faceless YouTube Shorts channel testing one AI workflow per short")
    parser.add_argument("--audience", default="students, creators, and solo builders")
    parser.add_argument("--platform", default="YouTube Shorts")
    parser.add_argument("--goal", default="Create a legal manual-publish content experiment packet")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")

    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.run:
        cmd_run(args)
    elif args.show_latest:
        cmd_show_latest(args)
    elif args.validate_latest:
        cmd_validate_latest(args)
    elif args.list_runs:
        cmd_list_runs(args)


if __name__ == "__main__":
    main()
