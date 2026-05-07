# Ghoti Next Implementation Plan

Date: 2026-04-26
Branch: `feat/ghoti-visible-operator-stack`
Milestone produced: N+2.9
Status: `implementation_plan / not_runtime_wired / approval_gated`

---

## Current Status After N+2.9

Ghoti has completed 9 milestones of external evaluation and skill scaffolding. Key truths:

- Ghoti is NOT autonomous. Dashboard MVP is built but not operator-driven.
- RUFLO: cloned (`21_repos/third_party/evals/ruflo`, commit `01070ed`, v3.5.80). Source audited read-only. No install. Verdict: isolated install candidate.
- AutoBrowser: cloned (`21_repos/third_party/evals/auto-browser`, commit `e646a48`, v1.0.2). Source audited read-only. No Docker run. Verdict: isolated install candidate.
- Obscura: cloned (`21_repos/third_party/evals/obscura`, commit `99e75f1`). Source audited read-only. No cargo build. Verdict: isolated build candidate.
- Gemma/Ollama: Ollama 0.9.2 present, 0 models installed. No prompt run. Status: diagnostic/status only.
- Rust: verified available locally (rustc 1.95.0). Not used for external repo build yet.
- Claude Code ↔ Codex bridge: manual_handoff_only.
- All skills: operator-side only, not runtime-wired.

---

## Track 1: RUFLO Multi-Agent Orchestration

**What it is:** Enterprise AI agent orchestration wrapping Claude Code. Deploy 60+ agent types in swarms with shared context/memory and MCP integration.

**Current position:** `isolated_clone_audit / no_install / no_runtime_wiring`

**Next safe milestone (N+3.0):** Isolated install + MCP descriptor audit
- Operator explicitly approves in terminal: `npm install --no-scripts --ignore-scripts`
- Run: `npm audit` and record findings
- Inspect all 314 MCP tool descriptors for injection patterns
- Run `npx claude-flow@v3alpha doctor` — read output, do not follow agent-start instructions
- Do NOT run `init`, `daemon start`, or any agent spawn command

**Approval gates:**
- Explicit operator terminal approval for npm install
- npm audit results reviewed before any further step
- MCP tool descriptors reviewed for injection risk before wiring into Claude Code

**What not to do:**
- Do not run `npx claude-flow@v3alpha init` — it writes to `.claude/settings.json` in the eval area
- Do not start the daemon
- Do not provide ANTHROPIC_API_KEY until after source audit
- Do not wire RUFLO into Ghoti runtime until approval gates, logs, and rollback are proven

**Expected value:** If approved after audit, RUFLO provides the multi-agent swarm framework that is central to Ghoti's long-term vision of many single-purpose agents with shared local memory.

**Risk level:** HIGH — prior security incidents; 314-tool MCP surface; requires API key and metered API credits

---

## Track 2: AutoBrowser Supervised Browser/Operator Candidate

**What it is:** MCP-native browser control plane with human takeover (noVNC), approval gates, audit trails, and auth profile reuse. Python/FastAPI + Docker Compose + Playwright.

**Current position:** `isolated_clone_audit / no_install / no_runtime_wiring`

**Next safe milestone (N+3.1):** Isolated Docker run
- Operator confirms Docker Desktop is installed and approves
- `cd 21_repos/third_party/evals/auto-browser && docker compose up --build`
- Verify: dashboard loads at `127.0.0.1:8000`, noVNC at `127.0.0.1:6080`
- Do not configure auth profiles until runtime review is complete
- Do not enable reverse-SSH tunnel

**Approval gates:**
- Docker Desktop presence confirmed
- Explicit operator terminal approval for `docker compose up`
- Runtime dashboard reviewed by operator before any auth profile or browser action

**What not to do:**
- Do not expose ports beyond 127.0.0.1
- Do not enable reverse-SSH tunnel
- Do not connect real accounts until operator has reviewed the running dashboard
- Do not use for stealth, CAPTCHA, or unauthorized access

**Expected value:** Most directly aligned tool for Ghoti's supervised browser operator layer. Human takeover and approval gates match Ghoti's safety model exactly.

**Risk level:** MEDIUM — explicit safety design; Docker required; auth profile data is local

---

## Track 3: Obscura Rust/Headless Candidate

**What it is:** Rust-based headless browser engine. Single binary, CDP server, Playwright/Puppeteer compatible, 30MB memory vs 200MB for Chrome, instant startup.

**Current position:** `isolated_clone_audit / no_build / no_runtime_wiring`

**Next safe milestone (N+3.2):** Pre-built binary evaluation (Windows .zip)
- Download pre-built `.zip` from releases page — no cargo build required
- Extract to a temp eval folder outside repo
- Test: `obscura --version` and `obscura fetch https://example.com --eval "document.title"`
- Do NOT use `--stealth` feature until TOS review is complete

OR (if operator prefers source build):
- `cd 21_repos/third_party/evals/obscura && cargo build --release` (5 min, V8 compiles)
- Operator approves build explicitly

**Approval gates:**
- Explicit operator approval for binary download or cargo build
- TOS review before using `--stealth` mode against any third-party site

**What not to do:**
- Do not use `--stealth` without explicit TOS review and operator approval
- Do not run against third-party sites without permission
- Do not use for anti-detection bypass of legitimate platform protections

**Expected value:** Lightweight browser alternative for high-volume, resource-constrained Ghoti browser tasks. CDP compatibility means existing Playwright tooling can target it without code changes.

**Risk level:** MEDIUM — stealth feature requires careful gating; Apache 2.0 license is permissive; single binary is simple to audit

---

## Track 4: Gemma/Ollama Local Diagnostic Brain Candidate

**What it is:** Local LLM (Gemma 3 via Ollama) for offline diagnostic reasoning, repo summarization, and future agent assistance without consuming Anthropic API credits.

**Current position:** `diagnostic_only / no_models_installed / not_runtime_wired`

**Next safe milestone (N+3.3):** Model pull approval
- Operator explicitly approves: `ollama pull gemma3:4b` (~2.5 GB download)
- Run triage prompt: `ollama run gemma3:4b "Summarize X in 5 bullets"`
- Save output to `14_context/gemma_repo_tool_triage_output.md` with `gemma_diagnostic_output_only` label
- Do NOT claim Gemma drives Ghoti or makes operator decisions

**Approval gates:**
- Explicit operator approval for `ollama pull`
- Disk space check before pull (~2.5 GB needed)

**What not to do:**
- Do not claim Gemma drives any Ghoti workflow
- Do not use Gemma for consequential decisions without human review
- Do not pull a model without explicit operator approval

**Expected value:** Free local diagnostic capability; reduces API credit consumption for summarization and triage tasks; future candidate for local agent memory summarization.

**Risk level:** LOW — fully local; no external accounts; no API credits; diagnostic only

---

## Track 5: Rust Install/Build Readiness

**What it is:** Rust toolchain is already verified locally (rustc 1.95.0, cargo 1.95.0). Needed for Obscura source build and potential future Ghoti native tooling.

**Current position:** `verified_available / not_used_for_external_builds`

**Next safe milestone:** Part of N+3.2 (Obscura build) or standalone Rust build test
- No new install needed — Rust is already available
- First use case: `cargo build --release` in `21_repos/third_party/evals/obscura/`

**Risk level:** LOW — toolchain already installed; no new install needed

---

## Track 6: PRD/Project Builder Workflow

**What it is:** A structured prompt/checklist process that requires every new app or project idea to start with a small PRD (product requirements doc) before implementation begins.

**Current position:** `concept_only / not_runtime_wired`

**Next safe milestone:** Create `13_prompts/codex_skills/ghoti-prd-builder/SKILL.md` with:
- PRD template: problem, users, scope, safety boundaries, success criteria
- Approval gate: no implementation without a completed PRD
- Integration with business research skill

**Risk level:** VERY LOW — documentation only

---

## Track 7: Content Factory Workflow (Later)

**What it is:** YouTube/social content production pipeline — research, script, review, publish — with strict human-in-the-loop and no autonomous posting.

**Current position:** `watchlist / concept_only`

**When to activate:** After at least Tracks 1–3 are partially operational. Content factory needs browser control (AutoBrowser), local reasoning (Gemma), and agent orchestration (RUFLO) to be meaningful.

**Risk level:** MEDIUM — autonomous posting risk if approval gates are not enforced; deferred until supervised infrastructure is proven

---

## Recommended 5-Milestone Path to First Ghoti Operator Loop

This path leads to the first real end-to-end Ghoti supervised operator action.

### Milestone N+3.0: RUFLO Isolated Install + MCP Audit
- `npm install --no-scripts` in ruflo eval area
- `npm audit` — record all findings
- Inspect MCP tool descriptors for injection
- Operator reviews before any agent spawn
- Deliverable: `14_context/ruflo_install_audit.md` with verdicts

### Milestone N+3.1: AutoBrowser Docker Run + Dashboard Review
- `docker compose up --build` in auto-browser eval area
- Verify dashboard, noVNC, API docs load
- Operator reviews dashboard UI and approval gate behavior
- Deliverable: `14_context/autobrowser_runtime_verification.md`

### Milestone N+3.2: Obscura Binary Test
- Download pre-built binary OR `cargo build --release`
- `obscura fetch https://example.com --eval "document.title"`
- Verify CDP server starts: `obscura serve --port 9222`
- Connect Playwright to Obscura CDP (test only, no live accounts)
- Deliverable: `14_context/obscura_runtime_verification.md`

### Milestone N+3.3: Gemma Model Pull + Triage Prompt
- `ollama pull gemma3:4b` (operator approves)
- Run triage prompt against repo tool intake doc
- Record exact output
- Deliverable: updated `14_context/gemma_repo_tool_triage_output.md`

### Milestone N+3.4: First Supervised Operator Loop (Prototype)
- Design a single narrow operator task: e.g., "navigate to a URL, take a screenshot, save to output/, return for human review"
- Wire AutoBrowser REST API to a new Ghoti dashboard action (approval-gated)
- Human must click approve before any browser action executes
- Full audit log recorded
- Deliverable: `01_projects/dashboard_mvp/` update with first real browser action route; `14_context/operator_loop_v1_verification.md`

---

## What Remains Manual / Unproven After N+2.9

- RUFLO agents: not spawned, not wired
- AutoBrowser: not running, not connected to Ghoti
- Obscura: not built, not running
- Gemma: no model installed
- Claude Code ↔ Codex bridge: manual_handoff_only
- All skills: operator-side only
- Ghoti autonomy: none
