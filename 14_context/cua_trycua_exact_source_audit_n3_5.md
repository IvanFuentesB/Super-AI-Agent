# CUA / TryCUA Exact Source Audit — N+3.5

Status label: `exact_source_verified / read_only / not_runtime_wired`
Date: 2026-04-27
Branch: `feat/ghoti-visible-operator-stack`
Milestone: N+3.5
Auditor: Claude Code (Sonnet 4.6)
Method: `git ls-remote` (remote HEAD verified) + shallow clone inspect

---

## Exact Source Verification

| Field | Value |
|-------|-------|
| **Source URL** | https://github.com/trycua/cua |
| **Organization** | https://github.com/trycua |
| **Remote HEAD (ls-remote)** | `46dbcb47802e2c712c87e9a34d4d5b06829a2932` |
| **Clone HEAD (verified)** | `46dbcb47802e2c712c87e9a34d4d5b06829a2932` |
| **Remote matches clone** | YES |
| **Status** | `exact_source_verified` |

---

## License

- **License:** MIT (open-source; commercial use permitted; attribution required)
- **Copyright:** 2025 Cua AI, Inc.

---

## Purpose (from README)

CUA is a mono-repo for building, benchmarking, and deploying agents that use computers. Three core components:

| Component | Role |
|-----------|------|
| **Cua Driver** | Background computer-use on macOS — drive native apps without stealing cursor/focus |
| **Cua Sandbox** | Agent-ready sandboxes for any OS via VM or Docker; one API across environments |
| **Cua Bench** | Benchmarks and RL environments for computer-use evaluation |

---

## OS Support — Updated Finding

| Path | Host OS Required | Status in This Environment |
|------|-----------------|---------------------------|
| **Lume (macOS VMs)** | macOS/Apple Silicon only | BLOCKED — Windows 11 host |
| **Cua Driver (macOS)** | macOS only | BLOCKED — Windows 11 host |
| **Windows Sandbox** | Windows 11 Pro/Enterprise | BLOCKED — OS is Windows 11 Home |
| **Docker/Ubuntu** | Any OS with Docker | BLOCKED — Docker not installed, WSL not installed |
| **Cloud containers** | Any (cloud infra) | NOT EVALUATED — no cloud service connection |

**Updated verdict:** All local execution paths are currently blocked on this Windows 11 Home machine.
- Lume: macOS/Apple Silicon only
- Windows Sandbox: requires Pro/Enterprise (this is Home)
- Docker/Ubuntu: requires Docker Desktop (not installed)
- WSL: not installed

**Cloud path exists but requires external service connection — not evaluated.**

---

## Install Surface

| Method | Command |
|--------|---------|
| Cua Driver (macOS) | `curl install.sh` → Homebrew + Swift package |
| Python SDK | `pip install cua` (requires Python ≥ 3.12) |
| Docker/Ubuntu | Docker pull + KasmVNC |
| Windows Sandbox | Windows feature enable + XML config |

Python version requirement: `>=3.12,<3.14` — our env has Python 3.13.3 ✓

Dependencies: `openai` (LLM), `anthropic` (LLM) — LLM API key required for agent tasks.

---

## API Keys Required?

- **LLM API key:** YES — Anthropic or OpenAI key required for agent operation
- **Cua cloud:** Optional (cloud infra for production workloads)
- **Local paths:** No paid service for Driver/Sandbox if running locally

---

## Security / Privacy Risks

| Risk | Assessment |
|------|-----------|
| Desktop screenshot capture | Controlled per session; not background-persistent |
| Live desktop control | Only inside VM/sandbox; no host desktop control |
| LLM API cost | Metered per token; needs budget approval |
| Credential capture | Must be blocked at ActionIntent level (sandbox-only profile enforced) |
| Sandbox escape | VM/container isolation mitigates; no bare-metal host control documented |

---

## Clone Status

- **Clone performed:** YES — shallow clone to `21_repos/third_party/evals/cua`
- **Depth:** 1 (shallow)
- **Install performed:** NO
- **Examples run:** NO
- **Dependencies installed:** NO
- **Runtime wired:** NO

---

## Next Safe Step

1. Install Docker Desktop on this Windows 11 Home machine to unlock the Docker/Ubuntu CUA path.
2. Alternatively: access a macOS/Apple Silicon machine for the canonical Lume-based path.
3. Do NOT install until operator explicitly approves Docker Desktop in session.
4. Keep CUA adapter descriptor as `descriptor_only` / `can_execute=false` until a local path is confirmed.
