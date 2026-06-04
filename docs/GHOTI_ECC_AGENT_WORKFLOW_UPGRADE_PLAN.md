# Ghoti ECC-Inspired Agent Workflow Upgrade Plan

ECC ("everything-claude-code") is an external Claude Code framework of agent roles,
skills, slash commands, lifecycle hooks, a security scanner, and token-optimization
ideas. **Ghoti does not install ECC.** This plan adapts only inspected ideas, keeping
Ghoti's supervised, local-first posture.

## Hard boundary

- Do **not** install the full ECC plugin into Ghoti.
- Do **not** enable ECC hooks.
- Do **not** run ECC Node scripts.
- Do **not** stack a plugin install on top of a manual install.
- Adapt **inspected patterns only**, re-expressed in Ghoti's own scripts.

## What we adopt (re-expressed, not installed)

1. **Agent roles** - keep one-agent-per-task with explicit narrow roles (implementer,
   auditor/merge-gate, status/handoff). This already matches Ghoti lanes; document the
   roles in `AGENTS.md`.
2. **Skill layout** - a predictable folder shape for project skills/commands so Codex
   and Claude find the right playbook quickly.
3. **Command templates** - reusable prompt-packet templates (see the N+6.19A prompt
   packet builder) for common tasks: implement, audit, merge-gate, status.
4. **Hooks as validators only** - adopt the *idea* of lifecycle hooks but implement
   them as **read-only validators** we run on demand (for example
   `public_repo_security_audit.py`, `git diff --check`, the test suite). No hook ever
   executes third-party code automatically.
5. **Security-scanner ideas** - extend the existing repo security audit with more
   read-only checks (secret shapes, risky subprocess patterns) rather than adopting an
   executable scanner.
6. **Token-optimization ideas** - compact status/handoff files over long chats,
   summarized context packs, and short auto-loaded `AGENTS.md` (see the GBrain plan).

## What we explicitly reject

- Automatic execution of any hook or Node script.
- Any agent launching another agent without operator approval.
- Any plugin that adds outbound network calls, account access, or live control.

## Rollout (behind flags, off by default)

- `ecc_agent_workflow_upgrade_enabled` gates any workflow change.
- Phase 1: document roles + skill layout (this milestone).
- Phase 2: add validator-style checks to the existing audit (separate milestone).
- Phase 3: prompt-packet command templates wired into the overnight operator queue.

No phase enables live hooks or runs external Node scripts.
