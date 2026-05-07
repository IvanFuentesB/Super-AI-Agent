# N+3.56-FIX — Bridge Ruflo Gemma Clean Pass

**Branch**: `feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass`
**Base**: N+3.51 commit `1a2c6fd`
**Goal**: Turn Codex N+3.56 CONDITIONAL PASS into clean PASS.

## What Was Done

### 1. course_certificate_assistant.py — `--goal` support added
- Added optional `--goal` argument to `--plan` mode.
- Goal appears in generated plan output as a personal learning objective.
- Policy explicitly states goal does not imply fake certification or assessment submission.
- All existing safety rules preserved: no fake certs, no cheating, no assessment submission, human does all assessments.
- `--policy` updated to document `--goal`.

### 2. cc_codex_bridge.py — `--init` mode + truth labels
- Added `--init` mode with `--dry-run` and `--apply`.
- `--init --dry-run` prints dirs it would create, writes nothing.
- `--init --apply` creates `14_context/bridge/`, `inbox/`, `outbox/`, `archive/`, `status/`.
- `--status` remains read-only; it reports missing dirs but does not create them.
- `_print_truth_labels()` helper added; called in all command outputs.
- Truth labels in every command: `CC/Codex automatic: NO`, `Bridge type: local manual file handoff`, `Clipboard: NO`, `API calls: NO`, `Auto-send: NO`, `Human copy-paste required: YES`.

### 3. obsidian_probe.py — new unified detection module
- Created `03_scripts/obsidian_probe.py` as single source of truth for Obsidian status.
- Checks vault path, required files (00_Index, 01_Current_State, 02_Next_Actions, 09_Migration_Handoff).
- Checks all executable candidates including Navif, ai_sandbox, Program Files paths.
- Checks winget if available.
- `--status` (human-readable) and `--json` (machine-readable) modes.
- `open_obsidian_vault.ps1` updated to call `obsidian_probe.py` when available.
- `ghoti_dashboard.py` updated to use `obsidian_probe.py` via subprocess `--json`.

### 4. ruflo_install_gate.py — `--source-status` + truthful clean-checkout messaging
- Added `--source-status` mode with status codes:
  - `SOURCE_PRESENT` — source exists and package.json found
  - `SOURCE_MISSING_BOOTSTRAPPABLE` — source absent but ruflo_source.example.json exists
  - `SOURCE_MISSING_NO_CONFIG` — source absent, no config (expected in clean checkout)
  - `PACKAGE_LOCK_PRESENT/MISSING`, `NPM_PRESENT/MISSING`, `NODE_MODULES_INSTALLED/MISSING`, `RUNTIME_WIRING_NO`
- Source missing is NOT called unsafe; truthful message says it must be bootstrapped.
- If source present and `--apply`, writes/updates `23_configs/ruflo_source.example.json` with detected remote URL.
- All existing modes (`--status`, `--install`, `--smoke`, `--report`, `--catalog`) preserved.

### 5. local_worker_router.py — bridge handoff routing fixed
- Added `cc_codex_bridge_worker` rule at highest priority (before generic codex_audit).
- Bridge handoff tasks now route to `cc_codex_bridge.py`, not to generic Codex.
- Keywords: `bridge handoff`, `cc codex bridge`, `codex bridge`, `create bridge`, `write handoff`, etc.
- Route description: "CC/Codex automatic = NO. Local file bridge only."

### 6. prompt_bus.py — overwrite protection verified
- `--allow-canonical-overwrite` is already required to overwrite `14_context/ghoti_current_prompt.md`.
- No changes needed; protection is confirmed in place.

### 7. ghoti_dashboard.py — N+3.56-FIX truth update
- MILESTONE updated to `N+3.56-FIX`.
- `--json` now includes: `bridge_status` with all 6 truth labels, `ruflo.source_status`, `course_helper.goal_supported`, `obsidian_app.probe_available`.
- `--card` renders bridge truth labels explicitly.
- `_probe_obsidian()` uses `obsidian_probe.py` via subprocess; inline fallback if probe absent.
- `GET /api/ghoti/local-orchestrator/status` remains read-only (no changes to server.js needed).

### 8. gemma_compact_memory_worker.py — explicit status fields
- `--status` now shows: Ollama found YES/NO, Ollama version, Gemma model found YES/NO, selected model, safe write fallback.
- Output markers `DRAFT_ONLY | NOT_CANONICAL | HUMAN_REVIEW_REQUIRED` listed in status.

## What Passed (validated commands)
See Step 14 in `ghoti_current_prompt.md` for full validation suite.

## What Remains Manual
- Ruflo source must be manually bootstrapped/cloned if absent.
- CC/Codex handoff requires human copy-paste.
- Gemma compression output requires human review before canonical promotion.
- Obsidian app launch requires explicit `-Open` flag.

## What Is NOT Automatic
- CC/Codex: NO automatic control.
- Ruflo: NOT wired to runtime.
- Gemma: draft only, no canonical writes.
- Obsidian: no auto-launch.

## Safety
- No live actions. No secrets. No global npm install. No Ruflo runtime launch.
- All approvals required from human.
