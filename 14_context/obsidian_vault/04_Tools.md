# Ghoti Tool Candidates (Compact)

**Updated:** 2026-04-27 — Milestone N+3.7
**Source:** `14_context/tool_intake_new_candidates_n3_2.md`, `14_context/cua_driver_readiness_plan.md`, `14_context/openfang_rust_readiness_plan.md`

---

## Computer-Use

| Tool | Status | Priority |
|------|--------|---------|
| TryCUA / CUA Driver | evaluation_plan / sandbox_first / not_wired / Docker blocked | TOP — Docker install approval required first |
| AutoBrowser | evaluation_plan / not_wired | HIGH — needs approval gate |
| Obscura | binary_built / CDP_verified / not_wired | MEDIUM — Playwright smoke next |
| Browser Use | not_installed | LOW until browser-role task ready |

## Local UI / Knowledge

| Tool | Status | Priority |
|------|--------|---------|
| AnythingLLM | not_installed / low_risk | HIGH — local-first RAG |
| Open WebUI | not_installed / low_risk | HIGH — Ollama frontend |
| LibreChat | not_installed / medium_risk | MEDIUM |
| Perplexica | not_installed / medium_risk | MEDIUM |

## Media

| Tool | Status | Priority |
|------|--------|---------|
| LTX-2 | evaluation_only | LOW — GPU requirement |
| ComfyUI | evaluation_only | LOW — GPU requirement |

## Screen / Memory Capture

| Tool | Status |
|------|--------|
| Screenpipe | retention_plan_created / not_installed / not_wired / read-only status route added (N+3.7) |

## Rust Candidates

| Tool | Status |
|------|--------|
| OpenFang | exact_repo_unknown / rust_not_installed / evaluation_only |
| RUFLO | isolated_clone_audit_done / not_wired |

---

## Blocked Gates

- CUA: Docker not installed, WSL not installed — all local paths blocked on Windows 11 Home
- OpenFang: Rust not installed, exact repo unknown
- Gemma/Ollama: no models installed (ollama list empty)
- Screenpipe: status route exists; no capture until operator-start approval

> Full detail per candidate: `14_context/tool_intake_new_candidates_n3_2.md`
