# Codex Screenpipe + Obsidian Token Workflow Review - N+3.6

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: 2e9ffec
Status label: codex_review / screenpipe_obsidian_token_workflow / not_runtime_wired

## Scope

This Codex lane reviewed Screenpipe retention planning and the Obsidian/local markdown vault token-saving workflow. No Screenpipe install, Screenpipe run, screen/audio capture, plugin install, RAG setup, or runtime wiring occurred.

## Screenpipe Truth

| Check | Review |
|---|---|
| Screenpipe capture started | NO |
| Screenpipe installed | not proven by this lane |
| Capture default | disabled/operator-start only per plan |
| Retention days | 3 |
| Cleanup default | dry-run |
| Allowed roots | `output/screenpipe`, `05_logs/screenpipe` |
| Blocked roots | includes `14_context`, `01_projects`, scripts/config/project roots |
| Runtime wired | NO |

## Screenpipe Plan Review

The plan is sound if Screenpipe remains operator-start only and retention-limited.

Good points:

- `enabled=false` in policy.
- `retention_days=3`.
- `dry_run_default=true`.
- Sensitive capture notes explicitly warn against passwords, 2FA, banking, private docs, and live accounts.
- Cleanup script refuses broad/root paths.
- Cleanup script deletes only under configured allowed roots.
- Cleanup script requires `-Execute` to delete files.
- No automatic capture is described.

Watch-outs:

- A cleanup script cannot prevent sensitive capture; it only deletes old files.
- Sensitive-window exclusion must be enforced at future adapter/capture-start layer.
- Capture status must be visible if Screenpipe is ever started.
- Screenshots/audio/transcripts must never be staged.

## Cleanup Script Safety

Reviewed script: `03_scripts/screenpipe_retention_cleanup.ps1`

Observed behavior:

- Dry-run by default.
- `-Execute` required for deletion.
- Allowed roots are limited to:
  - `C:\Users\ai_sandbox\Documents\AI_Managed_Only\output\screenpipe`
  - `C:\Users\ai_sandbox\Documents\AI_Managed_Only\05_logs\screenpipe`
- Blocks dangerous roots including `C:\`, `C:\Users`, `C:\Windows`, `Program Files`, and important repo directories.
- Uses file age cutoff based on retention days.

Verdict: safe enough for dry-run validation. Live deletion should still require explicit operator approval.

## Obsidian / Local Vault Truth

Files reviewed:

- `14_context/obsidian_token_saving_vault_plan.md`
- `14_context/obsidian_vault/00_Index.md`
- `14_context/obsidian_vault/01_Current_State.md`
- `14_context/obsidian_vault/04_Tools.md`
- `14_context/obsidian_vault/05_Safety_Gates.md`

Current state:

- Plain markdown vault exists.
- Notes are compact and link back to source docs.
- No plugin install is needed.
- No vector DB/RAG is needed yet.
- This is legal token/context saving, not provider cap bypass.

## Token Workflow Review

The vault can reduce token use safely because it gives each future session:

- a compact state note
- a compact tools note
- a compact safety gate note
- links to source files instead of pasted logs
- stable paths for handoffs

Recommended usage:

- ChatGPT starts from the vault notes for architecture/planning.
- Claude Code gets one narrow prompt with file paths.
- Codex reads only the relevant vault/source files.
- Finish-line logs remain detailed; vault notes remain compact.

## RAG / Plugin Deferral

Defer:

- Obsidian plugins
- AnythingLLM ingestion
- Open WebUI/RAG wiring
- vector database setup
- cloud sync

Reason:

- The current vault is small.
- Markdown is enough.
- Plugin/RAG install adds complexity and privacy risk before it is needed.

## Final Verdict

Screenpipe: promising, but capture must remain operator-start only with 3-day retention and dry-run cleanup first.

Obsidian/local vault: use now as compact markdown source of truth. No plugin/RAG needed yet.

This is legal token-saving/context management, not provider cap bypass.
