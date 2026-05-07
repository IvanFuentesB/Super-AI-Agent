# Codex N+3.14 Paperclip Source Audit

Status: codex_parallel_audit / isolated_clone_completed / no_install / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: bb48edd
Origin HEAD at start: 2149424
Local/Origin relationship at start: local ahead 2, behind 0

## Repo Truth

Dirty/local-only files already present before this audit:

- `14_context/ghoti_external_repo_tool_intake.md` modified
- `21_repos/third_party/.gitkeep` modified
- `.claude/skills/` untracked
- `01_projects/mcp_server/test.txt` untracked
- `14_context/ghoti_current_prompt_N1_6.md` untracked
- `14_context/local_gemma_ready_verification_n3_14.md` untracked
- CV `.docx` files untracked
- `output/` untracked

Staged files at start: none.

## Source Candidates

| Candidate | Source | What it appears to be | Fit for this milestone |
| --- | --- | --- | --- |
| `paperclipai/paperclip` | https://github.com/paperclipai/paperclip | Open-source orchestration/control plane for AI agent teams, with org charts, budgets, governance, heartbeats, Claude/Codex/OpenClaw-style adapters, and Node/React UI. | Correct Paperclip candidate. |
| `fredruss/agent-paperclip` | https://github.com/fredruss/agent-paperclip | Desktop companion/pet/monitor for Claude Code and Codex sessions; useful for visibility, not a multi-agent company control plane. | Different product; not the Paperclip orchestration candidate. |
| `agencyenterprise/paperclip-ai` | https://github.com/agencyenterprise/paperclip-ai | Appears to be tutorial/marketing/tutorial material pointing users to `paperclipai/paperclip`. | Reference only. |

Verdict: `paperclipai/paperclip` is the correct source for the Paperclip orchestration/control-plane idea. `fredruss/agent-paperclip` is interesting for desktop status visibility, but it is not a replacement for Paperclip's org/task/budget/governance control plane.

## Public Source Summary

The Paperclip README and official docs describe it as a Node.js server and React UI that coordinates agent teams with org charts, goals, budgets, governance, task checkout, heartbeats, cost tracking, approvals, and adapters for Claude Code, Codex, OpenClaw, shell/CLI agents, and HTTP/webhook agents.

Important source links:

- Paperclip GitHub: https://github.com/paperclipai/paperclip
- Paperclip agent runtime guide: https://paperclip.inc/docs/guides/agent-developer/how-agents-work/
- Paperclip adapter overview: https://paperclip.inc/docs/adapters/overview/
- Agent Paperclip GitHub: https://github.com/fredruss/agent-paperclip
- n8n docs: https://docs.n8n.io/

## Local Clone Truth

| Field | Value |
| --- | --- |
| Clone path | `21_repos/third_party/evals/paperclip` |
| Path existed before run | NO |
| Cloned this run | YES |
| Clone command | `git clone --depth 1 https://github.com/paperclipai/paperclip.git 21_repos/third_party/evals/paperclip` |
| HEAD | `d0bdbe11a9624435b6dca3968389bd59c6a559a2` |
| Remote | `https://github.com/paperclipai/paperclip.git` |
| Third-party files staged | NO |
| Dependencies installed | NO |
| Runtime started | NO |

The clone is intentionally untracked and must not be staged in this milestone.

## Local Source Inspection

Top-level shape:

- `server/`
- `ui/`
- `packages/`
- `cli/`
- `docs/`
- `doc/`
- `docker/`
- `scripts/`
- `.agents/skills/`
- `.claude/skills/`
- `package.json`
- `pnpm-workspace.yaml`
- `pnpm-lock.yaml`
- `Dockerfile`
- `LICENSE`

License:

- MIT License
- Local file: `21_repos/third_party/evals/paperclip/LICENSE`

Stack:

- TypeScript / Node.js
- React UI
- pnpm workspace
- Embedded PostgreSQL in local dev
- Docker options available
- Adapter packages for Claude local, Codex local, Cursor local, Gemini local, OpenCode local, OpenClaw gateway, and plugin/sandbox examples

Requirements from README/package files:

- Node.js 20+
- pnpm 9.15+
- Manual local dev path: `pnpm install` then `pnpm dev`
- One-command path: `npx paperclipai onboard --yes`
- API server default: `http://localhost:3100`

Commands documented but not executed:

- `pnpm install`
- `pnpm dev`
- `pnpm dev:once`
- `pnpm paperclipai run`
- Docker build/run and compose commands

## Agent / Adapter Findings

Paperclip appears to coordinate agents rather than act as a low-level executor. Local docs describe heartbeat-based execution:

- wakeup trigger
- adapter invocation
- local CLI or HTTP agent process
- status/log/cost/session capture
- UI updates and run records

Adapters observed locally:

- `@paperclipai/adapter-claude-local`
- `@paperclipai/adapter-codex-local`
- `@paperclipai/adapter-openclaw-gateway`
- `@paperclipai/adapter-cursor-local`
- `@paperclipai/adapter-gemini-local`
- `@paperclipai/adapter-opencode-local`
- `process` / shell-style path in docs
- HTTP/webhook-style agent path in docs

This strongly fits Ghoti's long-term desire for many Claude Code/Codex/Gemma/OpenClaw-style workers, but it also increases risk because local CLI adapters can run unsandboxed host processes if configured too broadly.

## Agent Paperclip Contrast

`fredruss/agent-paperclip` is a desktop companion for Claude Code/Codex visibility:

- Node.js 18+
- npm install path
- hooks into Claude Code status and watches Codex sessions
- desktop pet/window that shows activity/status/context use
- not an org-chart/budget/governance/task-control plane

It may be useful later as operator visibility inspiration, but it should not be confused with `paperclipai/paperclip`.

## Security Risks

- Local CLI adapters can execute with host privileges unless isolated.
- Paperclip can manage multiple agents, so a bad config could multiply mistakes quickly.
- Budget controls are useful but are not a provider cap-bypass mechanism.
- Secrets/env vars must be tightly scoped.
- Telemetry is enabled by default per README; disable for local privacy review before any serious use.
- OpenClaw gateway integration must not receive broad credentials or live account access.
- Docker paths require image/source review and bounded volumes.
- Agent heartbeats can create unattended loops if not configured conservatively.

## Local-First Fit

Paperclip is a strong local-first candidate because local dev can run with embedded PostgreSQL and local storage, and the README says no Paperclip account is required for self-hosted quickstart. It is still too large to install blindly inside Ghoti.

## Should It Be Cloned?

YES for isolated evaluation. Completed in this milestone.

## Should It Be Installed Now?

NO. Installation should be a separate approval-gated milestone after this audit. First install should use a separate sandbox/worktree or explicit local eval directory, not the Ghoti runtime. No Paperclip server should be exposed publicly.

## Verdict

Paperclip is currently the strongest candidate for Ghoti's future multi-agent control plane. It should not replace Ghoti runtime, approval gates, ActionIntent, CUA, or local Gemma routing. It should be evaluated as a coordination layer that may manage many workers later, while Ghoti keeps the safety/audit/operator boundary.
