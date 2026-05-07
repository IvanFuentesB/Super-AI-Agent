# MoneyPrinter Intake — N+3.63A

**Status:** Intake only. No clone, no install, no run.

## Note on Naming

"MoneyPrinter by DevBySami" maps to **FujiwaraChoki/MoneyPrinter** (V1).
MoneyPrinterV2 is a **separate, higher-risk project** (FujiwaraChoki/MoneyPrinterV2).
Do not conflate V1 and V2.

---

## V1: FujiwaraChoki/MoneyPrinter

- **repo_id:** `moneyprinter_shorts`
- **Possible GitHub:** FujiwaraChoki/MoneyPrinter
- **Language:** Python
- **Category:** content_generation_pipeline

### What it does

Automates YouTube Shorts generation from a topic:
- Ollama-first local LLM for script/metadata generation
- DB-backed job queue (Postgres)
- API + worker architecture
- Video rendering pipeline

### Relevant patterns for Ghoti

- Topic → script → video pipeline stages (maps to Ghoti workflow stages)
- Ollama-first local LLM (already in use via gemma_compact_memory_worker)
- DB-backed job queue design
- Queue/API/worker separation for content tasks
- Metadata and SEO generation scaffold

### Risks

- Platform ToS violations (YouTube upload OAuth)
- TikTok voice API (external, ToS risk)
- Copyrighted media or music
- Spam or low-quality content at scale
- Postgres dependency if run

### Forbidden until audited

- Running the pipeline to generate or upload actual videos
- Calling TikTok voice API
- Using YouTube OAuth upload
- Including any copyrighted media without license check
- Automated posting of any kind

### Safe next action

Study pipeline stage design only. Adapt stage structure to Ghoti `content_money_workflow` scaffold (planning artifacts, no upload).

---

## V2: FujiwaraChoki/MoneyPrinterV2 (Higher Risk)

- **repo_id:** `moneyprinter_v2`
- **Possible GitHub:** FujiwaraChoki/MoneyPrinterV2
- **Language:** Python
- **Category:** monetization_automation
- **Restriction:** planning_intake_only

### What it does

Expands toward YouTube Shorts, Twitter/X, affiliate marketing, local business outreach.

### Risks

- Social bots (Twitter/X automation)
- Affiliate marketing automation (platform ToS)
- Cold outreach automation (spam risk)
- Legal/ToS risk across multiple platforms

### Forbidden until audited

- All automation features
- Social posting of any kind
- Affiliate outreach
- Cold email or DM automation
- Running any V2 feature without explicit legal/ToS review

### Safe next action

Planning/intake only. Do not clone or reference any V2 code until V1 audit is complete and human has reviewed ToS implications.

---

## Gate Summary

| Field | V1 (Shorts) | V2 (Higher Risk) |
|-------|------------|-----------------|
| clone_allowed_now | false | false |
| install_allowed_now | false | false |
| runtime_wiring_allowed_now | false | false |
| restriction | — | planning_intake_only |
