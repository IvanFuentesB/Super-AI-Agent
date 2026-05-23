# Obsidian Compact Memory Plan

Ghoti uses Obsidian-compatible markdown as compact local memory. The goal is to
reduce context cost while keeping every important decision reviewable by the
operator.

## Current Status

- Memory files stay repo-local under `14_context/obsidian_vault/` and
  `14_context/compact_memory/`.
- `03_scripts/obsidian_probe.py` reports vault/app status without changing the
  user's machine.
- `03_scripts/local_memory_compression_bridge.py` can produce local summaries
  and falls back to `local_demo` when Ollama or Gemma is unavailable.
- No cloud sync, provider upload, or automatic desktop action is required.

## MVP Shape

- Keep one current-state note, one next-actions note, and milestone handoff
  notes.
- Summaries must say whether they were created by local fallback or a local
  model probe.
- Long repo context should become short source-intelligence packets before it
  is handed to premium model lanes.
- Any memory write that affects operator decisions should be visible in the
  dashboard or final report.

## Safety Gates

- No secrets, tokens, cookies, or browser sessions in memory notes.
- No captured account images or private documents in public-ready memory files.
- No automatic posting or live account action from memory content.
- Human review is required before a compact note becomes canonical project
  truth.
