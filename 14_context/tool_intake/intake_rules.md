# Tool / Repo / Connector Intake Rules

Every new tool, repo, or connector follows these rules before adoption.

1. **Inspect first.** Unknown repos are cloned only into the gitignored sandbox
   and statically inspected via `repo_intake.py`. Never run their install/build
   scripts to "see what happens".
2. **Deny by default.** A connector/template ships `enabled:false`. Dangerous
   capabilities (browser control, account actions, send/post/purchase) stay in
   the blocked list until a separate, explicit safety gate.
3. **No secrets in the repo.** Credentials are env vars set locally; templates
   carry env-var names only.
4. **Official APIs only.** No unofficial/automation-against-TOS integrations
   (e.g. no unofficial WhatsApp automation).
5. **Human owns money + accounts.** No purchases, payments, trading, posting, or
   email sending by an agent.
6. **Reject the abuse list.** Spam/fake engagement, seat-hoarding, false
   reports, payment/account abuse, stealth account automation are never built.
7. **Record the decision.** Each intake gets a report with one of:
   `inspect_more`, `safe_to_adapt`, `risky`, `reject`.
