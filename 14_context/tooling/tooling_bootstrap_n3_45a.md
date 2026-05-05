# Tooling Bootstrap — N+3.45A

**Milestone:** N+3.45A — Controlled Parallel Pilot, Claude Lane: Tooling Bootstrap + Prompt Bus + Obsidian/Ruflo Local Integration Readiness
**Date:** 2026-05-05
**Branch:** feat/ghoti-agent-claude-n3-45-tooling-prompt-bus

---

## What Was Built

### Obsidian

- **Status:** Installed (Obsidian 1.12.7 via winget)
- **Vault:** `14_context/obsidian_vault/` — 10+ markdown files from N+3.7 and N+3.34
- **Compact memory:** `14_context/compact_memory/` — 6+ compressed pointer files
- **Doc:** `14_context/tooling/obsidian_install_and_vault_link_n3_45a.md`

### Ruflo (claude-flow)

- **Status:** Intake-only — cloned to `21_repos/third_party/evals/ruflo/`
- **Version:** 3.5.80 (commit `01070ede81fa6fbae93d01c347bec1af5d6c17f0`)
- **Package:** `claude-flow` npm, MIT License
- **No runtime wiring** — not connected to Claude/Codex/live accounts
- **Doc:** `14_context/tooling/ruflo_intake_n3_45a.md`

### Prompt Bus

- **Status:** Created
- **Script:** `03_scripts/prompt_bus.py`
- **Directories:** `14_context/prompt_bus/` (inbox, outbox, archive, templates)
- **Templates:** claude_code, codex, chatgpt_handoff
- **Canonical prompt path:** `14_context/ghoti_current_prompt.md`

### Local Worker Router

- **Status:** Created
- **Script:** `03_scripts/local_worker_router.py`
- **Config:** `23_configs/local_worker_routing.example.json`
- **Docs:** `14_context/local_workers/README.md`, `local_worker_policy_n3_45a.md`

### Claude Slash Commands

- **Status:** Created
- **Location:** `.claude/commands/`
- **Commands:** `goal`, `ultraplan`, `ghoti-status`, `prompt-bus`

---

## How to Use

### Obsidian

1. Launch Obsidian
2. Open folder as vault: `C:\Users\ai_sandbox\Documents\AI_Managed_Only\14_context\obsidian_vault`
3. Navigate using `00_Index.md`
4. Use `09_Migration_Handoff.md` as context primer for new sessions

### Prompt Bus

```bash
python 03_scripts/prompt_bus.py --status
python 03_scripts/prompt_bus.py --init
python 03_scripts/prompt_bus.py --write-claude --title "N+3.46" --body "..." --apply
python 03_scripts/prompt_bus.py --write-codex --title "audit" --body "..." --apply
python 03_scripts/prompt_bus.py --list-outbox
```

### Local Worker Router

```bash
python 03_scripts/local_worker_router.py --recommend --task "compress a long markdown handoff"
python 03_scripts/local_worker_router.py --recommend --task "validate JSONL"
python 03_scripts/local_worker_router.py --recommend --task "edit dashboard JavaScript"
```

### Claude Slash Commands

In Claude Code:
```
/goal       — long-horizon Ghoti execution from current prompt
/ultraplan  — deep planning mode
/ghoti-status — repo + lane + prompt bus status
/prompt-bus — prompt bus status and copy-paste guide
```

---

## Validation Commands

```bash
python -c "import ast, pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['03_scripts/prompt_bus.py','03_scripts/local_worker_router.py']]; print('AST OK')"
python 03_scripts/prompt_bus.py --help
python 03_scripts/prompt_bus.py --status
python 03_scripts/local_worker_router.py --help
python 03_scripts/agent_lane_status.py --check
python 03_scripts/agent_lane_status.py --list
```

---

## Safety Gates

- Obsidian: no cloud sync, no plugins, no account
- Ruflo: source-check only, no runtime wiring, no API keys
- Prompt bus: no clipboard default, no live sends, no external calls
- Local worker router: no external APIs, no live actions
- Slash commands: no live actions, no cap bypass

---

## What Is Not Wired Yet

- Ruflo npm dependencies not installed (awaiting explicit approval)
- Ruflo not connected to Claude API or MCP
- Obsidian plugins: none installed
- Prompt bus clipboard support: disabled
- Gemma routing: config set `enabled: false` until Ollama confirmed running
- Local worker router does not call Ollama in this milestone

---

## Next Steps

1. Merge this lane branch after Codex N+3.45B audit
2. Get explicit approval for `npm install --ignore-scripts` in Ruflo eval area
3. Run Codex audit on Ruflo integration surface before any live wiring
4. Enable Gemma routing in `23_configs/local_worker_routing.example.json` when Ollama confirmed
5. Next milestone: N+3.46 — parallel pilot retrospective and Ruflo integration planning
