# N+3.7 Codex Obsidian Vault Review

Status: vault_review / plain_markdown / token_saving / not_runtime_wired

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack

## Current Vault Truth

The Obsidian-style vault exists under:

```text
14_context/obsidian_vault/
```

Known current notes from prior planning:

- `00_Index.md`
- `01_Current_State.md`
- `04_Tools.md`
- `05_Safety_Gates.md`

This vault is plain markdown. It does not require the Obsidian app, plugins, RAG, a vector database, or external services.

## What The Vault Is For

- Keep project state compact.
- Reduce repeated prompt context.
- Give ChatGPT, Codex, and Claude Code path-based references instead of pasted logs.
- Preserve safety gates and current truth labels.
- Support fresh-session handoffs without giant context dumps.

This is legal context management and token saving. It is not provider cap bypass, quota evasion, account abuse, or a way to defeat model limits.

## Notes To Update Each Milestone

Minimum useful update set:

- `00_Index.md`: keep links and note purpose current.
- `01_Current_State.md`: compact current project truth.
- `04_Tools.md`: installed/reference/tool status.
- `05_Safety_Gates.md`: non-negotiable boundaries.

Suggested later additions:

- `02_Next_Actions.md`
- `03_Runtime_Map.md`
- `06_Prompt_Handoff_Rules.md`
- `07_External_Repos.md`
- `08_Wait_Resume.md`

## Operating Rules

- Keep each note compact, ideally 200-400 words.
- Link to source files by path instead of pasting long excerpts.
- Do not paste large logs.
- Update after each meaningful milestone.
- Mark scaffold/runtime truth explicitly.
- Keep forbidden items visible.
- Do not install Obsidian plugins yet.
- Defer RAG/vector DB until markdown notes become too large to manage.

## Prompt Usage Rule

Future ChatGPT, Codex, and Claude prompts should reference vault files by path and ask the model to read only the relevant note. They should not paste the whole finish-line log or long historical threads unless absolutely necessary.

## Verdict

The vault is ready for token-saving use as plain markdown. The next useful step is a small vault sync/update workflow, not RAG and not plugin installation.
