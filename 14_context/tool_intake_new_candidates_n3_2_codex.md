# New Tool Intake Candidates - N+3.2 Codex

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Status label: intake_only / research_only / not_runtime_wired

No tools were installed, cloned, deployed, connected, or wired by this Codex lane.

## Candidate Table

| Tool | Category | Recommendation | Current truth |
|---|---|---|---|
| LTX-2 / Lightricks LTX-2 | content/video generation pipeline | research only | Mentioned candidate; exact runtime/license/resource requirements need verification. |
| ComfyUI / ComfyUI-LTXVideo | local content/media workflow | use soon after resource/license review | Strong local workflow candidate, but not core operator runtime. |
| Shannon / Keygraph Shannon / Shannon-like security tools | AppSec/security testing | research only | Authorized-target-only; exact source and scope need verification. |
| Proxima multi-AI MCP server | model/provider gateway | research only | Potential provider/TOS/session risk; no runtime wiring. |
| LibreChat | self-hosted LLM chat UI/gateway | research next | Useful operator UI/reference; secrets and auth need review. |
| AnythingLLM | local RAG/document workspace | use soon / research next | Strong local-first knowledge base candidate if data boundaries are clear. |
| Perplexica | search/RAG/research UI | research next | Useful research surface; web/API/TOS details need review. |
| Open WebUI | local Ollama/model UI | use soon / research next | Strong local LLM UI candidate; keep separate from Ghoti runtime until designed. |
| Nellavio | unknown | blocked until identified | Exact source unknown; needs search/verification before any evaluation. |

## LTX-2 / Lightricks LTX-2

- Purpose: likely video generation/model pipeline candidate.
- Why it may help Ghoti: could support future local or approved content factory workflows.
- Runtime category: content generation, media pipeline.
- Likely stack: model weights, GPU/runtime dependencies, possibly Python/ComfyUI integration.
- Local-first feasibility: possible but unverified; likely hardware-heavy.
- Account/API key risk: unknown; cloud variants may require accounts or paid credits.
- Safety/TOS risk: media rights, likeness, deepfake, and platform policy risk.
- Install risk: medium to high due model size and GPU/runtime dependencies.
- Data/privacy risk: input media and generated outputs may be sensitive.
- Recommendation: research only.
- Later Ghoti connection path: content generation proposals only, with human-reviewed prompts and explicit output approval before publishing.
- What NOT to do yet: no model pulls, no cloud account connection, no automated posting, no synthetic likeness/deepfake workflow.

## ComfyUI / ComfyUI-LTXVideo

- Purpose: node-based local image/video generation workflow host.
- Why it may help Ghoti: strong candidate for a local content factory workbench and reproducible media pipelines.
- Runtime category: local media pipeline.
- Likely stack: Python, GPU dependencies, model files, custom nodes.
- Local-first feasibility: high if hardware supports it, but setup can be large.
- Account/API key risk: low for local-only workflows; higher if cloud nodes/APIs are used.
- Safety/TOS risk: generated media rights, likeness, copyrighted style/data, platform posting rules.
- Install risk: medium to high due GPU/model/custom node drift.
- Data/privacy risk: local media may include private assets.
- Recommendation: use soon only after a dedicated setup milestone; otherwise research only.
- Later Ghoti connection path: ActionIntent for "generate local media draft" and separate approval before upload/post.
- What NOT to do yet: no automated posting, no paid/cloud nodes, no unreviewed model downloads, no deepfake/impersonation workflows.

## Shannon / Keygraph Shannon / Shannon-Like Security Tools

- Purpose: security research or AppSec tooling candidate.
- Why it may help Ghoti: could support authorized code/security review workflows.
- Runtime category: security analysis.
- Likely stack: unknown until exact source is verified.
- Local-first feasibility: unknown.
- Account/API key risk: unknown.
- Safety/TOS risk: high if used against systems without authorization.
- Install risk: unknown.
- Data/privacy risk: security scans may expose sensitive code, endpoints, or credentials.
- Recommendation: research only.
- Later Ghoti connection path: authorized-target-only scanner/report generator with explicit scope file and approval gate.
- What NOT to do yet: no scanning third-party targets, no exploitation, no credential testing, no malware/phishing/social engineering.

## Proxima Multi-AI MCP Server

- Purpose: possible MCP gateway for multiple AI providers/tools.
- Why it may help Ghoti: could centralize model/tool access later.
- Runtime category: MCP/model gateway.
- Likely stack: MCP server, provider credentials, local process.
- Local-first feasibility: partial; provider calls may be external.
- Account/API key risk: high due provider credentials and session handling.
- Safety/TOS risk: high if used for quota/cap bypass, shared sessions, or provider policy evasion.
- Install risk: medium until source reviewed.
- Data/privacy risk: prompts and tool calls may route through multiple providers.
- Recommendation: research only.
- Later Ghoti connection path: read-only status integration first, then explicit provider-by-provider approval if ever used.
- What NOT to do yet: no provider credentials, no session sharing, no cap bypass, no hidden routing of sensitive prompts.

## LibreChat

- Purpose: self-hosted multi-provider chat UI.
- Why it may help Ghoti: could become a local operator-facing LLM dashboard or reference for multi-provider UX.
- Runtime category: LLM chat UI/gateway.
- Likely stack: Node, database, provider keys, auth.
- Local-first feasibility: medium; self-hosted but often provider-connected.
- Account/API key risk: high if configured with provider keys.
- Safety/TOS risk: provider usage rules and data routing must be respected.
- Install risk: medium due services/database/auth.
- Data/privacy risk: chat logs and credentials are sensitive.
- Recommendation: research next.
- Later Ghoti connection path: local-only deployment review; never assume it is Ghoti runtime.
- What NOT to do yet: no deployment, no keys, no user auth import, no production use.

## AnythingLLM

- Purpose: local or self-hosted document/RAG workspace.
- Why it may help Ghoti: useful for local repo docs, skills, memory, and research retrieval.
- Runtime category: RAG/document knowledge base.
- Likely stack: local app, embeddings, vector store, optional provider/local model.
- Local-first feasibility: high if configured with local models.
- Account/API key risk: low for local-only; high if external providers are configured.
- Safety/TOS risk: low to medium; depends on ingested data rights and provider routing.
- Install risk: medium.
- Data/privacy risk: imported documents may be private.
- Recommendation: use soon / research next.
- Later Ghoti connection path: read-only local knowledge index for docs, with no autonomous actions.
- What NOT to do yet: no private data import without approval, no cloud sync, no provider keys by default.

## Perplexica

- Purpose: open-source search/research assistant style tool.
- Why it may help Ghoti: could support legal, TOS-aware research workflows.
- Runtime category: search/RAG/research UI.
- Likely stack: Node or web stack, search APIs or local search integrations, model provider.
- Local-first feasibility: partial; web search often needs external services.
- Account/API key risk: medium to high depending search/model providers.
- Safety/TOS risk: scraping/search API compliance and source attribution.
- Install risk: medium.
- Data/privacy risk: queries may contain sensitive research.
- Recommendation: research next.
- Later Ghoti connection path: human-reviewed research summaries with source links, no scraping abuse.
- What NOT to do yet: no unauthorized scraping, no hidden search APIs, no paid service connection.

## Open WebUI

- Purpose: local web UI for Ollama and model interaction.
- Why it may help Ghoti: practical local model console for Gemma/Ollama diagnostics and operator experiments.
- Runtime category: local LLM UI.
- Likely stack: web app/container, Ollama/local model connection.
- Local-first feasibility: high when paired with Ollama.
- Account/API key risk: low for Ollama-only; higher if external providers are configured.
- Safety/TOS risk: low for local diagnostics; still cannot be used to bypass law/safety.
- Install risk: medium due container/app setup.
- Data/privacy risk: chats/prompts may be stored locally.
- Recommendation: use soon / research next.
- Later Ghoti connection path: diagnostic UI only first; no operator action driver unless explicitly designed.
- What NOT to do yet: no provider keys, no runtime wiring, no claims that Open WebUI drives Ghoti.

## Nellavio

- Purpose: unknown.
- Why it may help Ghoti: unknown until exact source is identified.
- Runtime category: exact_source_unknown.
- Likely stack: unknown.
- Local-first feasibility: unknown.
- Account/API key risk: unknown.
- Safety/TOS risk: unknown.
- Install risk: unknown.
- Data/privacy risk: unknown.
- Recommendation: blocked until identified.
- Later Ghoti connection path: none until source, license, purpose, and risk are verified.
- What NOT to do yet: no clone, no install, no account creation, no runtime mention beyond watchlist.

## Existing Candidate Priority Summary

- RUFLO: high-priority multi-agent orchestration reference, still high-risk/research due security and trust concerns.
- AutoBrowser: best near-term supervised browser adapter candidate after ActionIntent policy and isolated Docker/profile review.
- Obscura: research only unless legal/TOS-gated and limited to authorized, non-stealth use.
- InvenTree: hardware/project inventory candidate, not operator runtime.
- OpenMontage/ComfyUI: content factory/media pipeline candidates; license, resource, and media-rights review first.
- Apify: jobs/internship/business research workflow candidate; TOS-aware only, no unauthorized scraping or spam.
