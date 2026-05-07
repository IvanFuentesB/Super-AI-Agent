# Codex N+3.16 Video-to-Money Pipeline

Status: codex_planning_audit_only / video_to_money_pipeline / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Purpose

Design the workflow for turning money-making videos into product ideas, content, experiments, and ethical distribution assets. Ghoti must not claim to watch a video unless transcript, notes, or a legal/TOS-safe source is available.

## Source Truth Rules

- If a transcript is provided, Gemma can summarize it locally.
- If no transcript is provided, the user must provide transcript, notes, or approved source material.
- Ghoti should not scrape or download video content unless a later milestone explicitly approves a legal/TOS-safe method.
- Screenshots or comments require separate approval and must be used only when allowed.
- Summaries should cite source metadata and preserve uncertainty.

## Pipeline Steps

1. User provides YouTube URL plus transcript, notes, or legal/TOS-safe source.
2. Create `14_context/money_workflows/<slug>/`.
3. Save metadata and compact source excerpt.
4. Gemma creates first-pass summary.
5. Gemma extracts business mechanism, tools, skills, costs, and risks.
6. Codex audits feasibility and safety.
7. Generate products/content/experiments.
8. User approves any external action.
9. Claude Code implements templates or local tools only if requested.
10. Metrics are added to the experiment tracker if anything is published manually.

## Extract From Each Video

- main claim
- monetization mechanism
- required skills
- capital required
- time required
- tools required
- proof quality
- risks
- legal/TOS concerns
- minimum viable experiment
- productizable templates
- content angles
- email lead magnet ideas
- approval checklist

## Proof Quality Rubric

| Level | Meaning |
| --- | --- |
| 1 | Anecdote only, no proof. |
| 2 | Screenshots or claims without context. |
| 3 | Some process detail and plausible examples. |
| 4 | Clear steps, constraints, and realistic numbers. |
| 5 | Transparent case study with verifiable outcomes and caveats. |

Low proof does not mean useless; it means the experiment should be smaller, cheaper, and more skeptical.

## Required Output Package

`business_model_summary.md`:

- main claim
- buyer/customer
- offer
- acquisition channel
- delivery mechanism
- monetization path
- proof quality score
- key caveats

`content_ideas.md`:

- 10 content ideas
- platform fit
- hook
- format
- call to action
- approval status

`digital_product_ideas.md`:

- 5 product ideas
- buyer
- pain solved
- MVP format
- estimated effort
- risk

`mvp_experiments.md`:

- 3 MVP experiments
- hypothesis
- required asset
- distribution channel
- approval needed
- metrics to track

`risk_checklist.md`:

- TOS/platform risk
- copyright/reuse risk
- false income claim risk
- privacy risk
- paid tool risk
- outreach/spam risk
- regulated advice risk

`approval_checklist.md`:

- publish approval
- spending approval
- account approval
- outreach approval
- affiliate approval
- platform/tool approval
- legal/finance review if applicable

## Gemma Prompt Shape

Use compact local prompts:

```text
You are helping summarize a user-provided transcript for internal planning.
Do not invent facts.
Extract:
1. main claim
2. monetization mechanism
3. required skills
4. required tools
5. risks
6. 3 minimum viable experiments
7. 5 productizable templates
8. 10 content angles
Keep output concise and label uncertainty.
```

## Codex Audit Questions

- Is the model legal and ethical?
- Does it depend on fake engagement, spam, scraping abuse, or deception?
- Does it require paid tools or live accounts?
- Are the claims realistic?
- What is the smallest safe experiment?
- What can be productized without copying the creator?
- What should remain manual?

## Claude Code Later Implementation

Claude Code can later implement:

- `video_to_money_intake_template.md`
- `business_model_summary.template.md`
- `digital_product_idea_card_template.md`
- `mvp_experiment.template.md`
- `content_batch_template.md`
- `approval_checklist.md`
- optional local CLI that creates folders and blank templates

No automation should fetch videos, scrape comments, post content, send outreach, spend money, or use live accounts in the first implementation.

## Example Minimum Viable Experiment

```yaml
experiment_id: money_video_001
source: user-provided transcript
claim: "Short templates for AI operators can attract builders."
asset: "AI Operator Starter Kit outline"
channel: "manual LinkedIn/X draft, not posted yet"
approval_required:
  - publish approval
metrics:
  - impressions
  - clicks
  - replies
  - opt_ins
decision: "draft only"
```

## Final Verdict

The video-to-money pipeline should start as a local artifact system. Gemma extracts and compresses. Codex audits. The user approves. Claude Code builds templates. External distribution remains manual until a later explicit approval gate.
