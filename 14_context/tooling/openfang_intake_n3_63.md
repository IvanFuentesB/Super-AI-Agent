# OpenFang Intake — N+3.63A

**Status:** Intake only. No clone, no install, no run.

## Ambiguity Warning

Multiple projects use the name "OpenFang". Do not conflate them.

## Candidate A: aidiss/openfang (Python Gateway)

- **repo_id:** `openfang_python_gateway`
- **Possible GitHub:** aidiss/openfang
- **Source note:** openfang.ai — lightweight Python AI agent gateway, messaging channels, tools, skills, persistent memory, FastAPI/HTMX/Alpine, ~5K LOC
- **Language:** Python
- **Category:** agent_gateway

### Relevant patterns for Ghoti

- Messaging channel abstraction
- Skills/tools registry compatible with Ghoti worker pattern
- Persistent memory without heavy dependencies
- FastAPI local API gateway for operator interface
- HTMX/Alpine lightweight frontend pattern

### Risks

- Messaging tokens for live channel actions
- External provider keys (Slack, Discord, Telegram, etc.)
- Live channel message dispatch

### Forbidden until audited

- Wiring any messaging channel to live accounts
- Storing provider tokens/keys in repo
- Making outbound API calls to messaging platforms

### Safe next action

Read source structure docs only. Design a Ghoti channel gateway adapter scaffold inspired by the pattern.

## Candidate B: RightNow-AI/openfang (Rust Agent OS)

- **repo_id:** `openfang_rust_agent_os`
- **Possible GitHub:** RightNow-AI/openfang
- **Source note:** openfang.sh/app/cc — Rust Agent OS, 14 crates, Hands (Clip/Lead/Collector/etc.), channel adapters, providers, security systems
- **Language:** Rust
- **Category:** rust_agent_os

### Relevant patterns for Ghoti

- Hands abstraction (Clip/Lead/Collector) — maps to Ghoti worker/gate concept
- Security and audit architecture in Rust (future)
- Crate-level modular agent OS design
- Channel adapter pattern at scale
- Scheduler and audit trail separation

### Risks

- Autonomous scheduled agents
- Many live channel adapters
- External providers wired at runtime
- Live posting via Clip hand if not gated

### Forbidden until audited

- Compiling or running any Rust crate
- Wiring any Hand to a live account or service
- Running the scheduler
- Connecting any channel adapter to a live endpoint

### Safe next action

Read architecture docs and crate names only. Sketch a future Ghoti Rust daemon inspired by the crate layout.

## Gate Summary

| Field | Python Gateway | Rust Agent OS |
|-------|---------------|---------------|
| clone_allowed_now | false | false |
| install_allowed_now | false | false |
| runtime_wiring_allowed_now | false | false |
