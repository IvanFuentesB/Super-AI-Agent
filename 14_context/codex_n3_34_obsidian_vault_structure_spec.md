# Codex N+3.34 Obsidian Vault Structure Spec

Status: codex_planning_only / obsidian_vault_structure / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: b95e577

## Purpose

Specify the local Obsidian-compatible markdown vault that should become Ghoti's durable, human-readable memory layer.

Obsidian/local markdown memory is vital infrastructure, not optional. It reduces repeated prompt context, keeps the project understandable across model limits, and gives Gemma/Ollama safe local documents to compress without replacing source records.

Existing truth: `14_context/obsidian_vault/` already exists with an N+3.7 scaffold (`00_Index.md`, `01_Current_State.md`, `04_Tools.md`, `05_Safety_Gates.md`). N+3.34 should evolve that scaffold later without overwriting user memory.

## Intended Vault Root

```text
14_context/obsidian_vault/
```

The vault must remain plain markdown. Obsidian app/plugins are optional and not required.

## Proposed File Set

```text
14_context/obsidian_vault/
  00_Index.md
  01_Current_State.md
  02_Next_Actions.md
  03_Decisions.md
  04_Tools_And_Repos.md
  05_Money_OS.md
  06_Safety_Gates.md
  07_Agent_Routing.md
  08_Dirty_State.md
  09_Migration_Handoff.md
```

## Canonical Rules

- Vault files summarize and link to durable sources.
- Vault files do not replace `current_state.md`, `next_actions.md`, `ghoti_finish_line_log.md`, milestone docs, logs, schemas, or runtime data.
- Every claim should point to a source file or say `unknown`.
- Gemma may draft updates, but canonical promotion needs human, Claude, or Codex review depending on risk.
- No secrets, API keys, credentials, tokens, 2FA, customer data, or private account instructions belong in the vault.
- No public, money-facing, or live-account action can be authorized by a vault note.

## 00_Index.md

Purpose:

- Map the vault and provide fast entry points.
- Show which notes are canonical, draft, stale, or migration-needed.

Belongs here:

- list of vault notes
- source-of-truth pointers
- update cadence table
- "read this first" instructions for Claude/Codex/ChatGPT

Must not belong here:

- full milestone logs
- raw transcripts
- secrets
- long implementation diffs

Update frequency:

- every memory-structure milestone
- whenever new vault notes are added

Gemma can draft:

- yes, from existing vault file list and source docs

Human review required:

- yes before canonical changes, because index errors misroute future prompts

## 01_Current_State.md

Purpose:

- One-page high-signal snapshot of Ghoti's actual state.

Belongs here:

- current branch and latest known pushed milestone
- major working capabilities
- major not-yet-wired capabilities
- current blockers
- links to `14_context/current_state.md` and latest milestone summary docs

Must not belong here:

- every historical milestone bullet
- speculative roadmap without status labels
- generated model claims without review

Update frequency:

- after major implementation milestones
- after dirty-state resolution

Gemma can draft:

- yes, from `current_state.md`, `next_actions.md`, and recent milestone docs

Human review required:

- yes before canonical promotion, because this is the top-level truth note

## 02_Next_Actions.md

Purpose:

- Compact list of the next safe actions and blocked actions.

Belongs here:

- exact next Claude recommendation
- exact next Codex recommendation
- operator approval gates
- blocked/unblocked state
- file paths for handoff docs

Must not belong here:

- unapproved execution commands that perform live actions
- broad brainstorming backlog
- stale next actions without date/source

Update frequency:

- after each milestone
- before a long context handoff

Gemma can draft:

- yes, from `next_actions.md`, recent Codex recommendation docs, and wait/resume summaries

Human review required:

- yes for any action touching runtime, public, money-facing, or live-account work

## 03_Decisions.md

Purpose:

- Durable decision log with rationale and source links.

Belongs here:

- architectural decisions
- safety decisions
- model-routing decisions
- money workflow boundaries
- "why not" decisions

Must not belong here:

- raw chat opinions without source
- temporary thoughts
- secrets
- unreviewed model output promoted as fact

Update frequency:

- when a decision changes future behavior
- after explicit operator policy changes

Gemma can draft:

- yes, by extracting candidate decisions from docs

Human review required:

- yes before canonical promotion

## 04_Tools_And_Repos.md

Purpose:

- Compact tool/repo truth: installed, cloned, evaluated, planning-only, blocked.

Belongs here:

- Paperclip/OpenClaw/n8n status
- CUA/Docker/Ollama status
- third-party clone status
- "not installed" and "not wired" flags
- source docs and repo paths

Must not belong here:

- third-party source dumps
- install commands without approval context
- leaked/proprietary code notes beyond audit-only warnings

Update frequency:

- after tool audits
- after installs/pulls/clones that were explicitly approved

Gemma can draft:

- yes for summarizing local docs

Human review required:

- yes before marking any tool as installed, runnable, or production-wired

## 05_Money_OS.md

Purpose:

- High-level memory for the ethical money workflow system.

Belongs here:

- numbers-game principle
- current money workflow files
- experiment tracker location
- product/content/distribution lanes
- manual approval rules
- links to money workflow specs

Must not belong here:

- fake revenue
- unverified proof
- private customer data
- live account instructions
- scraping tactics with legal/ToS risk

Update frequency:

- after Money OS implementation milestones
- after manual metrics are recorded

Gemma can draft:

- yes for summarizing local money docs and experiment tracker excerpts

Human review required:

- yes before any public/money-facing claim becomes canonical

## 06_Safety_Gates.md

Purpose:

- Canonical compact safety boundaries.

Belongs here:

- no live actions without approval
- no model-output execution
- no fake proof/testimonials/engagement
- no secrets
- approval phrase boundaries
- dirty-state warnings

Must not belong here:

- instructions for bypassing platform rules
- credential handling details
- hidden automation routes

Update frequency:

- whenever safety policy changes
- before enabling any new action surface

Gemma can draft:

- yes, but only from reviewed safety docs

Human review required:

- always

## 07_Agent_Routing.md

Purpose:

- Compact routing truth for Gemma, Claude Code, Codex, ChatGPT, and future control planes.

Belongs here:

- Gemma handles easy local draft/compression tasks
- Claude Code handles hard implementation
- Codex handles audits/specs
- ChatGPT handles strategy/prompting
- Paperclip/OpenClaw/n8n remain future candidates unless approved

Must not belong here:

- autonomous routing claims that are not implemented
- provider cap bypass language
- live-account execution paths

Update frequency:

- after model/router milestones
- after worker-card policy updates

Gemma can draft:

- yes for low-risk summaries

Human review required:

- yes before any autonomous routing policy becomes canonical

## 08_Dirty_State.md

Purpose:

- Keep the current dirty worktree warning visible and hard to miss.

Belongs here:

- dirty file list
- whether dirty files are Claude partial work, unrelated local dirt, or generated logs
- next safe action
- what not to stage

Must not belong here:

- full diffs
- cleanup commands without approval
- instructions to reset/delete

Update frequency:

- whenever `git status --short` materially changes
- before staging or commit milestones

Gemma can draft:

- yes from `git status` output pasted into a local artifact

Human review required:

- yes before canonical promotion, because incorrect dirty-state memory can cause data loss

## 09_Migration_Handoff.md

Purpose:

- Handoff note for moving between long ChatGPT/Codex/Claude sessions without repasting everything.

Belongs here:

- latest pushed commit
- must-read files for the next agent
- one-screen context summary
- exact next milestone recommendation
- known blockers and dirty files

Must not belong here:

- full source files
- raw logs
- unreviewed model output as canonical truth

Update frequency:

- at the end of major milestones
- before switching agents or losing context

Gemma can draft:

- yes from current vault notes and recent milestone docs

Human review required:

- yes before using as a canonical prompt base for Claude Code

## Implementation Guidance

Future implementation should create missing files only. It must not overwrite existing notes without preserving the prior content.

Recommended safe pattern:

1. create missing target note
2. if note exists, append a dated migration section or create a draft update
3. include source references
4. mark review status
5. require human/Claude/Codex review before canonical promotion

## Verdict

The Obsidian vault should be Ghoti's durable local memory map. It should stay compact enough for humans and models, but never become the only copy of project truth.
