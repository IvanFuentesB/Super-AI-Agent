# N+3.39 Free-Claude, Mythos, And Unrestricted Safety Register

Status: Codex safety register only.
Date: 2026-05-05

This register preserves risky user-requested ideas without approving their runtime use.

## Hard Rule

Ghoti must not install, run, clone into runtime, depend on, or wire these tools without explicit security review and legal approval.

If the user says "pull and use" a free Claude, Mythos, leaked, or unrestricted repo, the safe interpretation is:

1. Stop.
2. Ask for explicit quarantine/security-audit approval.
3. If approved, use an isolated research folder only.
4. Scan/read only.
5. Do not execute.
6. Do not connect accounts.
7. Do not use it to bypass subscriptions, rate limits, usage caps, auth, captchas, or platform rules.

## Register

| Item | Why risky | Allowed safe use | Runtime use verdict |
| --- | --- | --- | --- |
| free-claude-code/unlocked Claude Code repos | May proxy official tools, bypass account limits, contain malware, leak credentials, or violate terms | Source-check only; malware/supply-chain audit only after approval | Reject for runtime |
| leaked Claude Code code | Unauthorized or private code provenance, legal risk, malware copies, tainted architecture | No clone/copy/use; at most high-level public reporting notes | Forbidden |
| Mythos repo/model claims | User has referenced Mythos/leaked/unsafe concepts; provenance and claims are not trusted | Audit-only safety/verification pattern extraction if legal/public | Reject for runtime |
| Open Generative AI free-claude-code repo claims | Likely overlaps with bypass/proxy claims and unclear provenance | Source-check only; do not run | Reject for runtime |
| OBLITERATUS | Guardrail-removal and unrestricted-tooling risk | Research-only risk notes | Reject for Ghoti runtime |
| Unrestricted LLM lane | Can drift into law/safety/platform bypass if not constrained | Legitimate local research and summarization only; no bypass use | Evaluation-only |
| Claude Code Harness repos with hooks | Hooks may run on tool calls and execute shell, modify permissions, or alter workflow | Read docs/source only until isolated audit | Research-only |
| Hermes auth patches or Claude subscription bypass patches | Explicit cat-and-mouse auth evasion risk | Do not use; record as unsafe pattern | Reject |

## Safe Inspiration Boundary

Allowed:

- architecture inspiration from legal/public docs
- guardrail ideas
- verification loops
- task-budget ideas
- audit-log ideas
- file hash truth ideas
- permission boundary ideas

Not allowed:

- copying leaked code
- executing unknown scripts
- proxying official subscriptions through bypass layers
- using cracked/unlocked clients
- importing unreviewed hooks
- running unrestricted agents with live tools
- connecting payment, email, browser, scraping, or account tools

## Future Review Conditions

A risky repo can only move from `reject` to `sandbox research` if:

- exact source and license are verified
- no leaked/stolen/private code is involved
- malware/supply-chain scan plan exists
- no live credentials are present
- no runtime wiring is proposed
- operator gives explicit approval

Moving from `sandbox research` to `runtime candidate` requires a separate milestone, read-only default, lock files, and a human approval gate.
