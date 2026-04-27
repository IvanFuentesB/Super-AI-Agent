# Obsidian / Local Vault Token-Saving Plan

**Status label:** `vault_plan / local_markdown / not_runtime_wired`

---

## Goal

Replace large context re-pastes in prompts with compact, linked markdown notes. Prompts reference a 200-word summary + file path instead of copying hundreds of lines of context. This reduces token usage per session and keeps expensive model calls focused on actual decisions rather than restating known state.

---

## Proposed Vault Location

```
14_context/obsidian_vault/
```

Compatible with Obsidian (open the vault folder as an Obsidian vault). No plugin install required in this milestone.

---

## Proposed Structure

| File | Purpose |
|------|---------|
| `00_Index.md` | MOC — links to all other notes |
| `01_Current_State.md` | One-page snapshot of where Ghoti is right now |
| `02_Next_Actions.md` | Compact next-step list (not the full next_actions.md) |
| `03_Agents.md` | Agent roles, status, and wiring truth |
| `04_Tools.md` | External tool candidates and evaluation status |
| `05_Safety_Gates.md` | Active approval gates and safety rules |
| `06_Prompts.md` | Canonical prompt patterns (compact references) |
| `07_Runbooks.md` | Step-by-step operator runbooks |
| `08_Decisions.md` | Key decisions and rationale |

---

## Token-Saving Rules

1. One page per concept — max 200–400 words per note unless the topic genuinely requires more.
2. Backlink to the original source file instead of pasting content (e.g., `see [[14_context/current_state.md]]`).
3. Never paste raw logs or full file dumps into a prompt — cite the file path and line range.
4. Use compact summaries: one bullet per milestone outcome, not a paragraph per action.
5. ChatGPT writes architecture / task definitions; Claude/Codex execute narrow prompts referencing vault notes.
6. Each new milestone adds or updates one vault note, not a new giant context file.

---

## Suggested Tags

```
#ghoti #safety #adapter #agent #tool #prompt #decision #runbook
```

---

## Optional Future Extensions

- Sync vault with AnythingLLM or Open WebUI for RAG-assisted prompt retrieval.
- Generate a `01_Current_State.md` auto-update script that pulls key fields from `current_state.md` and `wait_resume_items.json`.
- Add daily compact state cron (operator-approved) that summarizes recent task history into the vault.
- Use tags to drive selective context injection in future multi-agent handoffs.

---

## No Plugin Install in This Milestone

Obsidian application and plugins are not installed. The vault is plain markdown, readable without Obsidian. If the operator installs Obsidian later, the folder can be opened directly.
