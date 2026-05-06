# Codex N+3.52 - Next Sequence Lock

## Current Status

- Main is `e7e946a` unless the operator has merged after this audit.
- N+3.50A exists locally at `56cf614` but was not remote-pushed during audit.
- N+3.50A is safe enough to preserve but not strong enough to merge as the final 90-percent bridge layer.

## Next Claude Recommendation

`N+3.51A - Safe Write Fallback + Ruflo Isolated Install + Gemma Draft Compression + Course Helper + Prompt Bus Apply Hardening`

Start from the local N+3.50A branch after pushing it for preservation.

Primary fixes:

1. Add explicit Ruflo install confirmation.
2. Fix or document npm path truth.
3. Add Gemma no-model fallback and draft output path.
4. Harden prompt bus context-pack overwrite behavior.
5. Make dashboard bridge truth explicit.
6. Add course/certificate helper or complete local templates.
7. Keep all live/public/account/money actions forbidden.

## Next Codex Recommendation

After Claude N+3.51A is pushed:

`N+3.52B - Audit N+3.51A Bridge Hardening And Merge Readiness`

Codex should validate Ruflo confirmation, Gemma draft writes, prompt bus safeguards, dashboard truth, course/certificate safety, and no live/account/tool execution.

## Operator Priority Commands

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
git switch feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma
git push origin feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma
```

Then harden before merge. Codex does not recommend direct merge yet.

## Do Not Do Next

- Do not run Ruflo swarms.
- Do not run global npm installs.
- Do not launch MCP/browser/operator tools.
- Do not connect accounts.
- Do not automate emails, posts, payments, scraping, jobs, giveaways, certificates, or live actions.
- Do not claim CC/Codex is automatic.
- Do not claim Gemma saves tokens until draft compression succeeds locally.

## Future Milestone After Hardening

`N+3.53 - First Safe Local Worker Pilot And Merge Assistant`

Candidate scope:

- deterministic Python worker on local prompt bus artifacts
- merge-readiness summary from Git and lane files
- dashboard read card for merge status
- all outputs local and draft-only
