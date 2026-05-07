# Claude Code Prompt Template

**Usage:** Copy this template structure when writing a new Claude Code milestone prompt.
**Canonical path:** `14_context/ghoti_current_prompt.md`

---

## Template

```markdown
You are Claude Code working in:

C:\Users\ai_sandbox\Documents\AI_Managed_Only

Base branch:
feat/ghoti-visible-operator-stack

Repo:
IvanFuentesB/Super-AI-Agent

Recommended Claude Code settings:
- model: sonnet
- effort: high
- permission mode: bypassPermissions

Milestone:
{{MILESTONE_ID}} — {{MILESTONE_TITLE}}

CURRENT TRUTH:
The repo is now at or after:
{{COMMIT_HASH}} {{COMMIT_MESSAGE}}

HARD SAFETY RULES:
- Do not run uncontrolled parallel agents.
- Do not connect live accounts.
- Do not send emails.
- Do not post, sell, pay, scrape, apply to jobs, enter giveaways, or touch live accounts.

THIS CLAUDE LANE:
{{LANE_DESCRIPTION}}

Claude lane branch:
{{LANE_BRANCH}}

Allowed Claude lane paths:
{{ALLOWED_PATHS}}

Forbidden Claude lane paths:
{{FORBIDDEN_PATHS}}

FIRST INSPECT AND SYNC:
Run:
git status --short
git branch --show-current
git fetch origin
git log --oneline --graph --decorate --all -20

{{TASK_INSTRUCTIONS}}

VALIDATION
{{VALIDATION_COMMANDS}}

FINAL REPORT:
{{REPORT_FORMAT}}
```
