# Operator Checklist — N+4.5A Seed: Parallel Agent Relay Seed Pair

## Pre-Launch
- [ ] Review 01_claude_code_prompt.md before pasting into Claude Code
- [ ] Review 02_codex_audit_prompt.md before pasting into Codex
- [ ] Confirm implementation branch: feat/ghoti-agent-claude-n4-5a-parallel-agent-relay-command-center
- [ ] Confirm audit branch: audit/ghoti-agent-codex-n4-5a-parallel-agent-relay-command-center-real-audit-3
- [ ] Confirm Codex effort: extra-high
- [ ] Confirm no live actions will be triggered

## Claude Code Lane
- [ ] Open a fresh Claude Code session
- [ ] Paste 01_claude_code_prompt.md
- [ ] Monitor until IMPLEMENTED_AND_PUSHED or confirmed blocker
- [ ] Record commit hash returned by Claude Code

## Codex Lane (run in parallel with Claude lane)
- [ ] Open a fresh Codex session
- [ ] Paste 02_codex_audit_prompt.md
- [ ] Codex will poll (git ls-remote) and wait for Claude to push
- [ ] Monitor until CLEAN PASS or BLOCKED

## Post-Audit Review
- [ ] Review Claude Code implementation commit on GitHub
- [ ] Review Codex audit report in audit/ghoti-agent-codex-n4-5a-parallel-agent-relay-command-center-real-audit-3
- [ ] Both CLEAN PASS? Approve main merge gate
- [ ] Either BLOCKED? Investigate root cause, fix, re-run

## Safety Gates (must hold)
- [ ] No live account actions taken by either agent
- [ ] No external repos cloned, installed, or run
- [ ] No secrets committed to any branch
- [ ] Human approval confirmed for all pushes
- [ ] Main merge approved only after human review
