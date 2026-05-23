# Local Memory Context Pack Guide

## What Context Packs Are

Ghoti context packs are compact repo-local handoff files that summarize the
current project truth for Codex, ChatGPT, Claude, and Obsidian. They are meant
to save tokens and reduce drift by giving each model the same small, truthful
status packet instead of a long thread replay.

Context packs are not autonomy. They do not call providers, configure tokens,
post content, run browser control, or take account actions.

## Generate A Fresh Pack

```powershell
python 03_scripts/ghoti_context_pack_builder.py --write --json
```

Launcher shortcut:

```powershell
python 03_scripts/ghoti_product_launcher.py --context-pack --json
```

Local worker companion:

```powershell
python 03_scripts/ghoti_product_launcher.py --local-worker-status --json
python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json
```

Repo knowledge companion:

```powershell
python 03_scripts/ghoti_product_launcher.py --repo-map --json
python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json
```

Dashboard:

```text
http://127.0.0.1:3210
```

Open the dashboard and read the **Local Memory / Context Pack** card for the
latest path, generated timestamp, compact status paragraph, and copy-paste
prompt path.

## Files Produced

Default output directory:

```text
14_context/compact_memory/generated/
```

Files:

- `ghoti_current_context_pack.md` - compact human-readable project status.
- `ghoti_current_context_pack.json` - machine-readable status payload.
- `ghoti_codex_next_prompt.md` - safe next Codex prompt.
- `ghoti_chatgpt_migration_summary.md` - short ChatGPT migration summary.
- `ghoti_status_short.md` - one compact paragraph for quick handoff.

Local worker companion files live under `14_context/local_worker/generated/`.
See [Local Model / Gemma Setup Guide](LOCAL_MODEL_GEMMA_SETUP_GUIDE.md) and
[Easy Worker Lane Guide](EASY_WORKER_LANE_GUIDE.md).

Repo knowledge companion files live under `14_context/repo_knowledge/generated/`.
Start with `repo_knowledge_map.md`, `latest_reports_index.md`, and the
task-specific bundles. See [Repo Knowledge Map Guide](REPO_KNOWLEDGE_MAP_GUIDE.md).

## How To Use The Pack

For ChatGPT:

Paste `ghoti_status_short.md` or `ghoti_chatgpt_migration_summary.md`, then ask
for planning or reasoning. Keep live account/API/provider setup manual.

For Codex:

Paste `ghoti_codex_next_prompt.md` and the current user goal. Codex should use
repo-contained worktrees under `.claude/worktrees`, add tests first, validate,
push feature branches, and create audit branches when required.

For Claude:

Paste the compact status plus the exact implementation scope. Keep Claude as a
manual implementation lane unless a later audited milestone changes it.

For Obsidian:

The generated Markdown files can be copied or linked into an Obsidian vault.
Ghoti does not require Obsidian to be installed and does not use an Obsidian API.
The repo-local vault pattern is:

```text
14_context/obsidian_vault/
```

## What The Pack Includes

- current main hash
- latest clean milestone
- launcher command
- dashboard URL
- what works now
- what remains pending/manual
- active safety boundaries
- latest repo reports
- Ollama/Gemma/local_demo truth
- repo knowledge map and task bundle paths
- Hermes WSL truth
- Obsidian/local memory truth
- next recommended milestone
- safe copy-paste prompt for Codex
- short ChatGPT migration summary
- compact status paragraph

## What Is Excluded For Safety

- secrets, API keys, provider tokens, cookies, browser sessions, local
  credentials, and human private files
- `.env` contents
- live provider setup
- Telegram setup
- browser automation or desktop click/type
- live account actions, posting, money movement, trading, or legal actions
- external repo runtime wiring
- bot/captcha/cloak bypass, fake engagement, spam, or unauthorized scraping

## Troubleshooting

### The pack has not been generated yet

Run:

```powershell
python 03_scripts/ghoti_context_pack_builder.py --write --json
```

### The dashboard card shows stale status

Use the **Generate Context Pack** button or rerun the CLI command, then refresh
the dashboard card.

### Ollama or Gemma is missing

This is expected in the current local MVP if Gemma has not been pulled. The
context pack should say `local_demo fallback active` instead of pretending a
Gemma worker is running.

### Hermes is not found

Run only safe probes or the repo status script:

```powershell
python 03_scripts/hermes_local_bootstrap.py --status --json
```

Do not run Hermes setup, provider config, Telegram setup, token flows, or live
APIs as part of context pack generation.

### Repo knowledge bundle missing

Run:

```powershell
python 03_scripts/ghoti_repo_knowledge_map.py --write --json
```

Then regenerate the context pack. The repo knowledge lane stays local-only:
Graphify runtime is roadmap only/not wired, no external runtime, and no network.

### Generated residue appears

Context pack files under `14_context/compact_memory/generated/` are intentional
when the milestone is updating the memory pack. Other generated status residue
should be inspected before commit and restored when it is not part of the work.

## Roadmap

Next local memory improvements:

- local repo knowledge map and report index compression
- future Graphify repo knowledge graph integration
- real Gemma model availability and worker-lane diagnostics
- milestone-aware memory summaries
- automatic context pack refresh after clean merge gates
- richer Obsidian vault links while staying file-based and local-first
