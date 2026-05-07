# Codex Obsidian Token-Saving Audit - N+3.3

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Observed HEAD: bd6a76f
Status label: local_markdown_vault / token_saving / not_runtime_wired

## Goal

Use a plain markdown vault to reduce prompt size, preserve compact project context, and make Ghoti easier for ChatGPT, Claude, Codex, and future local tools to read without re-ingesting giant logs.

This is legal context management only. It is not provider cap bypass, quota evasion, or hidden automation.

## Proposed Vault Path

`14_context/obsidian_vault/`

This path should remain plain markdown. No Obsidian plugin install is required for the first pass.

## Recommended Notes

| Note | Purpose |
|---|---|
| `00_Index.md` | Entry point with links to all notes |
| `01_Current_State.md` | 200-400 word compact state |
| `02_Next_Actions.md` | highest-priority next actions and blockers |
| `03_Agents.md` | role map for ChatGPT, Codex, Claude, Claude Code, Gemma |
| `04_Tools.md` | CUA, AutoBrowser, Screenpipe, Obsidian, Ollama, etc. |
| `05_Safety_Gates.md` | non-negotiable approval and forbidden-action rules |
| `06_Prompts.md` | prompt-file and handoff conventions |
| `07_Runbooks.md` | repeatable local commands and validation flows |
| `08_Decisions.md` | compact decision log with dates and links |

## Note Rules

- 200-400 words per note.
- One concept per note.
- Link to source files instead of pasting long logs.
- Do not paste terminal transcripts.
- Do not paste secrets, credentials, or private account data.
- Use tags such as `#ghoti`, `#runtime`, `#safety`, `#tool-intake`, `#computer-use`, `#token-saving`.
- Update after each milestone.
- Prefer stable file paths and commit hashes over narrative memory.
- Keep old detailed logs in their existing files; vault notes should point to them.

## Suggested Index Shape

```markdown
# Ghoti Vault Index

Status: local_markdown_vault / token_saving / not_runtime_wired

## Start Here

- [[01_Current_State]]
- [[02_Next_Actions]]
- [[05_Safety_Gates]]

## Computer Use

- [[04_Tools]]
- Source: ../computer_use_strategy_note.md

## Milestone Logs

- Source: ../ghoti_finish_line_log.md
```

## Comparison With Other Knowledge Tools

### Obsidian Markdown Vault

- Best first step.
- No install required to write/read markdown.
- Works with Git.
- Easy for ChatGPT/Claude/Codex to consume by file path.
- Low risk.

### AnythingLLM

- Strong future local RAG candidate.
- Useful after the markdown vault is clean.
- Requires install and ingestion boundaries.
- Should not import private data without approval.

### Open WebUI

- Strong local Ollama/model UI candidate.
- Good for diagnostics and local model experiments.
- Not a project memory source by itself unless paired with files/RAG.

### LibreChat

- Useful self-hosted multi-provider chat UI.
- More setup and secrets risk than plain markdown.
- Better later, not first.

### Perplexica

- Useful research/search UI candidate.
- More external-search/TOS considerations.
- Not the primary project memory system.

## Recommended Workflow

1. Create plain markdown vault.
2. Seed only 8 compact notes.
3. Add links to source docs and key commits.
4. Update the vault at the end of each milestone.
5. Use the vault as the top context path for new ChatGPT/Codex/Claude sessions.
6. Add RAG later only after the markdown notes are clean and stable.

## What Not To Do

- Do not install Obsidian plugins in this milestone.
- Do not create a giant copied mirror of `14_context`.
- Do not paste logs into notes.
- Do not store secrets.
- Do not treat Obsidian as Ghoti runtime wiring.
- Do not use markdown compaction to remove safety constraints from prompts.

## Verdict

Start with a plain markdown vault first, then evaluate AnythingLLM/Open WebUI/LibreChat/Perplexica later as optional read/search layers.

Recommendation: use soon as `14_context/obsidian_vault/`, markdown-only, not runtime-wired.
