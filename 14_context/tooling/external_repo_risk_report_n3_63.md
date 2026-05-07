# External Repo Risk Report — N+3.63A

Generated: 2026-05-07T07:52:39Z

**Purpose:** Safety risk summary for each tracked external repo candidate.
All items below are forbidden until explicitly audited and approved.

---

## OpenFang (Python gateway candidate — aidiss/openfang)

**Repo ID:** `openfang_python_gateway`

**Forbidden until audited:**
- wiring any messaging channel to live accounts
- storing provider tokens/keys in repo
- making outbound API calls to messaging platforms

**Risks:**
- messaging tokens for live channel actions
- external provider keys (Slack, Discord, Telegram etc.)
- live channel message dispatch

**Current gate status:**
- clone_allowed_now: False
- install_allowed_now: False
- runtime_wiring_allowed_now: False

---

## OpenFang (Rust Agent OS candidate — RightNow-AI/openfang)

**Repo ID:** `openfang_rust_agent_os`

**Forbidden until audited:**
- compiling or running any Rust crate
- wiring any Hand to a live account or service
- running scheduler
- connecting any channel adapter to a live endpoint

**Risks:**
- autonomous scheduled agents
- many live channel adapters
- external providers wired at runtime
- live posting via Clip hand if not gated

**Current gate status:**
- clone_allowed_now: False
- install_allowed_now: False
- runtime_wiring_allowed_now: False

---

## MoneyPrinter V1 (FujiwaraChoki/MoneyPrinter by DevBySami)

**Repo ID:** `moneyprinter_shorts`

**Forbidden until audited:**
- running the pipeline to generate or upload actual videos
- calling TikTok voice API
- using YouTube OAuth upload
- including any copyrighted media without license check
- automated posting of any kind

**Risks:**
- platform ToS violations (YouTube upload, TikTok voice API)
- copyrighted media or music inclusion
- TikTok voice synthesis API (external, ToS risk)
- YouTube upload OAuth (live account action)
- potential for spam or low-quality content at scale

**Current gate status:**
- clone_allowed_now: False
- install_allowed_now: False
- runtime_wiring_allowed_now: False

---

## MoneyPrinterV2 (FujiwaraChoki/MoneyPrinterV2 — higher risk)

**Repo ID:** `moneyprinter_v2`

**Forbidden until audited:**
- all automation features
- social posting of any kind
- affiliate outreach
- cold email or DM automation
- running any V2 feature without explicit legal/ToS review

**Risks:**
- social bots (Twitter/X automation)
- affiliate marketing automation (may violate platform ToS)
- cold outreach automation (spam risk)
- legal/ToS risk across multiple platforms
- higher risk than V1 due to multi-platform social posting scope

**Current gate status:**
- clone_allowed_now: False
- install_allowed_now: False
- runtime_wiring_allowed_now: False

---

## Karpathy LLM Council (karpathy/llm-council)

**Repo ID:** `karpathy_llm_council`

**Forbidden until audited:**
- storing API keys for external providers
- making external API calls without explicit user approval

**Risks:**
- external API keys if using cloud providers
- cost if not using local Ollama fallback

**Current gate status:**
- clone_allowed_now: False
- install_allowed_now: False
- runtime_wiring_allowed_now: False

---

## Global Safety Statements

- OpenFang intake only — no clone/install/run.
- MoneyPrinter intake only — no clone/install/run.
- Content workflow planning only — no upload, no post, no live actions.
- No secrets stored or read.
- No external API calls by default.
- Human review required before any real integration.
- '100%' means local-supervised MVP, not autonomous money machine.
