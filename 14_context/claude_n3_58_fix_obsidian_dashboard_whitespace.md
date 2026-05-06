# N+3.58-FIX — Obsidian Probe + Dashboard Stability + Whitespace Clean Pass

## Branch
`feat/ghoti-agent-claude-n3-58-fix-obsidian-dashboard-whitespace`

## Base
`feat/ghoti-agent-claude-n3-58-language-truth-rust-readiness-merge-assistant` @ `8a4a04d`

## Exact Issues Fixed

1. **`obsidian_probe.py` PermissionError crash** — `pathlib.Path.exists()` raises
   `PermissionError` on Windows when the calling process lacks read access to the
   parent directory of a candidate path (e.g. `C:\Users\Navif\AppData\Local\...`
   checked from the `ai_sandbox` process). Added `safe_exists`, `safe_is_file`,
   `safe_glob_md`, `safe_stat`, and `safe_check_candidate` helpers that catch
   `PermissionError`, `OSError`, and `FileNotFoundError`. Every probe path check
   now uses these helpers. Inaccessible paths are reported in
   `app.inaccessible_candidates` and `probe_errors` without crashing.

2. **`ghoti_dashboard.py` crash via Obsidian probe path** — `_probe_obsidian()` was
   called bare in `_collect_status()`. If the subprocess or inline fallback raised,
   the entire dashboard crashed. Wrapped in `try/except Exception`; on failure a
   safe fallback dict is used and `obsidian_probe_error` is populated in the
   status/JSON output.

3. **`ghoti_dashboard_card.md` trailing whitespace** — Python's `Path.write_text()`
   on Windows translates `\n` to `\r\n` (CRLF) by default. git reads the `\r` as
   trailing whitespace, failing `git diff --cached --check`. Fixed by:
   - Adding `_clean_markdown(text)` helper that `rstrip()`s every line and ensures
     a single trailing newline.
   - Applying it in `_render_card()` before returning.
   - Adding `newline="\n"` to `_safe_write_text()` so the file is written with LF.

## Files Changed

| File | Change |
|------|--------|
| `03_scripts/obsidian_probe.py` | Added 5 safe helpers; all path checks hardened; `inaccessible_candidates` + `probe_errors` in JSON output |
| `03_scripts/ghoti_dashboard.py` | Probe wrapped in try/except; `_safe_exists` helper; `_clean_markdown` helper; `newline="\n"` in write; `obsidian_probe_error` in status dict; MILESTONE updated to N+3.58-FIX |
| `14_context/ghoti_dashboard_card.md` | Regenerated with LF line endings and no trailing whitespace |
| `14_context/agent_lanes/active_locks.jsonl` | Lock record appended |
| `14_context/agent_lanes/lane_status.jsonl` | Start + complete status records appended |
| `14_context/claude_n3_58_fix_obsidian_dashboard_whitespace.md` | This doc |
| `14_context/tooling/obsidian_probe_n3_58_fix.md` | Probe hardening details |
| `14_context/tooling/dashboard_whitespace_n3_58_fix.md` | Dashboard stability + whitespace fix details |

## Validation Results

| Check | Result |
|-------|--------|
| AST parse (12 scripts) | PASS |
| `obsidian_probe.py --status` | PASS |
| `obsidian_probe.py --json` | PASS |
| `ghoti_dashboard.py --status` | PASS |
| `ghoti_dashboard.py --json` | PASS |
| `ghoti_dashboard.py --card --dry-run` | PASS |
| `ghoti_dashboard.py --card --apply` | PASS |
| `repo_language_inventory.py --status/--json` | PASS |
| `rust_readiness_probe.py --status/--json` | PASS |
| `ghoti_merge_assistant.py --status/--plan --dry-run` | PASS |
| All safety tools (bridge, course, ruflo, gemma, prompt_bus, router) | PASS |
| `node --check` server.js + app.js | PASS |
| JSON configs (9 files) | PASS |
| `git diff --check` on card (unstaged) | PASS |
| `agent_lane_status.py --check` | PASS (8 locks, 15 statuses) |

## Direct Answers

- **Obsidian probe crashes fixed?** YES — PermissionError now caught and reported.
- **Dashboard status/json/card fixed?** YES — all four modes pass.
- **Dashboard card trailing whitespace fixed?** YES — LF-only output, `rstrip()` on every line.
- **CC/Codex automatic?** NO.
- **Ruflo runtime wired?** NO.
- **Java tracked?** NONE (0 .java files in git ls-files).
- **Rust tracked?** NONE (0 .rs files in git ls-files).
- **Rust rewrite now?** NO.

## Safety Confirmation

- No live actions performed.
- No secrets, .env, tokens, credentials read.
- No Ruflo runtime wiring.
- No CC/Codex automation.
- No global package installs.
- No Rust implementation added.
- No auto-merge into main.
- No force push.
- `cc_codex_bridge.py` remains manual file handoff only.
- `ghoti_merge_assistant.py` remains commands-only.
