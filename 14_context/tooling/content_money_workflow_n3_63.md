# Content Money Workflow — N+3.63A

**Script:** `03_scripts/content_money_workflow.py`
**Config:** `23_configs/content_money_workflow.example.json`
**Output dir:** `14_context/content_workflows/` (planning artifacts only, not staged)

## Purpose

Local-first workflow planner for legal/ethical faceless content experiments.
Does NOT generate or upload videos. Creates planning artifacts and stage checklists.

## Inspiration

- MoneyPrinter V1 (FujiwaraChoki/MoneyPrinter) — pipeline stages
- OpenFang Clip hand concept (RightNow-AI/openfang) — gated content action
- Ghoti approval gates — human review required
- LLM Council — idea review and multi-perspective analysis

## Safety Constraints

- No live posting
- No upload
- No account login
- No fake engagement
- No copyrighted media assumption
- No scraping without legality review
- No spam outreach
- Human approval gates before any publish/upload
- Platform ToS review required
- Output is planning only

## Workflow Stages

1. **niche_selection** — Choose a niche and target audience. Human decides.
2. **content_angle_research** — Research angles, hooks, and format ideas. Planning only.
3. **script_outline** — Draft a script outline for the short. Text artifact only.
4. **asset_sourcing_plan** — Plan which assets are needed. No download or sourcing yet.
5. **rights_check** — HUMAN gate: check all planned assets for rights/license. Required.
6. **voice_subtitle_plan** — Plan voice-over approach and subtitle strategy. No recording yet.
7. **edit_checklist** — Generate a checklist for the editing stage. Human edits.
8. **metadata_seo_checklist** — Generate title/description/tag ideas. Human reviews before use.
9. **human_review_gate** — HUMAN gate: full review of script, assets plan, metadata. Required before any upload.
10. **manual_publish_or_future_approved_publisher** — Human manually publishes, or waits for a future approved automated publisher.

## Approval Gates

- `rights_check` — No asset sourcing without rights confirmation
- `brand_safety` — No content that violates brand or ethical standards
- `platform_tos` — No upload without ToS review
- `final_human_review` — Complete human review of all artifacts
- `publish_approval` — Explicit human approval to publish

## CLI Modes

```bash
python 03_scripts/content_money_workflow.py --status
python 03_scripts/content_money_workflow.py --plan --niche "..." --platform youtube_shorts --dry-run
python 03_scripts/content_money_workflow.py --plan --niche "..." --platform youtube_shorts --apply
python 03_scripts/content_money_workflow.py --shot-list --topic "..." --count 10 --dry-run
python 03_scripts/content_money_workflow.py --shot-list --topic "..." --count 10 --apply
python 03_scripts/content_money_workflow.py --workflow-check --dry-run
python 03_scripts/content_money_workflow.py --workflow-check --apply
```

## Supported Platforms (planning only)

- youtube_shorts
- tiktok
- instagram_reels

Publishing is disabled for all platforms until explicit approval.
