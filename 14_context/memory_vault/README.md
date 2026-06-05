# Repo Memory Vault (v1)

A token-efficient, durable place in the repo for the *details* behind a reminder - so
the main working memory only has to hold the short reminder, not the whole list.

## Principle

- **Main memory keeps the reminder.** Example: remember "go to the store".
- **The vault keeps the details.** The store item list lives here as a Markdown
  checklist (for example `lists/groceries.md`), and the reminder just points at it.
- This keeps conversations and status files small while the details stay durable and
  human-readable.

## Format rules

- **Markdown** for anything a human reads (notes, checklists, lists, preferences).
- **JSON** only for script-readable indexes/schemas.
- Keep each file short and single-purpose; link instead of duplicating.

## Categories

| Folder | What goes here |
|--------|----------------|
| `lists/` | Checklists and durable lists (groceries, packing, errands, backlog checklists). |
| `preferences/` | Stable preferences and defaults (tone, formatting, workflow choices). |
| `tool_backlog/` | Short durable notes about tools/repos to evaluate (full details live in `14_context/tool_intake/`). |
| `project_notes/` | Durable project notes that are too detailed for the status files. |
| `templates/` | Copy-me templates (`checklist.md`, `tool_note.md`). |

## What must never go in committed memory

No secrets, tokens, API keys, passwords, health/medical details, home/street
addresses, private account data, financial account numbers, or other sensitive
personal data. The vault is for non-sensitive, durable details only. Anything
sensitive stays outside the repo.

## How to use

1. Add the short reminder wherever the main memory lives.
2. Put the details in the right category folder as a Markdown file (copy a template).
3. Add a one-line pointer in `INDEX.md`.
