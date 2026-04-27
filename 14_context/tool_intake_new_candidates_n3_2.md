# Tool Intake — New Candidates N+3.2

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.2
Status label: intake_document / research_only / no_runtime_wiring

---

## Candidate: LTX-2 / Lightricks LTX-Video

| Field | Value |
|-------|-------|
| Purpose | AI video generation from text/image prompts |
| Why it may help Ghoti | Content-pipeline capability; could power video demos or operator-facing showcases |
| Current truth | LTX-2 (LTX-Video) is an open-weight model from Lightricks, available on HuggingFace |
| Risk level | Medium — large model download, GPU-heavy, no live account needed for local use |
| Install/runtime requirements | Python, PyTorch, CUDA GPU strongly recommended; CPU-only is impractical for video |
| Local-first feasibility | Yes if GPU is available; CPU-only is too slow for useful output |
| Account/API key risk | None for local inference; HuggingFace account may be needed for gated weights |
| Legal/TOS/safety boundary | Open weights; review Lightricks model license before commercial use |
| Use status | `research_only` — no GPU confirmed, no install approved |
| Next safe step | Verify GPU availability and disk space; operator approval before download |

---

## Candidate: ComfyUI + ComfyUI-LTXVideo

| Field | Value |
|-------|-------|
| Purpose | Node-based UI for AI image/video generation pipelines |
| Why it may help Ghoti | Visual content generation; can integrate LTX-Video, Stable Diffusion, etc. |
| Current truth | ComfyUI is actively maintained; ComfyUI-LTXVideo adds LTX model support |
| Risk level | Medium — large model files, but local-only by default |
| Install/runtime requirements | Python 3.10+, PyTorch, CUDA for GPU acceleration; considerable disk space |
| Local-first feasibility | Yes — ComfyUI runs fully locally with no cloud dependency |
| Account/API key risk | None for local; ComfyUI nodes that call external APIs would require review |
| Legal/TOS/safety boundary | ComfyUI is Apache-2.0; individual model licenses apply |
| Use status | `research_only` — no install approved |
| Next safe step | Operator approval before install; verify disk/GPU first |

---

## Candidate: Shannon (Security / Pentesting)

| Field | Value |
|-------|-------|
| Purpose | Security research, penetration testing, vulnerability analysis |
| Why it may help Ghoti | Security posture assessment for Ghoti's own systems; operator-controlled auditing |
| Current truth | Shannon-class tools include various open-source security frameworks; exact repo TBD |
| Risk level | High — dual-use; must only target systems the operator owns or has written permission for |
| Install/runtime requirements | Varies by tool; typically Python or Go |
| Local-first feasibility | Yes for most tools |
| Account/API key risk | None for local; some cloud-based scanning services require accounts |
| Legal/TOS/safety boundary | **Security research only. Must have owner permission for any target. No third-party scanning.** |
| Use status | `research_only` — blocked until operator provides explicit target authorization |
| Next safe step | Identify exact repo/tool; operator approval with stated authorized target before any use |

---

## Candidate: Proxima (Multi-AI MCP Server)

| Field | Value |
|-------|-------|
| Purpose | MCP server enabling multiple AI providers to share tool access and state |
| Why it may help Ghoti | Could reduce per-provider setup; multi-model operator hub |
| Current truth | Proxima is an emerging project; exact source and maturity level under review |
| Risk level | Medium-High — multi-provider session management may carry TOS/account session risks |
| Install/runtime requirements | Node.js or Python; requires provider API keys |
| Local-first feasibility | Partial — needs API keys; not fully local |
| Account/API key risk | HIGH — coordinates multiple provider accounts; session sharing may violate provider TOS |
| Legal/TOS/safety boundary | Must evaluate each provider's TOS for multi-session or shared-session use before enabling |
| Use status | `research_only` — blocked pending TOS review |
| Next safe step | Read Proxima source and each provider's TOS on multi-session use; operator decision before install |

---

## Candidate: TryCUA / CUA Driver

| Field | Value |
|-------|-------|
| Purpose | Computer-use agent framework for UI automation via structured action dispatch |
| Why it may help Ghoti | Structured computer-use with ActionIntent-compatible action dispatch; sandbox-first design |
| Current truth | TryCUA/CUA Driver is a candidate framework; exact repo and maturity under review |
| Risk level | High — computer-use has wide blast radius; live desktop/account access is a hard gate |
| Install/runtime requirements | Python; may require display server or VM for sandbox isolation |
| Local-first feasibility | Yes for sandbox; VM recommended for isolation |
| Account/API key risk | HIGH if used with live accounts; sandbox mode avoids this |
| Legal/TOS/safety boundary | No live account or full desktop autonomy until operator explicitly promotes from sandbox |
| Use status | `user_approval` in wait/resume queue — sandbox-first evaluation only |
| Next safe step | Operator approval for sandboxed eval; see `computer_use_strategy_note.md` gate requirements |

---

## Candidate: LibreChat

| Field | Value |
|-------|-------|
| Purpose | Open-source multi-provider chat UI with plugin and RAG support |
| Why it may help Ghoti | Local operator UI; could replace raw API calls with a friendly interface |
| Current truth | Actively maintained; Docker-based; supports OpenAI, Claude, Gemini, local models |
| Risk level | Low for local use; medium if cloud providers are wired |
| Install/runtime requirements | Docker or Node.js; MongoDB for persistence |
| Local-first feasibility | Yes — designed for local self-hosting |
| Account/API key risk | Only if wired to cloud providers; local-only mode avoids this |
| Legal/TOS/safety boundary | MIT license; provider TOS applies only to configured APIs |
| Use status | `research_only` — not installed or runtime-wired |
| Next safe step | Operator approval for local install evaluation |

---

## Candidate: AnythingLLM

| Field | Value |
|-------|-------|
| Purpose | Local RAG platform with document ingestion, multi-model support, and operator UI |
| Why it may help Ghoti | Local knowledge base for Ghoti context docs; operator Q&A without cloud |
| Current truth | Actively maintained; supports Ollama, OpenAI, Claude; easy local install |
| Risk level | Low for local use |
| Install/runtime requirements | Node.js or Docker; works with local Ollama models |
| Local-first feasibility | Yes — strong local support |
| Account/API key risk | None for local Ollama; cloud APIs add key risk |
| Legal/TOS/safety boundary | MIT license |
| Use status | `research_only` — not installed |
| Next safe step | Operator approval for local install; good candidate for Ghoti context RAG |

---

## Candidate: Perplexica

| Field | Value |
|-------|-------|
| Purpose | Open-source AI search engine with local model support |
| Why it may help Ghoti | Operator research without cloud search APIs; local Ollama integration |
| Current truth | Actively maintained; Next.js frontend, Node backend; Ollama integration available |
| Risk level | Low for local use; search APIs add external call risk |
| Install/runtime requirements | Node.js, Docker; Ollama for local inference |
| Local-first feasibility | Yes |
| Account/API key risk | Only if external search APIs (SearXNG, etc.) are wired |
| Legal/TOS/safety boundary | MIT license |
| Use status | `research_only` — not installed |
| Next safe step | Operator approval for local install |

---

## Candidate: Open WebUI

| Field | Value |
|-------|-------|
| Purpose | Feature-rich web UI for Ollama and OpenAI-compatible APIs |
| Why it may help Ghoti | Operator-facing chat UI for local Gemma/Ollama models; no coding required |
| Current truth | Actively maintained; Docker-based; supports Ollama natively |
| Risk level | Low for local use |
| Install/runtime requirements | Docker or pip install; Ollama required for local models |
| Local-first feasibility | Yes |
| Account/API key risk | None for local Ollama |
| Legal/TOS/safety boundary | MIT license |
| Use status | `research_only` — not installed |
| Next safe step | Operator approval; best used after Ollama + Gemma are installed and approved |

---

## Candidate: Nellavio (or Nellavio-like)

| Field | Value |
|-------|-------|
| Purpose | Unknown — candidate name provided; exact repo/project not confirmed |
| Why it may help Ghoti | TBD — purpose unclear without confirmed source |
| Current truth | `exact_source_unknown / needs_search` |
| Risk level | Unknown until source is identified |
| Install/runtime requirements | Unknown |
| Local-first feasibility | Unknown |
| Account/API key risk | Unknown |
| Legal/TOS/safety boundary | Unknown |
| Use status | `needs_search` — do not install or evaluate until source is confirmed |
| Next safe step | Operator provides exact repo URL or description; then re-evaluate |

---

## Boundary Summary

| Candidate | Gate |
|-----------|------|
| Shannon | Security-research only; operator must own/have permission for target |
| TryCUA/CUA Driver | Sandbox-first; no live account/full desktop until explicitly promoted |
| Proxima | Provider TOS review required before any session use |
| LTX-2/ComfyUI | No paid/cloud connection without approval; GPU/disk check first |
| LibreChat/Open WebUI/AnythingLLM/Perplexica | Local/operator UI candidates; not runtime-wired |
| Nellavio | Blocked until source is confirmed |
