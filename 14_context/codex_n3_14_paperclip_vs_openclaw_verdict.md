# Codex N+3.14 Paperclip vs OpenClaw Verdict

Status: codex_parallel_audit / decision_support_only / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Short Verdict

Ghoti should evaluate Paperclip as a future control plane, not replace Ghoti with it and not replace OpenClaw outright. Paperclip and OpenClaw solve different problems:

- Paperclip is closer to a company/task/org/budget/governance control plane.
- OpenClaw is closer to a personal/channel assistant or worker-agent runtime.
- Ghoti should remain the local approval-gated operator core.
- Gemma/Ollama should handle easy local work.
- Claude Code/Codex should handle hard implementation and audit work.
- n8n can later provide deterministic workflow rails.

Recommended next install: none yet. Recommended next implementation: local Gemma router preview + worker-card registry inside Ghoti.

## Paperclip

Paperclip appears useful for:

- Control plane / company metaphor.
- Org chart and role assignment.
- Goals, budgets, and cost visibility.
- Many agents and many Claude/Codex workers.
- Heartbeat-based agent runs.
- Session persistence and task checkout.
- Governance and approvals.
- Adapter model for Claude local, Codex local, OpenClaw gateway, Gemini local, OpenCode local, and HTTP/process-style agents.

Paperclip is likely good for Ghoti's coordination layer later. It is not the low-level desktop executor. It should not be given broad filesystem, credential, Docker, CUA, or live account access until sandboxing and approval gates are proven.

## OpenClaw

OpenClaw appears useful as:

- A personal assistant / channel-based worker.
- A future chat/mobile/personal-agent interface.
- A possible worker under Paperclip or Ghoti supervision.
- A source of skill/channel integration ideas.

OpenClaw is higher operational risk if exposed or over-permissioned:

- Channel integrations can touch messages and accounts.
- Skills may create broad tool access.
- Public exposure increases security risk.
- Live account credentials must not be added until sandbox and TOS boundaries are reviewed.

OpenClaw should not be the main Ghoti control plane yet. It can become a worker candidate later.

## Claude Code / Codex Tabs

Parallel Claude Code and Codex sessions are useful but dangerous if unmanaged. Each worker should have a card:

- Worker ID.
- Tool/model.
- Task.
- Allowed files.
- Forbidden files.
- Expected output.
- Status.
- Handoff file.
- Commit hash.

Without worker cards, multiple tabs become hidden state and accidental conflict risk. Paperclip's value is precisely that it may organize those workers, but Ghoti can implement a lightweight worker-card registry first without installing Paperclip.

## Gemma / Ollama

Gemma should handle:

- Easy local summaries.
- Small checklist drafts.
- Queue classification.
- Compact memory notes.
- Small local markdown rewrites.
- Cheap first-pass task proposals.

Gemma should not handle:

- Multi-file runtime edits.
- CUA/browser execution.
- Live accounts.
- Money, legal, tax, outreach, posting, or trades.
- Git pushes.
- Installs or Docker/model/image pulls.
- Security-sensitive code changes.

N+3.13/N+3.14 local truth says `gemma3:4b` is present and smoke passed in the Claude lane. That makes Gemma valuable for API-free easy work, but it still does not make Gemma an autonomous operator.

## n8n

n8n is a deterministic workflow engine. It should handle repeatable workflow rails after approvals:

- scheduled health checks
- local file watchers
- local webhook intake
- notifications
- daily summary triggers
- stable "if this, then that" steps

n8n should not replace agent reasoning. It should not send emails, post content, scrape, trade, buy, file legal/tax forms, or use credentials without explicit approval and audited workflow design.

## Required Verdicts

| Question | Verdict |
| --- | --- |
| Should Ghoti use Paperclip? | Yes, evaluate seriously as a future control plane. |
| Should Ghoti replace OpenClaw with Paperclip? | No. Paperclip and OpenClaw are complementary. |
| Should Paperclip coordinate OpenClaw later? | Possibly, after sandboxed local proof and strict credentials review. |
| What should be installed next? | Nothing from Paperclip/OpenClaw/n8n yet. |
| What should not be installed yet? | Paperclip runtime, OpenClaw runtime, n8n runtime, public deploys, live account adapters. |
| What should be built next inside Ghoti? | Preview-only local brain router policy + worker-card registry. |

## Final Recommendation

Use Paperclip as the north-star orchestration reference. Build a tiny Ghoti-native worker-card registry first. Then test whether Paperclip can import or mirror that registry later. This keeps progress fast without handing a large new system control over the machine.
