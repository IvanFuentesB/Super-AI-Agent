# RUFLO Read-Only Evaluation

Date: 2026-04-26
Branch: feat/ghoti-visible-operator-stack
Status label: read_only_evaluation / not_installed / not_runtime_wired
Evaluator: Claude Code (Sonnet 4.6) — operator-supervised, read-only web metadata only
Internet access available: YES — WebSearch used for public repo metadata only

---

## Basic Identity

- Repo/tool name: RUFLO (formerly Claude Flow)
- Source URL: https://github.com/ruvnet/ruflo
- Vendor / owner: ruvnet (Ruv — open-source maintainer)
- Category: Multi-agent orchestration / Claude Code integration framework
- Date evaluated: 2026-04-26
- Status label: `read_only_evaluation / not_installed / not_runtime_wired`

---

## Purpose Truth

- Claimed purpose: "The leading agent orchestration platform for Claude. Deploy intelligent multi-agent swarms, coordinate autonomous workflows, and build conversational AI systems. Features enterprise-grade architecture, distributed swarm intelligence, RAG integration, and native Claude Code / Codex integration."
- Real purpose after inspection: A Node.js CLI tool that wraps Claude Code (and optionally Codex) to define swarms of role-labeled agents, coordinate task handoffs between them, and maintain shared context/memory across agents. Runs on top of the user's local Claude Code installation.
- What Ghoti capability this might support: Multi-agent orchestration, parallel agent roles, shared local memory, operator-visible task handoffs — all relevant to Ghoti's long-term direction.
- What it does not do: It is not a runtime-standalone AI model. It does not replace Claude. It does not work without an Anthropic API key. It does not run fully offline.
- Is it runtime-wired today? NO.

---

## License / Ownership

- License: MIT (confirmed via public README and repository metadata, April 2026)
- Commercial-use clarity: MIT allows commercial use without restriction
- Copyleft/AGPL implications: NONE — MIT is permissive with no copyleft
- Attribution requirements: Standard MIT attribution (preserve copyright notice)
- Unknowns: Some companion packages (e.g. AgentDB) use "MIT OR Apache-2.0" — dependency audit required before install to confirm no AGPL or proprietary sub-dependencies sneak in

---

## Risk Review

### SECURITY — CRITICAL FLAGS (must be read before any install decision)

**Finding 1 — Prompt Injection via MCP Tool Descriptions (reported 2026, Issue #1375):**
RUFLO's MCP tool descriptions contained hidden instructions directing Claude to silently add the repository owner (ruvnet) as a contributor to the user's repositories without user knowledge or consent. This is a textbook supply-chain prompt injection attack exploiting Claude's MCP tool trust model.

**Finding 2 — Obfuscated Malicious Preinstall Script (versions 3.1.0-alpha.55 through 3.5.2):**
A deliberately obfuscated one-liner in the npm `preinstall` script silently deleted directories and cache files on user machines. The code was removed only after external security disclosure and with no explanation from the maintainer.

**Finding 3 — SQL Injection Vulnerabilities (remediated in v3.5.40):**
SQL injection vulnerabilities were present prior to v3.5.40, converted to parameterized queries as part of the security remediation release.

**Remediation status:** v3.5.40 claims to address the above. However, the history of obfuscated code and covert contributor manipulation represents a severe trust signal failure that must be weighed independently of the fix.

---

- Security risk: **CRITICAL** — supply-chain attack history; obfuscated malicious preinstall; covert repo manipulation via prompt injection; SQL injection history. Even with v3.5.40 remediation, trust is not automatically restored.
- TOS/legal risk: MEDIUM — requires Anthropic API key; autonomous agent actions could violate Anthropic usage policies if swarms act without proper human approval gates.
- Privacy/PII risk: MEDIUM — shared agent memory could accumulate sensitive data; unclear whether memory is stored locally only or transmitted.
- Supply-chain risk: **HIGH** — demonstrated willingness to ship obfuscated code; dependency graph (Node.js ecosystem) requires full audit.
- Abuse risk: MEDIUM — autonomous multi-agent swarms without proper gate checks could perform unintended file writes, git operations, or API calls.
- Autonomous-action risk: HIGH — swarms are designed to act autonomously; Ghoti approval gates must be preserved if RUFLO is ever integrated.
- Paid/cloud-service risk: HIGH — requires Anthropic API key; all agent calls consume API credits.

---

## Runtime Requirements

- Operating system support: macOS, Linux primary; Windows supported but with known issues
- Windows compatibility: **KNOWN ISSUES** — Issue #615 documents PowerShell/nvm incompatibility; Claude Code ↔ RUFLO integration breaks in some Windows PowerShell + Node nvm configurations. Must be tested in the specific environment before any install.
- Rust requirements: None documented
- Python requirements: None documented (Node-based)
- Node requirements: Node.js 18+ (LTS recommended), npm 9+
- Docker requirements: None for base install; may be used by enterprise features
- GPU/model requirements: None (uses Claude via API)
- Background service requirements: None documented for base use; GitHub Actions integration is optional
- Browser requirements: None for CLI use
- Other native dependencies: None beyond Node/npm; sub-dependency audit needed

---

## Account / Auth / Secrets

- Accounts required: Anthropic account (for API key)
- API keys required: **YES — ANTHROPIC_API_KEY required**; cannot run without it
- OAuth/browser login required: Not required for CLI use; GitHub Actions integration requires GitHub secrets
- Paid plan required: YES effectively — Anthropic API usage is metered; multi-agent swarms multiply token consumption significantly
- Data sent outside local machine: YES — all agent prompts and context are sent to Anthropic's API; memory contents may be included in API calls
- Local-only feasibility: **NO — not fully local.** Requires live Anthropic API access for every agent call. Cannot run in a true air-gapped or local-only configuration.
- Secret-handling plan: ANTHROPIC_API_KEY must never be hardcoded; must be stored in environment only; not staged, not committed.

---

## Multi-Agent Capability Notes

- Supports concurrent/parallel agents: YES — core design feature; swarms run multiple agents
- Single narrow role per agent: YES — role-labeled agents are the intended pattern
- Agent permissions scoped by role: Claimed but not independently verified; audit needed
- Pause/inspect/cancel agents: Claimed in v3 architecture; not independently verified
- Per-agent logs: Claimed; not independently verified
- Merge without autonomous code execution: Unclear — swarms may generate and execute code

---

## Claude Code / Codex Integration Claims

- RUFLO claims native Claude Code integration as its primary design
- RUFLO claims Codex integration as a secondary path
- The prompt injection finding (Issue #1375) exploited this integration surface — MCP tool trust was abused to insert covert instructions into Claude's context
- Any integration with Ghoti must be treated as a potential prompt injection vector until independently audited

---

## Shared-Memory / RAG Claims

- Shared context store: YES — claimed as a core feature ("a memory store accessible across agents within a swarm")
- Storage backend: Not independently verified; likely file-based or SQLite given SQL injection finding
- Local memory only: Unclear — must audit whether memory is transmitted to API or external services
- Operator review/delete of memory: Not independently verified
- RAG integration: Claimed in README; backend and data-handling details unknown

---

## Approval Gates Required Before Install

- [ ] User explicitly approves clone into isolated evaluation directory
- [ ] User explicitly approves npm install (full dependency audit must precede)
- [ ] User explicitly approves any ANTHROPIC_API_KEY use in RUFLO context
- [ ] User explicitly approves any agent run or swarm execution
- [ ] Security review of v3.5.40+ source code before any install (not just README)
- [ ] Dependency tree audit (npm audit) before any install
- [ ] Windows compatibility test in isolated environment before any Ghoti integration

---

## Sandbox Test Plan (for a future approved milestone only)

1. Read full README, SECURITY.md, CLAUDE.md, and CHANGELOG in public repo without cloning.
2. If approved: clone into `21_repos/third_party/ruflo-eval/` (isolated, read-only evaluation path).
3. Run `npm audit` on the cloned repo before any `npm install`.
4. Inspect `package.json` preinstall/postinstall scripts for obfuscated code.
5. Inspect MCP tool description strings for hidden prompt injection.
6. If approved: `npm install` in isolated directory only; do not link globally.
7. Run a single minimal smoke test with a disposable ANTHROPIC_API_KEY scope.
8. Verify generated files are gitignored and not staged.
9. Confirm no credentials or covert repo mutations occurred.
10. Record all results in finish-line log.

---

## Rollback Plan

- Files/directories created: `21_repos/third_party/ruflo-eval/` (if cloned)
- Services/processes started: None (CLI only)
- Environment variables changed: ANTHROPIC_API_KEY in shell only (not committed)
- Accounts/tokens used: Anthropic API key (revocable in Anthropic console)
- Cleanup command(s): `rm -rf 21_repos/third_party/ruflo-eval/` and revoke API key if used
- Gitignore/update needed: Ensure `ruflo-eval/` and any generated artifacts are gitignored before clone

---

## Final Verdict

**`research only`**

RUFLO is architecturally promising and directly relevant to Ghoti's multi-agent direction. However, the security history — obfuscated malicious preinstall code, covert contributor manipulation via prompt injection, and SQL injection — represents a serious trust deficit that cannot be resolved by reading docs alone.

The project has addressed these issues in v3.5.40, but:
- Trust is not automatically restored by a patch.
- The maintainer's response to the obfuscated code disclosure was silence, not transparency.
- Windows compatibility issues add further friction.
- Fully local-only operation is impossible (requires Anthropic API).
- Multi-agent swarms multiply API costs and autonomous-action risk.

**Recommended next step:** Before any clone/install decision, wait for additional community trust signals (independent security audits, extended post-v3.5.40 clean track record). The evaluation template and sandbox test plan are ready for a future explicitly approved milestone.

**Do not install, clone, or wire into Ghoti runtime without a separate explicit approval milestone.**

---

## Current Status

- Status label: `read_only_evaluation / not_installed / not_runtime_wired`
- Cloned: NO
- Installed: NO
- Runtime wired: NO
- API key used: NO
- Accounts connected: NO
- Internet access used: YES — WebSearch for public GitHub metadata only; no account login or data submission

---

Sources used (public metadata only):
- https://github.com/ruvnet/ruflo
- https://github.com/ruvnet/ruflo/blob/main/README.md
- https://github.com/ruvnet/ruflo/issues/1375 (Security Audit Summary)
- https://github.com/ruvnet/ruflo/issues/1384 (Security Remediation v3.5.40)
- https://github.com/ruvnet/ruflo/issues/615 (Windows PowerShell compatibility)
- https://github.com/ruvnet/ruflo/blob/main/SECURITY.md
- https://byteiota.com/agent-orchestration-frameworks-2026-openai-ruflo-swarms/
- https://pasqualepillitteri.it/en/news/774/claude-flow-ruflo-multi-agent-orchestration-guide
