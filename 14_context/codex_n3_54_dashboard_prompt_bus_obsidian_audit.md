# Codex N+3.54 - Dashboard, Prompt Bus, And Obsidian Audit

## Verdict

AUDIT STATUS: PENDING TARGET BRANCH

The N+3.51 dashboard, prompt bus, and Obsidian hardening cannot be audited because the real Claude N+3.51 branch is missing from the remote.

## Dashboard Audit Checklist

When the branch is available, verify:

- `GET /api/ghoti/local-orchestrator/status` exists if changed.
- Any new dashboard route is read-only.
- Routes do not install Ruflo, call Gemma compression, open Obsidian, launch browser tools, or mutate repo state.
- Routes do not read secrets, `.env`, tokens, cookies, credentials, SSH keys, or API keys.
- The UI renders without JavaScript syntax errors.
- The UI honestly distinguishes manual bridge steps from automatic automation.
- The dashboard exposes accurate Ruflo, Gemma, Obsidian, prompt bus, and lane status.

Required commands:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
python 03_scripts/ghoti_dashboard.py --status
python 03_scripts/ghoti_dashboard.py --json
python 03_scripts/ghoti_dashboard.py --card --dry-run
```

## Prompt Bus Audit Checklist

When the branch is available, verify:

- `python 03_scripts/prompt_bus.py --status-json` works.
- `--write-context-pack --dry-run` writes nothing.
- Context packs include branch/HEAD, dirty state, lane status, memory pointers, next actions, and safety warnings.
- Apply mode writes only intended local prompt files.
- Canonical prompt overwrites require explicit confirmation or force.
- No clipboard, auto-send, browser automation, external API, account action, email, social posting, or payment action exists.

Required command:

```powershell
python 03_scripts/prompt_bus.py --write-context-pack --target all --title n3-51-audit --include-status --include-memory --include-next-actions --dry-run
```

## Obsidian Audit Checklist

When the branch is available, verify:

- `14_context/obsidian_vault/` exists.
- Required vault files exist.
- Obsidian installation is proven by executable path, winget, or documented absence.
- The helper does not falsely claim that the GUI opened unless verified.
- The helper provides an `obsidian://open?vault=...` fallback or direct executable fallback.
- It remains local-only and performs no account or sync action.

Required command:

```powershell
powershell -ExecutionPolicy Bypass -File 03_scripts/open_obsidian_vault.ps1 -Check
```

## Current Verdict

Dashboard, prompt bus, and Obsidian are partially present in earlier milestones, but N+3.51 improvements cannot be credited until a pushed branch exists and passes the audit checklist.
