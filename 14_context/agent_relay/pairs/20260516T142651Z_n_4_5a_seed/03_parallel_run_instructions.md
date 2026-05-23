# Parallel Run Instructions — N+4.5A Seed: Parallel Agent Relay Seed Pair

## Overview
Run Claude Code and Codex in parallel using the generated prompt packets.
Claude implements while Codex polls and waits. Both run simultaneously.

## Step 1 — Open Claude Code
Copy and paste the contents of:
  01_claude_code_prompt.md

Claude Code will:
- Use /ultraplan for deep planning (maximum effort)
- Use /goal for long-horizon execution (Sonnet 4.6 high)
- Implement all deliverables on feat/ghoti-agent-claude-n4-5a-parallel-agent-relay-command-center
- Run validations, write report, commit, and push

## Step 2 — Open Codex (run in parallel with Step 1)
Copy and paste the contents of:
  02_codex_audit_prompt.md

Codex will:
- Poll for the implementation branch (git ls-remote, every ~50s, up to 60 attempts)
- Wait until Claude pushes the branch
- Audit all deliverables once the branch appears
- Push audit report to audit/ghoti-agent-codex-n4-5a-parallel-agent-relay-command-center-real-audit-3 (or fresh -3 if -2 exists — never force-push)

## Step 3 — Human Review and Approval
- Review Claude Code's implementation commit
- Review Codex's audit report
- Approve main merge ONLY if both show CLEAN PASS / IMPLEMENTED_AND_PUSHED
- If either is BLOCKED: investigate root cause before proceeding

## Safety
- No button or automated trigger starts Claude Code or Codex.
- Human must manually paste each prompt.
- Human must review all output before any main merge.
- Approval gates are intact at every step.

## Codex effort: extra-high
## Claude planning: /ultraplan max
## Claude execution: /goal Sonnet high
