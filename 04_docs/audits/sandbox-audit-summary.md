# Sandbox Audit Summary

Last updated: 2026-04-05

## Scope

This audit covers the current `ai_sandbox` account only.

- Read-only inspection plus workspace folder/doc creation under `AI_Managed_Only`
- No source-profile access into `C:\Users\Navif`
- No big installs
- No registry edits
- No PATH cleanup

## High-level state

This sandbox account is usable but thin. The machine is not broken. The sandbox profile is missing or has broken parts of a normal dev setup.

## Windows and shell state

- Theme is dark.
- Transparency is enabled.
- Explorer still hides file extensions.
- Explorer still hides hidden files and protected files.
- Taskbar pins visible from file state: File Explorer, Microsoft Edge, Notion.
- PowerShell 5.1 is present.
- No `pwsh` detected.
- No user PowerShell profile was found for this account.

## Browsers

- Edge is installed and is the default browser.
- Edge has one active local profile under `AppData\Local\Microsoft\Edge\User Data\Default`.
- Chrome is installed but appears lightly initialized.
- No active Firefox or Brave profile was found.
- Browser imports were not attempted.

## IDE state

- VS Code is installed for `ai_sandbox`.
- VS Code user settings folder is not present yet.
- No user-installed VS Code extensions were found.
- Cursor is not installed for `ai_sandbox`.
- A stale `cursor.cmd` resolves to `C:\Users\Navif\...` through machine PATH residue.

## Git state

- Git and Git LFS are installed and usable.
- No user `.gitconfig` was found in `C:\Users\ai_sandbox`.
- No GitHub CLI auth state was found.
- No `.ssh` folder was found.

## Workspace roots

Current roots visible from this account:

- Canonical permanent root: `C:\Users\ai_sandbox\Documents\AI_Managed_Only`
- Temporary-only extra root: `C:\Users\ai_sandbox\AI_Workspace`

Current visible git repo:

- `C:\Users\ai_sandbox\AI_Workspace\21_repos\core\claw-code`

## Automation readiness

Present:

- `schtasks`
- PowerShell
- Codex desktop app

Missing or not ready:

- `gh`
- `uv`
- `pwsh`
- local model runtime
- background automation policy/docs before execution

## AI and local-model readiness

Present:

- strong hardware baseline
- Node
- Git

Missing:

- Python command path
- Ollama
- llama.cpp
- Docker
- WSL2
- benchmark harnesses in the workspace

## GitHub readiness

Not ready yet:

- no `gh`
- no auth
- no repo structure under the base workspace
- no private repo plan implemented yet

## Notion readiness

Important: real Notion integration is not verified.

What is verified:

- Notion desktop app is installed.
- Local Notion app state exists.

What is not verified:

- Notion MCP search
- Notion page read
- Notion page write
- Codex-side Notion sync

## Source-profile reality

`C:\Users\Navif` exists, but direct inspection is blocked from this sandbox account. That is expected based on your correction. No attempt was made to bypass that boundary.

## Most important current blockers

1. Python appears installed at the machine level but is not callable as `python`, `py`, or `pip`.
2. VS Code is installed, but the `code` command is not registered in the current shell.
3. Cursor is not installed for this account, but stale machine PATH entries still point to the other account.
4. The permanent root is now fixed as `AI_Managed_Only`, but one temporary repo still exists under `AI_Workspace`.
5. Real GitHub and Notion integration are not connected yet.
