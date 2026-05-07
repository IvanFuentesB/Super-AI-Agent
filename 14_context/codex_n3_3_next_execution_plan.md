# Codex N+3.3 Next Execution Plan

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Observed HEAD: bd6a76f
Status label: execution_plan_only / no_runtime_changes / not_runtime_wired

## Purpose

This plan turns the N+3.3 parallel audits into concrete next milestones without conflicting with Claude Code's current docs/scripts lane.

## N+3.4 - CUA Driver Exact Repo / Source Evaluation + Sandbox Test Plan

Goal: identify the exact CUA Driver / TryCUA source and produce a sandbox-only test plan.

Claude Code should:

- verify exact repo/source/license
- inspect install/build scripts without running them
- inspect dependencies and runtime permissions
- document Windows and sandbox requirements
- create a sandbox test checklist

Codex should:

- cross-check source/license findings
- review the sandbox test plan for approval-gate gaps
- confirm no runtime wiring occurred

ChatGPT should:

- sharpen the architecture and risk model
- decide whether the sandbox test is worth approving

User must approve:

- any clone
- any install
- any sandbox launch
- any screenshot or UI control test

Still forbidden:

- host desktop control
- live accounts
- credentials
- external actions
- cap/quota bypass

## N+3.5 - Screenpipe Dry-Run Retention + Dashboard Capture Status Route

Goal: design and validate local retention before capture.

Claude Code should:

- verify Screenpipe source/docs if approved
- create or validate a dry-run cleanup policy
- ensure default `retention_days = 3`
- add a read-only dashboard status route only if low-risk and local-only

Codex should:

- audit retention paths
- check that deletion cannot cross safe roots
- verify no capture/audio starts during docs-only work

ChatGPT should:

- refine operator-facing capture wording and retention policy

User must approve:

- any Screenpipe install
- any capture start
- any cleanup confirmation

Still forbidden:

- hidden recording
- cloud sync
- indefinite retention
- deleting outside allowed capture roots

## N+3.6 - Obsidian Vault Sync / Update Script

Goal: create a tiny markdown-only project memory vault.

Claude Code should:

- create `14_context/obsidian_vault/`
- seed the 8 recommended notes
- optionally add a local script that updates index metadata only
- avoid plugin installation

Codex should:

- validate note size, links, and safety language
- ensure no logs/secrets/private docs were copied

ChatGPT should:

- use the vault as top-level project context
- keep notes compact after each milestone

User must approve:

- any plugin installation
- any RAG import
- any private document ingestion

Still forbidden:

- giant transcript mirroring
- plugin install by default
- cloud sync by default

## N+3.7 - First Harmless CUA / Screenpipe ActionIntent Proposal, No Execution

Goal: prove Ghoti can propose a future adapter action without executing it.

Claude Code should:

- create a proposed ActionIntent for a harmless local/sandbox target
- include payload hash and adapter descriptor
- record audit event
- do not execute the adapter

Codex should:

- verify approval binding and replay/mismatch handling
- confirm execution remains disabled

ChatGPT should:

- review whether the proposed adapter contract is specific enough

User must approve:

- moving from proposal-only to sandbox execution in a later milestone

Still forbidden:

- clicking/typing
- host desktop control
- live accounts
- external web actions

## N+3.8 - Gemma Model Pull + Local Summarization If Approved

Goal: enable local summarization diagnostics only.

Claude Code should:

- ask for explicit operator approval before model pull
- run the exact approved `ollama pull` command only if approved
- run one local summarization diagnostic
- label output as diagnostic, not operator driver

Codex should:

- validate model/status truth
- confirm no model drives actions

ChatGPT should:

- decide where local summaries help reduce prompt size

User must approve:

- model download
- disk/GPU usage
- any local model integration beyond diagnostics

Still forbidden:

- claiming Gemma drives Ghoti actions
- using local models to bypass provider limits
- forwarding private data to unreviewed tools

## Cross-Milestone Guardrails

- ActionIntent gates stay mandatory.
- Computer-use candidates remain sandbox-first.
- Screen/audio capture stays local-only, explicit, and retention-limited.
- Obsidian stays markdown-only until plugin/RAG approval.
- External tools remain research-only until a dedicated implementation milestone.
- No deployment, paid service connection, autonomous posting, fake engagement, spam, trades, purchases, legal/tax filing, malware, phishing, or unsafe weapons guidance.

## Recommended Immediate Next Step

Recommended next milestone: N+3.4 CUA Driver exact source evaluation and sandbox test plan.

Reason: CUA Driver is the highest-leverage path toward real computer use, but it must be source-verified and sandbox-designed before any install or runtime wiring.
