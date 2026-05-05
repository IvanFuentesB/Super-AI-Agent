# Agent Lane Merge Checklist

Use this before merging any agent lane branch.

1. Fetch first: `git fetch origin`.
2. Compare local HEAD and origin for the lane branch.
3. Inspect `14_context/agent_lanes/active_locks.jsonl`.
4. Confirm no shared-file overlap with another active lane.
5. Inspect staged files: `git diff --cached --name-only`.
6. Confirm only intentional files are staged.
7. Run validation for touched files.
8. Confirm generated logs are not staged unless explicitly approved.
9. Confirm no secrets, API keys, credentials, or tokens are staged.
10. Commit on the lane branch.
11. Push the lane branch.
12. Merge one branch at a time.
13. Update state docs only from the designated state-owner lane.
14. Never run `git reset` or destructive cleanup without explicit human approval.
15. Confirm no public/live side effects happened: no posting, email, payment, scraping, account creation, job application, giveaway entry, or product listing.

## Stop And Ask If

- Branches diverged.
- Another active lane locks the same shared file.
- Runtime files and dashboard files are both touched unexpectedly.
- A generated artifact contains secrets or live-account instructions.
- A task requires public, money-facing, account, connector, browser, or scraping actions.
