# CUA / TryCUA Exact Source Evaluation

Status label: `exact_source_evaluation / no_install / not_runtime_wired`
Date: 2026-04-27
Branch: `feat/ghoti-visible-operator-stack`
Milestone: N+3.4
Auditor: Claude Code (Sonnet 4.6)

---

## Verdict

- **Canonical source identified:** YES — `https://github.com/trycua/cua`
- **Clone performed:** NO
- **Install performed:** NO
- **Runtime wired:** NO
- **Sandbox-first required:** YES

---

## Candidate Repositories

| Repo | URL | Notes |
|------|-----|-------|
| **trycua/cua** (canonical) | https://github.com/trycua/cua | Primary open-source repo; Y Combinator company; active through 2026 |
| trycua/acu | https://github.com/trycua/acu | Curated resource list (not a runtime tool) |
| syntax-syndicate/cua-agent | https://github.com/syntax-syndicate/cua-agent | Docker Container mirror/fork; not canonical |
| ykeselman/trycua-computer | https://github.com/ykeselman/trycua-computer | Fork focused on VM management; not canonical |

---

## Canonical Source: trycua/cua

- **URL:** https://github.com/trycua/cua
- **Organization:** https://github.com/trycua
- **Why canonical:** Official trycua organization repo; Y Combinator company (CUA); primary README and documentation; most stars and commits; active releases through March 2026.
- **Founded:** 2025, by Francesco Bonacci
- **License:** MIT (open-source; commercial use permitted; attribution required)
- **Last release observed:** Ongoing maintenance through March 2026

---

## Architecture (Three Layers)

| Layer | Name | Role |
|-------|------|------|
| 1 | **Lume** | High-performance VM virtualization (Apple Virtualization.Framework) |
| 2 | **CUI** | Computer-Use Interface — screen observation and interaction for Lume VMs |
| 3 | **CUA** | Computer-Use Agent — LLM-driven workflows on top of CUI |

---

## Install Method (if documented)

From README:
```bash
# macOS/Apple Silicon install via Homebrew (Lume)
brew install trycua/tap/lume

# Python SDK install
pip install cua-computer cua-agent

# Or use MCP server for Claude Code / Cursor integration
```

Python SDK entry points: `cua-computer`, `cua-agent`
CLI / MCP server: supported for Claude Code and Cursor

---

## OS Requirements — CRITICAL FINDING

| Requirement | Status |
|------------|--------|
| **Host OS for Lume (VM layer):** macOS on Apple Silicon ONLY | **INCOMPATIBLE with current Windows environment** |
| Guest OS inside VMs: macOS, Linux, Windows (running inside the VM) | N/A on Windows host |
| Docker alternative: possible for Linux-only CUA without Lume | Requires investigation |
| Windows-native CUA: NOT covered by canonical trycua/cua | Alternative needed |

**Finding:** The canonical `trycua/cua` uses Apple's Virtualization.Framework (Lume) which requires macOS on Apple Silicon. Our environment is Windows 11. The canonical trycua/cua cannot run as a host on Windows.

---

## Alternatives for Windows

| Alternative | Notes |
|------------|-------|
| Docker-based CUA (Linux container) | Possible without Lume; requires Docker Desktop on Windows |
| syntax-syndicate/cua-agent | Docker Container fork; may work on Windows; not audited |
| AutoBrowser (already cloned) | Docker Compose, Python/Playwright; Windows feasible; closer to Ghoti model |
| Anthropic Computer Use (Claude) | Cloud-based; requires API key; not local |

---

## Does It Need Docker/VM?

- **Yes** — Lume spins macOS or Linux VMs using Apple's Virtualization.Framework
- Without Lume (Linux Docker variant): Docker required for isolation
- No bare-metal option documented for Windows

---

## API Keys Required?

- **LLM API key required:** YES — supports Anthropic (Claude), OpenAI, and open-source models
- **No proprietary cloud service** beyond the LLM provider; agent logic runs locally
- **Metered cost:** YES if using Claude or OpenAI API

---

## Capabilities

| Capability | Supported |
|-----------|-----------|
| Screenshots / observe screen | YES |
| Click | YES (inside VM) |
| Type | YES (inside VM) |
| Windows guest control | YES (inside VM) |
| macOS host required | YES (for canonical Lume-based setup) |

---

## Main Risks

| Risk | Assessment |
|------|-----------|
| macOS-only host requirement | **Blocks use on current Windows environment** |
| VM/Docker isolation | Mitigates desktop-control blast radius |
| LLM API cost | Metered; need explicit budget approval |
| Full desktop control inside VM | High risk if misconfigured; sandbox isolation critical |
| Screenpipe / screenshot retention | Must enforce 3-day retention policy if used |

---

## Safe Next Step

1. Identify a Windows-compatible CUA alternative (Docker-based cua-agent or AutoBrowser) rather than canonical trycua/cua.
2. If macOS machine is available in the future, evaluate canonical trycua/cua in a VM sandbox.
3. Create CUA sandbox profile for whichever approach is selected (see `23_configs/cua_sandbox_profile.example.json`).
4. No clone or install until the approach is confirmed and operator explicitly approves in session.

---

## Explicit Verdict

- **Clone/install:** NOT DONE — no approval granted in this session
- **Runtime wiring:** NO
- **Sandbox-first:** YES — required before any execution
- **Windows compatibility (canonical trycua/cua):** BLOCKED — Apple Silicon required for Lume
- **Recommendation:** Evaluate Docker-based CUA variant or use AutoBrowser as the Windows-compatible supervised browser/CUA path
- **Status:** `exact_source_evaluation / windows_incompatible / no_install / not_runtime_wired`
