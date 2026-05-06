# Codex N+3.55 - Dashboard, Prompt Bus, And Obsidian Audit

## Verdict

AUDIT STATUS: PENDING TARGET BRANCH

Dashboard, prompt bus, and Obsidian N+3.51 updates cannot be audited because the target branch is not pushed.

## Dashboard Requirements

Once the branch exists, Codex must verify:

- Dashboard routes are read-only.
- API routes do not install Ruflo, compress with Gemma, write prompt files, open Obsidian, or trigger apply modes.
- API routes do not read secrets or `.env`.
- UI syntax passes `node --check`.
- The card truthfully states what is manual versus automatic.
- The card accurately reports Ruflo, Gemma, Obsidian, prompt bus, and lane status.

## Prompt Bus Requirements

- `--status-json` works.
- `--write-context-pack --dry-run` writes nothing.
- Dirty state is included.
- Context packs include useful branch, memory, next-actions, and safety context.
- Canonical overwrite is protected by explicit flag or confirmation.
- Safe write fallback exists if Windows blocks writes.
- No clipboard, auto-send, API calls, browser automation, email, posting, payment, scraping, or account action.

## Obsidian Requirements

- Vault exists and required vault files exist.
- App executable or winget proof is reported honestly.
- Helper provides direct executable and `obsidian://open` URI guidance.
- No false claim that the GUI opened unless actually verified.
- No account/sync action is performed.

## Required Commands Once Target Exists

```powershell
python 03_scripts/prompt_bus.py --status-json
python 03_scripts/prompt_bus.py --write-context-pack --target all --title n3-51-audit --include-status --include-memory --include-next-actions --dry-run
python 03_scripts/ghoti_dashboard.py --status
python 03_scripts/ghoti_dashboard.py --json
python 03_scripts/ghoti_dashboard.py --card --dry-run
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
powershell -ExecutionPolicy Bypass -File 03_scripts/open_obsidian_vault.ps1 -Check
```

## Direct Answer

Is Obsidian accessible? Not proven by N+3.51. Prior scaffolding exists, but app visibility/open behavior must be verified on the actual branch.
