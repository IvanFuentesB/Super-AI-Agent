# Obsidian Install and Vault Link — N+3.45A

**Milestone:** N+3.45A
**Date:** 2026-05-05
**Branch:** feat/ghoti-agent-claude-n3-45-tooling-prompt-bus

---

## Install Status

**INSTALLED** — Obsidian 1.12.7 via winget

### Command Output Summary

```
winget --version
v1.28.240

winget install --id Obsidian.Obsidian --exact --accept-package-agreements --accept-source-agreements
Found Obsidian [Obsidian.Obsidian] Version 1.12.7
Downloading https://github.com/obsidianmd/obsidian-releases/releases/download/v1.12.7/Obsidian-1.12.7.exe
Installer hash verified
Starting package installation...
Successfully installed

winget list --id Obsidian.Obsidian --exact
Name     Id                Version Source
------------------------------------------
Obsidian Obsidian.Obsidian 1.12.7  winget
```

---

## Vault Path

```
C:\Users\ai_sandbox\Documents\AI_Managed_Only\14_context\obsidian_vault
```

Contents: 10+ markdown files created in N+3.7 and N+3.34.
Key files: `00_Index.md`, `01_Current_State.md`, `06_Safety_Gates.md`, `07_Agent_Routing.md`, `09_Migration_Handoff.md`.

## Compact Memory Path

```
C:\Users\ai_sandbox\Documents\AI_Managed_Only\14_context\compact_memory
```

Contents: 6+ compact pointer files: `project_state.md`, `agent_routing_memory.md`, `safety_rules.md`, etc.

---

## How to Open Vault in Obsidian

1. Launch Obsidian from Start Menu or Desktop.
2. Click **Open folder as vault**.
3. Navigate to `C:\Users\ai_sandbox\Documents\AI_Managed_Only\14_context\obsidian_vault`.
4. Click **Open**.

The vault will load all `.md` files as linked notes. `[[wikilinks]]` connect notes automatically.

**No cloud sync or Obsidian account required.** The vault is entirely local.

---

## No Cloud Sync / No Account Required

- Do NOT connect Obsidian Sync.
- Do NOT install plugins.
- Do NOT log in to an Obsidian account.
- The vault is a folder of plain `.md` files — readable and editable by any text editor.

---

## Token-Saving Role

The vault serves as a persistent context layer between Claude/Codex/ChatGPT sessions:

- Instead of re-pasting full state docs, reference a vault note + file path.
- `00_Index.md` is the navigation hub.
- `09_Migration_Handoff.md` is the session handoff note — paste its path as context primer.
- `14_context/compact_memory/` holds 300-700 word compressed pointers for each domain.

Pattern:
```
Read 14_context/obsidian_vault/09_Migration_Handoff.md and 14_context/compact_memory/project_state.md for current context.
```

This replaces pasting 3000+ words of state docs into every new session.

---

## What Is NOT Wired

- No Obsidian plugins installed.
- No Obsidian Sync/account connected.
- No vault files were moved or renamed.
- No automated vault write from Claude Code.
- Vault files are read/write by the user manually or by Claude Code via explicit Write tool calls.

---

## Next Safe Steps

1. Open the vault in Obsidian manually to verify note links.
2. Add `09_Migration_Handoff.md` to your prompt templates as a context primer.
3. Future: automate vault note updates via `03_scripts/prompt_bus.py` when vault write is explicitly approved.
