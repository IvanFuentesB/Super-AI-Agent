# External Repo Intake Catalog — N+3.63A

Generated: 2026-05-07T07:52:38Z

**Purpose:** Local catalog of external repo candidates for Ghoti supervised MVP.
No clone, no install, no runtime wiring. Intake and planning only.

---

## OpenFang (Python gateway candidate — aidiss/openfang)

- **repo_id:** `openfang_python_gateway`
- **possible_github:** `aidiss/openfang`
- **source_url_note:** openfang.ai — lightweight Python AI agent gateway, messaging channels, tools, skills, persistent memory, FastAPI/HTMX/Alpine, ~5K LOC
- **category:** agent_gateway
- **language_guess:** Python
- **clone_allowed_now:** False
- **install_allowed_now:** False
- **runtime_wiring_allowed_now:** False

**Why relevant to Ghoti:** Channel gateway concepts, tool/skill organization, compact local operator gateway pattern compatible with Ghoti's Python-first stack.

**Useful patterns:**
- messaging channel abstraction
- skills/tools registry
- persistent memory without heavy dependencies
- FastAPI local API gateway
- HTMX/Alpine lightweight frontend

**Risks:**
- messaging tokens for live channel actions
- external provider keys (Slack, Discord, Telegram etc.)
- live channel message dispatch

**Safe next action:** Read source structure docs only; design Ghoti channel gateway adapter scaffold inspired by pattern

**Ambiguity note:** Multiple projects use the name 'OpenFang'. This entry is specifically for aidiss/openfang (Python gateway). Do NOT conflate with RightNow-AI/openfang (Rust Agent OS).

---

## OpenFang (Rust Agent OS candidate — RightNow-AI/openfang)

- **repo_id:** `openfang_rust_agent_os`
- **possible_github:** `RightNow-AI/openfang`
- **source_url_note:** openfang.sh/app/cc — Rust Agent OS, 14 crates, Hands (Clip/Lead/Collector/etc.), many channel adapters, providers, security systems
- **category:** rust_agent_os
- **language_guess:** Rust
- **clone_allowed_now:** False
- **install_allowed_now:** False
- **runtime_wiring_allowed_now:** False

**Why relevant to Ghoti:** Eventual Rust daemon, scheduler, security layers, audit trail inspiration. Content Clip hand concept is relevant to supervised content workflow design.

**Useful patterns:**
- Hands abstraction (Clip/Lead/Collector)
- security/audit architecture in Rust
- crate-level modular agent OS design
- channel adapter pattern at scale
- scheduler + audit trail separation

**Risks:**
- autonomous scheduled agents
- many live channel adapters
- external providers wired at runtime
- live posting via Clip hand if not gated

**Safe next action:** Read architecture docs and crate names only; sketch a future Ghoti Rust daemon inspired by crate layout

**Ambiguity note:** Multiple projects use the name 'OpenFang'. This entry is specifically for RightNow-AI/openfang (Rust Agent OS). Do NOT conflate with aidiss/openfang (Python gateway).

---

## MoneyPrinter V1 (FujiwaraChoki/MoneyPrinter by DevBySami)

- **repo_id:** `moneyprinter_shorts`
- **possible_github:** `FujiwaraChoki/MoneyPrinter`
- **source_url_note:** GitHub FujiwaraChoki/MoneyPrinter — YouTube Shorts generation from a topic. Ollama-first script gen. DB-backed queue/API/worker/Postgres.
- **category:** content_generation_pipeline
- **language_guess:** Python
- **clone_allowed_now:** False
- **install_allowed_now:** False
- **runtime_wiring_allowed_now:** False

**Why relevant to Ghoti:** Content generation workflow inspiration, YouTube Shorts pipeline stages, local Ollama script/metadata generation, queue design patterns.

**Useful patterns:**
- topic → script → video pipeline stages
- Ollama-first local LLM script generation
- DB-backed job queue for content tasks
- API/worker architecture for content pipeline
- metadata and SEO generation scaffold

**Risks:**
- platform ToS violations (YouTube upload, TikTok voice API)
- copyrighted media or music inclusion
- TikTok voice synthesis API (external, ToS risk)
- YouTube upload OAuth (live account action)
- potential for spam or low-quality content at scale

**Safe next action:** Study pipeline stage design only; adapt stage structure to Ghoti content_money_workflow scaffold (planning artifacts, no upload)

---

## MoneyPrinterV2 (FujiwaraChoki/MoneyPrinterV2 — higher risk)

- **repo_id:** `moneyprinter_v2`
- **possible_github:** `FujiwaraChoki/MoneyPrinterV2`
- **source_url_note:** GitHub FujiwaraChoki/MoneyPrinterV2 — expands toward YouTube Shorts, Twitter/X, affiliate marketing, local business outreach
- **category:** monetization_automation
- **language_guess:** Python
- **clone_allowed_now:** False
- **install_allowed_now:** False
- **runtime_wiring_allowed_now:** False

**Why relevant to Ghoti:** Modular workflow concepts and content/money experiments. Separate from V1 and higher risk.

**Useful patterns:**
- modular platform adapter design
- content type diversification (video + social + affiliate)

**Risks:**
- social bots (Twitter/X automation)
- affiliate marketing automation (may violate platform ToS)
- cold outreach automation (spam risk)
- legal/ToS risk across multiple platforms
- higher risk than V1 due to multi-platform social posting scope

**Safe next action:** Planning/intake only. Do not clone or reference any V2 code until V1 audit is complete and human has reviewed ToS implications.

**Restriction:** planning_intake_only

---

## Karpathy LLM Council (karpathy/llm-council)

- **repo_id:** `karpathy_llm_council`
- **possible_github:** `karpathy/llm-council`
- **source_url_note:** GitHub karpathy/llm-council — multi-model debate/synthesis scaffold
- **category:** llm_orchestration
- **language_guess:** Python
- **clone_allowed_now:** False
- **install_allowed_now:** False
- **runtime_wiring_allowed_now:** False

**Why relevant to Ghoti:** Model council debate and synthesis for idea review and multi-perspective analysis.

**Useful patterns:**
- multi-model debate flow
- chairman synthesis
- peer review between models

**Risks:**
- external API keys if using cloud providers
- cost if not using local Ollama fallback

**Safe next action:** Already implemented as local-first scaffold in N+3.61A via llm_council_runner.py. Continue using local_demo mode.

**Implementation status:** implemented_n3_61a_local_scaffold

---
