# Claude Code Skills Policy

Milestone: N+6.4A
Date: 2026-05-31

This policy governs how Claude Code uses "skills" when acting as Ghoti's
implementation specialist. It keeps skill usage safe, inspectable, and minimal.

## Principles

1. Inspect before use. Any skill — local or external — is read and understood
   before it influences a change. External skills are treated as guidance, not
   as trusted executable automation.
2. No runtime wiring. Skills are not connected into an automatic execution loop.
   A skill does not gain permission to run shell commands, install packages, or
   take live actions just because it was consulted.
3. Minimal and surgical. Implementation follows the Karpathy guidelines intake
   (`14_context/skills/karpathy_guidelines_intake.md`): think first, simplest
   change, touch only what the task requires, define a verifiable success check.
4. One task per branch. Claude Code implements a single assigned task on a
   feature branch in an isolated worktree.
5. Approval gates stay intact. Risky or outbound actions, and all merges, need
   human approval. Skills cannot weaken or bypass an approval gate.

## Allowed skill effects

- Provide a checklist, playbook, or guideline that shapes how code is written.
- Provide a documented prompt/recipe that a human or coordinator can run.

## Forbidden skill effects

- Installing third-party/executable repositories without inspection and
  explicit human approval.
- Reading or writing secrets, `.env` files, tokens, cookies, or browser
  sessions.
- Enabling Telegram, browser automation, or computer-use.
- Launching other agents automatically or performing live account/API/posting
  actions.

## Logging

When Claude Code consults or registers a skill, it is recorded in
`14_context/skills/claude_code_skill_install_log.md` with its enablement status
(guidance-only vs. runtime-wired). Today, all entries are guidance-only.
