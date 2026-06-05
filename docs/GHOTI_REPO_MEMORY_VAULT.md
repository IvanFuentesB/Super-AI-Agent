# Ghoti Repo Memory Vault

The Repo Memory Vault is a small, durable, token-efficient memory area committed to the
repo at `14_context/memory_vault/`. It exists so the main working memory only needs to
hold a short *reminder*, while the *details* live as human-readable Markdown.

## Why

Working memory and status files should stay small. Long lists and detailed notes bloat
them and cost tokens to carry around. The vault moves the details into committed
Markdown that is durable, diff-able, and easy to read.

## Design

- **Reminder vs details.** The reminder ("go to the store") stays in the main memory;
  the details (the item list) live in `lists/` as a Markdown checklist.
- **Markdown for humans, JSON for scripts.** Notes, lists, and preferences are
  Markdown. JSON is used only for script-readable indexes/schemas (for example the tool
  intake inventory JSON under `14_context/tool_intake/`).
- **Categories plus index.** Four category folders (`lists/`, `preferences/`,
  `tool_backlog/`, `project_notes/`) plus `templates/`, and a top-level `INDEX.md`.
- **Single-purpose files.** Each file is short and links instead of duplicating.

## Safety

No secrets, tokens, API keys, passwords, health/medical details, addresses, private
account data, or other sensitive personal data may be committed to the vault. It holds
only non-sensitive durable details. Sensitive data stays outside the repo.

## How it is used

1. Keep the short reminder in the main memory.
2. Copy a template into the right category folder and fill in the details.
3. Add a one-line pointer in `INDEX.md`.

## Relationship to other memory

The vault complements (does not replace) the existing compact-memory snapshots, the
status brain/bridge, and the agent handoff vault. Those track project status and
handoffs; the memory vault holds durable, non-sensitive *detail lists* that would
otherwise bloat them.
