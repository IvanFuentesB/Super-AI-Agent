# CUA / TryCUA Isolated Clone Audit — N+3.5

Status label: `clone_complete / read_only_inspect_only / not_runtime_wired / dependencies_not_installed`
Date: 2026-04-27
Branch: `feat/ghoti-visible-operator-stack`
Milestone: N+3.5
Auditor: Claude Code (Sonnet 4.6)

---

## Clone Summary

| Field | Value |
|-------|-------|
| **Cloned** | YES |
| **Path** | `21_repos/third_party/evals/cua` |
| **Depth** | 1 (shallow) |
| **HEAD hash** | `46dbcb47802e2c712c87e9a34d4d5b06829a2932` |
| **Remote URL** | https://github.com/trycua/cua |
| **Remote HEAD verified** | YES — matches ls-remote output |
| **License** | MIT (2025 Cua AI, Inc.) |

---

## Key Files Found

| File/Dir | Type | Notes |
|----------|------|-------|
| `README.md` | Docs | Main project overview and install paths |
| `LICENSE.md` | License | MIT |
| `pyproject.toml` | Python config | workspace requires Python ≥3.12; deps: openai, anthropic |
| `Package.swift` | Swift package | Lume (macOS VM layer) — Swift + Apple frameworks |
| `Dockerfile` | Docker | Docker build for agent environment |
| `Makefile` | Build | Workspace build shortcuts |
| `uv.lock` | Lock file | Python UV lock (not pip) |
| `pnpm-lock.yaml` | Lock file | Node/pnpm lock for docs/UI |
| `libs/lume/` | Swift | macOS Virtualization.Framework — Apple Silicon only |
| `libs/cua-driver/` | Swift/scripts | Background macOS computer-use driver |
| `libs/python/` | Python | cua, cua-agent, cua-computer, mcp-server, etc. |
| `libs/qemu-docker/` | Docker | Linux (Ubuntu/QEMU), Windows, Android container images |
| `libs/kasm/` | KasmVNC | Web-accessible Ubuntu desktop in Docker |
| `libs/lumier/` | Python | Lume VM management SDK |
| `examples/agents/` | Python | Example agent scripts (test_linux_agent.py, etc.) |
| `examples/sandboxes/` | Mixed | Sandbox examples |
| `examples/sandboxes-cli/` | CLI | CLI sandbox examples |
| `libs/cua-driver/scripts/install.sh` | Install script | curl-based macOS install — NOT run |
| `libs/cua-driver/scripts/install-local.sh` | Install script | Local build — NOT run |
| `blog/windows-sandbox.md` | Docs | Windows Sandbox support path (June 2025) |
| `blog/ubuntu-docker-support.md` | Docs | Ubuntu Docker/KasmVNC path (Aug 2025) |

---

## Install Surface

| Surface | Method | Risk |
|---------|--------|------|
| Lume (macOS) | Homebrew + Apple Virtualization | macOS only; NOT run |
| Cua Driver (macOS) | curl + build-app.sh | macOS only; NOT run |
| Python SDK | `pip install cua` / UV | Python ≥3.12 required; NOT run |
| Docker/Ubuntu | Docker pull + run | Docker not installed on host; NOT run |
| Windows Sandbox | Windows feature + XML config | Requires Pro/Enterprise; host is Home |

**No install scripts were run. No dependencies installed.**

---

## Example Surface

| Directory | Contents |
|-----------|---------|
| `examples/agents/` | `test_linux_agent.py` — Linux VM agent test (requires running Lume/Docker) |
| `examples/computer-example-ts/` | TypeScript computer-use example |
| `examples/sandboxes/` | Various sandbox launch examples |
| `examples/sandboxes-cli/` | CLI-based sandbox examples |

**No examples were run.**

---

## macOS / Linux / Windows / Docker / VM Requirements

| Requirement | Finding |
|------------|---------|
| macOS/Apple Silicon for Lume | YES — Lume is macOS-only (Package.swift + Apple Virt.Framework) |
| macOS for Cua Driver | YES — Swift app; macOS-only binary |
| Docker for Linux container | YES — qemu-docker/linux uses Docker + QEMU/KVM |
| Windows Sandbox | YES — requires Windows 11 Pro/Enterprise (not Home) |
| KasmVNC | Used inside Docker container for web-accessible Linux desktop |
| LLM API key | YES — openai or anthropic key required for agent operation |
| Cloud option | YES — Cua cloud infrastructure (external service, not evaluated) |

---

## Windows Path on This Environment

| Path | Requirement | This Environment | Status |
|------|------------|-----------------|--------|
| Lume | macOS/Apple Silicon | Windows 11 Home | BLOCKED |
| Cua Driver | macOS | Windows 11 Home | BLOCKED |
| Windows Sandbox | Windows 11 Pro/Enterprise | Windows 11 Home | BLOCKED |
| Docker/Ubuntu | Docker Desktop | Not installed | BLOCKED |
| WSL | WSL installed | Not installed | BLOCKED |
| Cloud | External service | Not evaluated | NOT EVALUATED |

---

## Screenshot-Only Smoke Test Feasibility

| Question | Answer |
|----------|--------|
| Can observe_screen work on this host? | NO — all local paths blocked |
| Can screenshot be taken in Docker/Ubuntu? | YES if Docker installed |
| Can screenshot be taken in Windows Sandbox? | YES if Pro/Enterprise OS |
| Required next step | Install Docker Desktop or upgrade OS |

---

## Security / Privacy Risks

| Risk | Assessment |
|------|-----------|
| Desktop screenshot | Local-only when using sandbox; no background persistence |
| VM isolation | Mitigates desktop-control blast radius effectively |
| Install scripts | `curl | bash` pattern for macOS install — inspect before running |
| LLM API cost | Metered; explicit approval needed before agent tasks |
| Sandbox escape | Not documented in README; standard container isolation applies |
| Credential capture in VM | Must be blocked at ActionIntent level |

---

## Fit for Ghoti

| Dimension | Assessment |
|-----------|-----------|
| ActionIntent-compatible | YES — API action dispatch fits Ghoti's intent gate |
| Approval-gate compatible | YES — each UI action can flow through ActionIntent |
| Audit trail compatible | YES — actions can be logged to cua_action_audit.jsonl |
| Windows 11 Home usable now | NO — all local paths currently blocked |
| Future path | Docker Desktop install or macOS machine access |

---

## Explicit Status

- **Cloned:** YES — `21_repos/third_party/evals/cua` (shallow, read-only inspect)
- **Dependencies installed:** NO
- **Actions executed:** NO
- **Runtime wired:** NO
- **Third-party contents staged:** NO (untracked; third-party clone remains in .gitignore / untracked)

---

## Recommendation

1. Do NOT install CUA dependencies until operator approves Docker Desktop install.
2. Record Docker Desktop as required precondition in wait/resume gates.
3. Once Docker Desktop is installed and approved, evaluate `libs/qemu-docker/linux` path for Ubuntu container agent.
4. Keep CUA adapter as `descriptor_only` / `can_execute=false` until smoke test succeeds.
5. Revisit Windows Sandbox path only if OS is upgraded to Pro/Enterprise.
