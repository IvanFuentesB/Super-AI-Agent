# Codex N+3.48 - Roadmap To 80 Percent

Milestone: N+3.48 - Post-Merge Audit + 80 Percent Roadmap Lock

Date: 2026-05-06

## Roadmap Principle

Do not chase Ruflo/OpenClaw/Paperclip/n8n/CUA yet. Ghoti gets to 80% faster by making the local rails useful:

1. Prompt bus becomes an actual operator workbench.
2. Lane locks and status become visible and script-updated.
3. Context packs become generated artifacts.
4. Gemma compression becomes a draft-producing local workflow.
5. Obsidian/compact memory becomes refreshable without data loss.
6. Merge readiness becomes script-checkable.

## N+3.49 - Prompt Bus Dashboard + Context Pack Generator + Lane Status Beacon Helper

Goal: reduce copy-paste and make the current agent system visible.

Recommended Claude scope:

- Add a read-only dashboard route/card for prompt bus, lane locks, and local workers.
- Add a local `03_scripts/prompt_context_pack.py` helper.
- Add a local status/beacon helper extension or small helper that can append safe lane status records.
- Generate context pack artifacts under `05_logs/prompt_context_packs/<run_id>/`.
- Keep all writes dry-run by default and `--apply` gated.
- Do not connect external tools.
- Do not run live accounts or browser/operator tools.

Minimum artifacts:

- `context_pack.md`
- `context_pack.json`
- `claude_prompt.md`
- `codex_prompt.md`
- `chatgpt_handoff.md`
- `run_summary.json`

Dashboard card should show:

- canonical Claude prompt path
- outbox count
- latest prompt artifacts
- active lane locks
- latest lane statuses
- local worker routing config
- warnings for stale locks or missing status
- next manual action

Expected project percentage after N+3.49: **74%**.

## N+3.50 - Gemma Compression + Obsidian Compact Memory Refresh

Goal: make token saving real, not only recommended.

Recommended Claude scope:

- Add a local Gemma/Ollama compression task wrapper that writes draft artifacts only.
- Add `--dry-run` and `--apply`; default to dry-run.
- Output to `05_logs/compact_memory_drafts/<run_id>/`.
- Never overwrite canonical compact memory automatically.
- Add a safe promotion checklist for human/Codex/Claude review.
- Add an Obsidian/compact memory refresh helper that previews source-to-target changes.

Minimum artifacts:

- `draft_project_state.md`
- `draft_agent_routing_memory.md`
- `draft_safety_rules.md`
- `source_map.json`
- `promotion_checklist.md`
- `run_summary.json`

Expected project percentage after N+3.50: **80-83%**.

## N+3.51 - Merge Assistant And Parallel Lane Retrospective

Goal: make controlled parallel work less fragile.

Recommended Claude scope:

- Add `03_scripts/merge_readiness_check.py`.
- Check branch HEAD vs origin.
- Check changed files per lane.
- Check active locks and shared file overlap.
- Check untracked/generated logs.
- Check required validations.
- Print exact merge order and stop conditions.
- No automatic merge by default.

Expected project percentage after N+3.51: **83-86%**.

## N+3.52 - Safe Deterministic Automation Runner

Goal: route boring deterministic work to Python without model calls.

Recommended Claude scope:

- Add a stdlib-only runner for allowed local tasks:
  - JSONL validation
  - markdown report assembly
  - prompt outbox report
  - lane status report
  - money workflow counts
  - Obsidian file existence checks
- Use allowlisted commands only.
- No shell command passthrough.
- No external APIs.
- No account actions.

Expected project percentage after N+3.52: **86-88%**.

## N+3.53+ - External Tool Evaluation Gates

Only after the local operator rails are stable:

- Ruflo isolated dependency/source audit.
- OpenClaw/Paperclip/n8n comparison in isolated folders.
- Browser/operator sandbox plan for CUA/Chrome DevTools MCP/Firecrawl/Glif.
- Connector account inventory and secret handling.
- No live actions until every safety gate passes.

## What Not To Do Next

- Do not wire Ruflo directly into Claude Code.
- Do not run OpenClaw/Paperclip/n8n workflows.
- Do not connect browser tools to real accounts.
- Do not add automatic posting/email/payment/scraping.
- Do not make Gemma canonical truth.
- Do not let dashboard buttons mutate state before a separate approval-gated mutation milestone.

## 80 Percent Lock

The fastest safe path to 80% is:

1. N+3.49 prompt bus/context pack/dashboard/beacons.
2. N+3.50 Gemma compression plus Obsidian compact memory refresh.
3. N+3.51 merge readiness assistant.

External orchestrators come after that, not before.
