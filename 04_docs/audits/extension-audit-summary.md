# Extension Audit Summary

Last updated: 2026-04-05

## What was actually found

- VS Code is installed.
- No user-installed VS Code extensions were found under `C:\Users\ai_sandbox\.vscode\extensions`.
- No user-installed Cursor extensions were found under `C:\Users\ai_sandbox\.cursor\extensions`.
- Cursor is not installed for `ai_sandbox`.
- VS Code ships with bundled built-in extensions, but those are not the migration target and are not the interesting part of this audit.
- Re-scan on 2026-04-05 did not change that result.

## Current classification

### Keep

- None yet. There are no user-installed extensions in this sandbox account.

### Probably useful later

- Continue
  - Best first editor-side bridge for local models and cloud fallbacks.
- Python
  - Needed once Python is repaired.
- Ruff
  - Fast Python lint/format workflow.
- rust-analyzer
  - Worth installing only if Rust becomes active in this sandbox.
- Even Better TOML
  - Useful because this stack will use TOML for configs and automations.
- GitLens
  - Helpful once GitHub and repo-heavy work start.
- GitHub Actions
  - Useful later for workflow review, not needed today.
- Markdown All in One
  - Practical because a lot of the planning and ops docs will live in markdown.
- Rust Analyzer
  - Recommended later if and when Rust becomes active.
- Microsoft C/C++
  - Recommended later for Windows C++ work and also the official debugging path mentioned by the VS Code Rust docs for Rust on Windows.
- Even Better TOML
  - Useful later for Cargo, automation, and config files.

### Probably unnecessary right now

- Large theme/icon packs
- Kubernetes extensions
- Docker extensions before Docker exists
- Jupyter-heavy extensions before notebook work exists
- Remote SSH / remote containers before that workflow is real
- Overlapping AI assistants that duplicate Codex/Continue/Aider roles

### Unknown or needs review later

- Any extension set imported from the `Navif` account
- Any extension recommended by external repos but not yet proven useful here

## Recommendation

Do not install a pile of extensions yet.

First clean path later:

1. Repair Python and editor CLI basics.
2. Install only the minimum editor extensions for the active languages and workflows.
3. Add extras only after a repo or task actually requires them.
