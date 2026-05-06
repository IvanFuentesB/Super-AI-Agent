# Codex N+3.56 - Next Sequence Lock

## Recommendation

CONDITIONAL PASS.

The operator may merge N+3.51 if they accept that Ruflo/Gemma remain gated and that small polish fixes should follow immediately. If the operator wants a cleaner capability story before merge, ask Claude for N+3.56-FIX first.

## Exact Next Operator Commands If Merging Now

```powershell
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git fetch origin
git merge --no-ff origin/feat/ghoti-agent-claude-n3-51-ruflo-gemma-bridge-hardening -m "merge(ghoti): land N+3.51 bridge Ruflo Gemma hardening"
```

Then run the validation commands listed in `codex_n3_56_merge_plan.md` and push only if they pass or fail only in the documented conditional ways.

## Exact Next Claude Recommendation

If fixing before merge:

```text
N+3.56-FIX - Small bridge hardening fixes before merge
```

Files likely touched:

- `03_scripts/course_certificate_assistant.py`
- `03_scripts/cc_codex_bridge.py`
- `03_scripts/open_obsidian_vault.ps1`
- `03_scripts/ghoti_dashboard.py`
- `03_scripts/local_worker_router.py`
- related docs only

Do not touch live accounts, secrets, Ruflo runtime, browser automation, email, posting, payments, scraping, job applications, fake certificates, or assessment workflows.

## Exact Next Codex Recommendation

After merge or fix branch, Codex should run a smaller re-audit focused on:

- `--goal` course CLI behavior.
- Bridge directory verify behavior.
- Obsidian detection consistency.
- Ruflo missing-repo wording.
- Router bridge-handoff route.
- Post-merge validation from main.

## Future Pilot

After merge/fix, run a controlled local pilot:

1. Generate a Claude/Codex/ChatGPT prompt pair with `cc_codex_bridge.py`.
2. Generate a prompt-bus context pack.
3. Run Gemma status and, only after model install, one draft compression.
4. Run Ruflo gate status and only then consider isolated `npm ci --ignore-scripts`.
5. Verify dashboard local-orchestrator card in a browser.
